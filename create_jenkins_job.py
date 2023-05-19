#!/usr/bin/env python3

# Copyright 2015 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import collections
import copy
import os
import re
import sys

try:
    import ros_buildfarm  # noqa
except ImportError:
    sys.exit("Could not import ros_buildfarm, please add it to the PYTHONPATH.")

try:
    import jenkinsapi  # noqa
except ImportError:
    sys.exit("Could not import jenkinsapi, please install it with pip or apt-get.")

from ros_buildfarm.jenkins import configure_job
from ros_buildfarm.jenkins import connect
from ros_buildfarm.templates import expand_template
try:
    from ros_buildfarm.templates import template_prefix_path
except ImportError:
    sys.exit("Could not import symbol from ros_buildfarm, please update ros_buildfarm.")

DEFAULT_REPOS_URL = 'https://raw.githubusercontent.com/ros2/ros2/rolling/ros2.repos'
DEFAULT_MAIL_RECIPIENTS = 'ros2-buildfarm@googlegroups.com'
PERIODIC_JOB_SPEC = '0 4 * * *'

template_prefix_path[:] = \
    [os.path.join(os.path.abspath(os.path.dirname(__file__)), 'job_templates')]


def retention_data_by_job_type(job_name):
    build_discard = None
    if job_name.startswith('test_'):
        build_discard = {'days_to_keep': 300, 'num_to_keep': 10}
    elif job_name.startswith('ci_packaging'):
        build_discard = {'days_to_keep': 300, 'num_to_keep': 30}
    elif job_name.startswith('ci_'):
        build_discard = {'days_to_keep': 732, 'num_to_keep': 500}
    elif job_name.startswith('packaging_'):
        build_discard = {'days_to_keep': 732, 'num_to_keep': 200}
    elif job_name.startswith('nightly_'):
        build_discard = {'days_to_keep': 732, 'num_to_keep': 732}
    else:
        raise f'Please set a retention level for {job_name}'
    return {'build_discard': build_discard}


def nonnegative_int(inval):
    try:
        ret = int(inval)
    except ValueError:
        ret = -1
    if ret < 0:
        raise argparse.ArgumentTypeError('Value must be nonnegative integer')
    return ret


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Creates the ros2 jobs on Jenkins")
    parser.add_argument(
        '--jenkins-url', '-u', default='https://ci.ros2.org',
        help="Url of the jenkins server to which the job should be added")
    parser.add_argument(
        '--ci-scripts-repository', default='git@github.com:ros2/ci.git',
        help="repository from which ci scripts should be cloned"
    )
    parser.add_argument(
        '--ci-scripts-default-branch', default='master',
        help="default branch of the ci repository to get ci scripts from (this is a job parameter)"
    )
    parser.add_argument(
        '--commit', action='store_true',
        help='Actually modify the Jenkins jobs instead of only doing a dry run',
    )
    parser.add_argument(
        '--select-jobs-regexp', default='',
        help='Limit the job creation to those that match the given regular expression'
    )
    parser.add_argument(
        '--context-lines', type=nonnegative_int, default=0,
        help='Set the number of diff context lines when showing differences between old and new jobs'
    )
    args = parser.parse_args(argv)

    data = {
        'ci_scripts_repository': args.ci_scripts_repository,
        'ci_scripts_default_branch': args.ci_scripts_default_branch,
        'default_repos_url': DEFAULT_REPOS_URL,
        'supplemental_repos_url': '',
        'time_trigger_spec': '',
        'mailer_recipients': '',
        'ignore_rmw_default': {
            'rmw_connext_dynamic_cpp',
            'rmw_fastrtps_dynamic_cpp'},
        'use_connext_debs_default': 'false',
        'use_isolated_default': 'true',
        'colcon_mixin_url': 'https://raw.githubusercontent.com/colcon/colcon-mixin-repository/master/index.yaml',
        'build_args_default': '--event-handlers console_cohesion+ console_package_list+ --cmake-args -DINSTALL_EXAMPLES=OFF -DSECURITY=ON -DAPPEND_PROJECT_NAME_TO_INCLUDEDIR=ON',
        'test_args_default': '--event-handlers console_direct+ --executor sequential --retest-until-pass 2 --ctest-args -LE xfail --pytest-args -m "not xfail"',
        'compile_with_clang_default': 'false',
        'enable_coverage_default': 'false',
        'dont_notify_every_unstable_build': 'false',
        'build_timeout_mins': 0,
        'ubuntu_distro': 'jammy',
        'el_release': '9.1',
        'ros_distro': 'rolling',
    }

    jenkins = connect(args.jenkins_url)

    os_configs = {
        'linux': {
            'label_expression': 'linux',
            'shell_type': 'Shell',
        },
        'osx': {
            'disabled': True,
            'label_expression': 'macos',
            'shell_type': 'Shell',
            # the current OS X agent can't handle  git@github urls
            'ci_scripts_repository': args.ci_scripts_repository.replace(
                'git@github.com:', 'https://github.com/'),
        },
        'windows-metal': {
            'label_expression': 'windows',
            'shell_type': 'BatchFile',
            'use_isolated_default': 'false',
        },
        'windows': {
            'label_expression': 'windows-container',
            'shell_type': 'BatchFile',
            'use_isolated_default': 'false',
        },
        'linux-aarch64': {
            'label_expression': 'linux_aarch64',
            'shell_type': 'Shell',
            'ignore_rmw_default': data['ignore_rmw_default'] | {'rmw_connext_cpp', 'rmw_connext_dynamic_cpp', 'rmw_connextdds'},
        },
        'linux-rhel': {
            'label_expression': 'linux',
            'shell_type': 'Shell',
            'build_args_default': '--packages-skip-by-dep ros1_bridge --packages-skip ros1_bridge ' + data['build_args_default'],
            'test_args_default': '--packages-skip-by-dep ros1_bridge --packages-skip ros1_bridge ' + re.sub(
                r'(--ctest-args +-LE +)"?([^ "]+)"?', r'\1"(cppcheck|\2)"', data['test_args_default']),
        },
    }

    os_config_overrides = {
        'linux-rhel': {
            'mixed_overlay_pkgs': '',
            'use_connext_debs_default': 'false',
        },
    }

    launcher_exclude = {
        'linux-rhel',
        'osx',
        'windows-metal',
    }

    jenkins_kwargs = {}
    jenkins_kwargs['context_lines'] = args.context_lines
    if not args.commit:
        jenkins_kwargs['dry_run'] = True
    pattern_select_jobs_regexp = ''
    if args.select_jobs_regexp:
        pattern_select_jobs_regexp = re.compile(args.select_jobs_regexp)

    def create_job(os_name, job_name, template_file, additional_dict):
        if pattern_select_jobs_regexp and not pattern_select_jobs_regexp.match(job_name):
            return
        job_data = dict(data)
        job_data['os_name'] = os_name
        job_data.update(os_configs[os_name])
        job_data.update(additional_dict)
        job_data.update(os_config_overrides.get(os_name, {}))
        job_data.update(retention_data_by_job_type(job_name))
        job_config = expand_template(template_file, job_data)
        configure_job(jenkins, job_name, job_config, **jenkins_kwargs)

    # configure os specific jobs
    for os_name in sorted(os_configs.keys()):
        # This short name is preserved for historic reasons, but long-paths have been enabled on
        # windows containers and their hosts
        job_os_name = os_name
        if os_name == 'windows':
            job_os_name = 'win'

        # configure manual triggered job
        create_job(os_name, 'ci_' + os_name, 'ci_job.xml.em', {
            'cmake_build_type': 'None',
        })
        # configure test jobs for experimenting with job config changes
        # Keep parameters the same as the manual triggered job above.
        create_job(os_name, 'test_ci_' + os_name, 'ci_job.xml.em', {
            'cmake_build_type': 'None',
        })

        if os_name == 'windows-metal':
            # Don't create nightlies or packaging jobs for bare-metal Windows
            continue

        packaging_label_expression = os_configs[os_name]['label_expression']
        if os_name == 'osx':
            packaging_label_expression = 'macos &amp;&amp; mojave'

        # configure a manual version of the packaging job
        ignore_rmw_default_packaging = set()
        if os_name in ['linux-aarch64']:
            ignore_rmw_default_packaging |= {'rmw_connext_cpp', 'rmw_connext_dynamic_cpp', 'rmw_connextdds'}
        create_job(os_name, 'ci_packaging_' + os_name, 'packaging_job.xml.em', {
            'cmake_build_type': 'RelWithDebInfo',
            'label_expression': packaging_label_expression,
            'mixed_overlay_pkgs': 'ros1_bridge',
            'ignore_rmw_default': ignore_rmw_default_packaging,
            'use_connext_debs_default': 'true',
        })
        # configure manual test packaging job 
        create_job(os_name, 'test_packaging_' + os_name, 'packaging_job.xml.em', {
            'cmake_build_type': 'RelWithDebInfo',
            'label_expression': packaging_label_expression,
            'mixed_overlay_pkgs': 'ros1_bridge',
            'ignore_rmw_default': ignore_rmw_default_packaging,
            'use_connext_debs_default': 'true',
        })

        # configure packaging job
        create_job(os_name, 'packaging_' + os_name, 'packaging_job.xml.em', {
            'cmake_build_type': 'RelWithDebInfo',
            'disabled': False,
            'label_expression': packaging_label_expression,
            'mixed_overlay_pkgs': 'ros1_bridge',
            'time_trigger_spec': PERIODIC_JOB_SPEC,
            'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
            'ignore_rmw_default': ignore_rmw_default_packaging,
            'use_connext_debs_default': 'true',
        })

        # create a nightly Debug packaging job on Windows
        if os_name == 'windows':
            create_job(os_name, 'packaging_' + os_name + '_debug', 'packaging_job.xml.em', {
                'cmake_build_type': 'Debug',
                'mixed_overlay_pkgs': 'ros1_bridge',
                'time_trigger_spec': PERIODIC_JOB_SPEC,
                'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
                'ignore_rmw_default': ignore_rmw_default_packaging,
                'use_connext_debs_default': 'true',
            })

        # configure nightly triggered job
        job_name = 'nightly_' + job_os_name + '_debug'
        debug_config = {
            'cmake_build_type': 'Debug',
            'time_trigger_spec': PERIODIC_JOB_SPEC,
            'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
        }
        if os_name == 'windows':
            job_name = job_name[:15]
        if os_name == 'linux':
            # Temporarily pin the debug jobs to larger instances.
            # https://github.com/ros2/ci/issues/702
            debug_config['label_expression'] = 'linux &amp;&amp; 2xlarge'
        create_job(os_name, job_name, 'ci_job.xml.em', debug_config)

        # configure nightly job for testing with address sanitizer on linux
        if os_name == 'linux':
            asan_build_args = data['build_args_default'].replace('--cmake-args',
                '--cmake-args -DOSRF_TESTING_TOOLS_CPP_DISABLE_MEMORY_TOOLS=ON') + \
                ' --mixin asan-gcc --packages-up-to rcpputils'

            create_job(os_name, 'nightly_{}_address_sanitizer'.format(os_name), 'ci_job.xml.em', {
                'cmake_build_type': 'Debug',
                'time_trigger_spec': PERIODIC_JOB_SPEC,
                'mailer_recipients': DEFAULT_MAIL_RECIPIENTS + ' ros-contributions@amazon.com',
                'build_args_default': asan_build_args,
                'test_args_default': data['test_args_default'] + ' --packages-up-to rcpputils',
            })

        # configure jobs for compiling with clang+libcxx on linux
        if os_name == 'linux':
            # Set the logging implementation to noop because log4cxx will not link properly when using libcxx.
            clang_libcxx_build_args = data['build_args_default'] + ' --mixin clang-libcxx --packages-skip intra_process_demo'
            # Only running tests from the lowest-level C package to ensure "working" binaries are generated.
            # We do not want to test more than this as we observe issues with the clang libcxx standard library
            # we don't plan to tackle for now. The important part of the jobs is to make sure the code compiles
            # without emitting thread-safety related warnings.
            clang_libcxx_test_args = data['test_args_default'].replace(' --retest-until-pass 2', '') + ' --packages-select rcutils'
            # nightly job
            create_job(os_name, 'nightly_' + os_name + '_clang_libcxx', 'ci_job.xml.em', {
                'cmake_build_type': 'Debug',
                'compile_with_clang_default': 'true',
                'time_trigger_spec': PERIODIC_JOB_SPEC,
                'mailer_recipients': DEFAULT_MAIL_RECIPIENTS + ' ros-contributions@amazon.com',
                'build_args_default': clang_libcxx_build_args,
                'test_args_default': clang_libcxx_test_args,
            })
            # manually triggered job
            create_job(os_name, 'ci_' + os_name + '_clang_libcxx', 'ci_job.xml.em', {
                'cmake_build_type': 'None',
                'compile_with_clang_default': 'true',
                'build_args_default': clang_libcxx_build_args,
                'test_args_default': clang_libcxx_test_args,
            })

        # configure nightly job for testing rmw/rcl based packages with thread sanitizer on linux
        if os_name == 'linux':
            tsan_build_args = data['build_args_default'].replace('--cmake-args',
                '--cmake-args -DOSRF_TESTING_TOOLS_CPP_DISABLE_MEMORY_TOOLS=ON') + \
                ' --mixin tsan --packages-up-to rcpputils rcutils'

            create_job(os_name, 'nightly_' + os_name + '_thread_sanitizer', 'ci_job.xml.em', {
                'cmake_build_type': 'Debug',
                'time_trigger_spec': PERIODIC_JOB_SPEC,
                'mailer_recipients': DEFAULT_MAIL_RECIPIENTS + ' ros-contributions@amazon.com',
                'build_args_default': tsan_build_args,
                'test_args_default': data['test_args_default'] + ' --packages-select rcpputils rcutils',
            })

        # configure a manually triggered version of the coverage job

        # Proposed list of packages to maximize coverage while testing quality level
        # packages. The list is composed by the list of qualitly level packages plus
        # packages of ros2.repos that are used by the quality level packages during
        # tests.

        # out of the list since ignored by colcon: shape_msgs, stereo_msgs,
        # rmw_connext, rmw_connextdds, rmw_cyclonedds.
        quality_level_pkgs = [
            'action_msgs',
            'ament_index_cpp',
            'builtin_interfaces',
            'class_loader',
            'composition_interfaces',
            'console_bridge_vendor',
            'diagnostic_msgs',
            'fastcdr',
            'fastrtps',
            'foonathan_memory_vendor',
            'geometry_msgs',
            'libstatistics_collector',
            'libyaml_vendor',
            'lifecycle_msgs',
            'nav_msgs',
            'rcl',
            'rcl_action',
            'rcl_interfaces',
            'rcl_lifecycle',
            'rcl_logging_spdlog',
            'rcl_yaml_param_parser',
            'rclcpp',
            'rclcpp_action',
            'rclcpp_components',
            'rclcpp_lifecycle',
            'rcpputils',
            'rcutils',
            'rmw',
            'rmw_dds_common',
            'rmw_fastrtps_cpp',
            'rmw_fastrtps_shared_cpp',
            'rmw_implementation',
            'rosgraph_msgs',
            'rosidl_default_runtime',
            'rosidl_runtime_c',
            'rosidl_runtime_cpp',
            'rosidl_typesupport_c',
            'rosidl_typesupport_cpp',
            'rosidl_typesupport_fastrtps_c',
            'rosidl_typesupport_fastrtps_cpp',
            'rosidl_typesupport_interface',
            'rosidl_typesupport_introspection_c',
            'rosidl_typesupport_introspection_cpp',
            'spdlog_vendor',
            'statistics_msgs',
            'std_msgs',
            'std_srvs',
            'tracetools',
            'trajectory_msgs',
            'unique_identifier_msgs',
            'visualization_msgs',
        ]

        # out of the list since ignored by colcon: ros1_bridge
        testing_pkgs_for_quality_level = [
            'interactive_markers',
            'launch_testing_ros',
            'message_filters',
            'ros2action',
            'ros2component',
            'ros2doctor',
            'ros2interface',
            'ros2lifecycle',
            'ros2lifecycle_test_fixtures',
            'ros2param',
            'ros2topic',
            'rosbag2_compression',
            'rosbag2_cpp',
            'rosbag2_storage',
            'rosbag2_storage_default_plugins',
            'rosbag2_test_common',
            'rosbag2_tests',
            'rosbag2_transport',
            'rosidl_generator_c',
            'rosidl_generator_cpp',
            'rosidl_generator_py',
            'rosidl_runtime_py',
            'rosidl_typesupport_introspection_tests',
            'test_cli',
            'test_cli_remapping',
            'test_communication',
            'test_launch_ros',
            'test_msgs',
            'test_quality_of_service',
            'test_rclcpp',
            'test_security',
            'test_tf2',
            'test_tracetools',
            'tf2',
            'tf2_bullet',
            'tf2_eigen',
            'tf2_geometry_msgs',
            'tf2_kdl',
            'tf2_msgs',
            'tf2_py',
            'tf2_ros',
            'tf2_sensor_msgs',
        ]

        foxy_testing_pkgs_for_quality_level = copy.copy(testing_pkgs_for_quality_level)
        foxy_testing_pkgs_for_quality_level.remove('test_tracetools')
        foxy_testing_pkgs_for_quality_level.remove('rosidl_typesupport_introspection_tests')
        foxy_testing_pkgs_for_quality_level.append('tracetools_test')
        humble_testing_pkgs_for_quality_level = copy.copy(testing_pkgs_for_quality_level)
        iron_testing_pkgs_for_quality_level = copy.copy(testing_pkgs_for_quality_level)

        if os_name == 'linux':
            create_job(os_name, 'ci_' + os_name + '_coverage', 'ci_job.xml.em', {
                'cmake_build_type': 'Debug',
                'enable_coverage_default': 'true',
                'build_args_default': data['build_args_default'] + ' --packages-skip qt_gui_cpp --packages-skip-by-dep qt_gui_cpp ' +
                                      '--packages-up-to ' + ' '.join(quality_level_pkgs + testing_pkgs_for_quality_level),
                'test_args_default': data['test_args_default'] + ' --packages-skip qt_gui_cpp --packages-skip-by-dep qt_gui_cpp ' +
                                     '--packages-up-to ' + ' '.join(quality_level_pkgs + testing_pkgs_for_quality_level),
            })
            create_job(os_name, 'test_' + os_name + '_coverage', 'ci_job.xml.em', {
                'cmake_build_type': 'Debug',
                'enable_coverage_default': 'true',
                'build_args_default': data['build_args_default'] + ' --packages-skip qt_gui_cpp --packages-skip-by-dep qt_gui_cpp ' +
                                      '--packages-up-to ' + ' '.join(quality_level_pkgs + testing_pkgs_for_quality_level),
                'test_args_default': data['test_args_default'] + ' --packages-skip qt_gui_cpp --packages-skip-by-dep qt_gui_cpp ' +
                                     '--packages-up-to ' + ' '.join(quality_level_pkgs + testing_pkgs_for_quality_level),
            })

        # configure nightly coverage job on x86 Linux only
        if os_name == 'linux':
            create_job(os_name, 'nightly_' + os_name + '_coverage', 'ci_job.xml.em', {
                'cmake_build_type': 'Debug',
                'enable_coverage_default': 'true',
                'time_trigger_spec': PERIODIC_JOB_SPEC,
                'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
                'build_args_default': data['build_args_default'] +
                                      ' --packages-up-to ' + ' '.join(quality_level_pkgs + testing_pkgs_for_quality_level),
                'test_args_default': data['test_args_default'] +
                                     ' --packages-up-to ' + ' '.join(quality_level_pkgs + testing_pkgs_for_quality_level),
            })
            # Add a coverage job targeting Foxy.
            create_job(os_name, 'nightly_' + os_name + '_foxy_coverage', 'ci_job.xml.em', {
                'cmake_build_type': 'Debug',
                'default_repos_url': 'https://raw.githubusercontent.com/ros2/ros2/foxy/ros2.repos',
                'enable_coverage_default': 'true',
                'time_trigger_spec': PERIODIC_JOB_SPEC,
                'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
                'ros_distro': 'foxy',
                'ubuntu_distro': 'focal',
                'build_args_default': data['build_args_default'] +
                                      ' --packages-up-to ' + ' '.join(quality_level_pkgs + foxy_testing_pkgs_for_quality_level),
                'test_args_default': data['test_args_default'] +
                                     ' --packages-up-to ' + ' '.join(quality_level_pkgs + foxy_testing_pkgs_for_quality_level),
            })
            # Add a coverage job targeting Humble.
            create_job(os_name, 'nightly_' + os_name + '_humble_coverage', 'ci_job.xml.em', {
                'cmake_build_type': 'Debug',
                'default_repos_url': 'https://raw.githubusercontent.com/ros2/ros2/humble/ros2.repos',
                'enable_coverage_default': 'true',
                'time_trigger_spec': PERIODIC_JOB_SPEC,
                'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
                'ros_distro': 'humble',
                'ubuntu_distro': 'jammy',
                'build_args_default': data['build_args_default'] +
                                      ' --packages-up-to ' + ' '.join(quality_level_pkgs + humble_testing_pkgs_for_quality_level),
                'test_args_default': data['test_args_default'] +
                                     ' --packages-up-to ' + ' '.join(quality_level_pkgs + humble_testing_pkgs_for_quality_level),
            })
            # Add a coverage job targeting Iron.
            create_job(os_name, 'nightly_' + os_name + '_iron_coverage', 'ci_job.xml.em', {
                'cmake_build_type': 'Debug',
                'default_repos_url': 'https://raw.githubusercontent.com/ros2/ros2/iron/ros2.repos',
                'enable_coverage_default': 'true',
                'time_trigger_spec': PERIODIC_JOB_SPEC,
                'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
                'ros_distro': 'iron',
                'ubuntu_distro': 'jammy',
                'build_args_default': data['build_args_default'] +
                                      ' --packages-up-to ' + ' '.join(quality_level_pkgs + iron_testing_pkgs_for_quality_level),
                'test_args_default': data['test_args_default'] +
                                     ' --packages-up-to ' + ' '.join(quality_level_pkgs + iron_testing_pkgs_for_quality_level),
            })

        # configure nightly triggered job
        job_name = 'nightly_' + job_os_name + '_release'
        if os_name == 'windows':
            job_name = job_name[:15]
        create_job(os_name, job_name, 'ci_job.xml.em', {
            'cmake_build_type': 'Release',
            'time_trigger_spec': PERIODIC_JOB_SPEC,
            'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
        })

        # configure nightly triggered job with repeated testing
        job_name = 'nightly_' + job_os_name + '_repeated'
        if os_name == 'windows':
            job_name = job_name[:15]
        test_args_default = os_configs.get(os_name, data).get('test_args_default', data['test_args_default'])
        test_args_default = test_args_default.replace('--retest-until-pass', '--retest-until-fail')
        test_args_default = re.sub(r'(--ctest-args +-LE +)"?([^ "]+)"?', r'\1"(linter|\2)"', test_args_default)
        test_args_default = test_args_default.replace('--pytest-args -m "not xfail"', '--pytest-args -m "not linter and not xfail"')
        create_job(os_name, job_name, 'ci_job.xml.em', {
            'cmake_build_type': 'None',
            'time_trigger_spec': PERIODIC_JOB_SPEC,
            'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
            'test_args_default': test_args_default,
        })

        # configure nightly triggered job for excluded test
        job_name = 'nightly_' + job_os_name + '_xfail'
        test_args_default = os_configs.get(os_name, data).get('test_args_default', data['test_args_default'])
        test_args_default = re.sub(r'--ctest-args +-LE +"?[^ "]+"?', r'--ctest-args -L xfail', test_args_default)
        test_args_default = test_args_default.replace('--pytest-args -m "not xfail"', '--pytest-args -m xfail --runxfail')
        create_job(os_name, job_name, 'ci_job.xml.em', {
            'cmake_build_type': 'None',
            'time_trigger_spec': PERIODIC_JOB_SPEC,
            'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
            'test_args_default': test_args_default,
        })

    # configure the launch job
    for launch_prefix in ('', 'test_'):
        launcher_job_name = launch_prefix + 'ci_launcher'
        if not pattern_select_jobs_regexp or pattern_select_jobs_regexp.match(launcher_job_name):
            os_specific_data = collections.OrderedDict()
            for os_name in sorted(os_configs.keys() - launcher_exclude):
                os_specific_data[os_name] = dict(data)
                os_specific_data[os_name].update(os_configs[os_name])
                os_specific_data[os_name]['job_name'] = launch_prefix + 'ci_' + os_name
            job_data = dict(data)
            job_data['ci_scripts_default_branch'] = args.ci_scripts_default_branch
            job_data['label_expression'] = 'built-in || master'
            job_data['os_specific_data'] = os_specific_data
            job_data['cmake_build_type'] = 'None'
            job_data.update(retention_data_by_job_type(launcher_job_name))
            job_config = expand_template('ci_launcher_job.xml.em', job_data)
            configure_job(jenkins, launcher_job_name, job_config, **jenkins_kwargs)


if __name__ == '__main__':
    main()
