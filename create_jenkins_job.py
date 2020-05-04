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
import os
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

DEFAULT_REPOS_URL = 'https://raw.githubusercontent.com/ros2/ros2/master/ros2.repos'
DEFAULT_MAIL_RECIPIENTS = 'ros2-buildfarm@googlegroups.com'
PERIODIC_JOB_SPEC = '30 7 * * *'

template_prefix_path[:] = \
    [os.path.join(os.path.abspath(os.path.dirname(__file__)), 'job_templates')]


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
    args = parser.parse_args(argv)

    data = {
        'build_discard': {
            'days_to_keep': 1000,
            'num_to_keep': 3000},
        'ci_scripts_repository': args.ci_scripts_repository,
        'ci_scripts_default_branch': args.ci_scripts_default_branch,
        'default_repos_url': DEFAULT_REPOS_URL,
        'supplemental_repos_url': '',
        'time_trigger_spec': '',
        'mailer_recipients': '',
        'ignore_rmw_default': {
            'rmw_connext_dynamic_cpp',
            'rmw_fastrtps_dynamic_cpp',
            'rmw_opensplice_cpp'},
        'use_connext_debs_default': 'false',
        'use_isolated_default': 'true',
        'colcon_mixin_url': 'https://raw.githubusercontent.com/colcon/colcon-mixin-repository/master/index.yaml',
        'build_args_default': '--event-handlers console_cohesion+ console_package_list+ --cmake-args -DINSTALL_EXAMPLES=OFF -DSECURITY=ON',
        'test_args_default': '--event-handlers console_direct+ --executor sequential --retest-until-pass 2 --ctest-args -LE xfail --pytest-args -m "not xfail"',
        'compile_with_clang_default': 'false',
        'enable_coverage_default': 'false',
        'dont_notify_every_unstable_build': 'false',
        'turtlebot_demo': False,
        'build_timeout_mins': 0,
        'ubuntu_distro': 'focal',
    }

    jenkins = connect(args.jenkins_url)

    os_configs = {
        'linux': {
            'label_expression': 'linux',
            'shell_type': 'Shell',
        },
        'osx': {
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
            'ignore_rmw_default': data['ignore_rmw_default'] | {'rmw_connext_cpp', 'rmw_connext_dynamic_cpp'},
        },
        'linux-armhf': {
            'label_expression': 'linux_armhf',
            'shell_type': 'Shell',
            'ignore_rmw_default': data['ignore_rmw_default'] | {'rmw_connext_cpp', 'rmw_connext_dynamic_cpp'},
            'build_args_default': data['build_args_default'].replace(
                '--cmake-args', '--cmake-args -DCMAKE_CXX_FLAGS=-Wno-psabi -DCMAKE_C_FLAGS=-Wno-psabi -DDISABLE_SANITIZERS=ON'),
        },
        'linux-centos': {
            'label_expression': 'linux',
            'shell_type': 'Shell',
            'build_args_default': '--packages-skip-by-dep image_tools ros1_bridge --packages-skip image_tools ros1_bridge ' + data['build_args_default'].replace(
                '--cmake-args', '--cmake-args -DCMAKE_POLICY_DEFAULT_CMP0072=NEW -DPYTHON_VERSION=3.6 -DDISABLE_SANITIZERS=ON'),
            'test_args_default': '--packages-skip-by-dep image_tools ros1_bridge --packages-skip image_tools ros1_bridge ' + data['test_args_default'],
        },
    }

    os_config_overrides = {
        'linux-centos': {
            'mixed_overlay_pkgs': '',
            'ignore_rmw_default': {'rmw_connext_cpp', 'rmw_connext_dynamic_cpp', 'rmw_opensplice_cpp'},
            'use_connext_debs_default': 'false',
        },
    }

    launcher_exclude = {
        'linux-armhf',
        'linux-centos',
        'windows-metal',
    }

    jenkins_kwargs = {}
    if not args.commit:
        jenkins_kwargs['dry_run'] = True

    def create_job(os_name, job_name, template_file, additional_dict):
        job_data = dict(data)
        job_data['os_name'] = os_name
        job_data.update(os_configs[os_name])
        job_data.update(additional_dict)
        job_data.update(os_config_overrides.get(os_name, {}))
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
        ignore_rmw_default_packaging = {'rmw_opensplice_cpp'}
        if os_name in ['linux-aarch64', 'linux-armhf']:
            ignore_rmw_default_packaging |= {'rmw_connext_cpp', 'rmw_connext_dynamic_cpp'}
        create_job(os_name, 'ci_packaging_' + os_name, 'packaging_job.xml.em', {
            'build_discard': {
                'days_to_keep': 180,
                'num_to_keep': 100,
            },
            'cmake_build_type': 'RelWithDebInfo',
            'label_expression': packaging_label_expression,
            'mixed_overlay_pkgs': 'ros1_bridge',
            'ignore_rmw_default': ignore_rmw_default_packaging,
            'use_connext_debs_default': 'true',
        })

        # configure packaging job
        create_job(os_name, 'packaging_' + os_name, 'packaging_job.xml.em', {
            'build_discard': {
                'days_to_keep': 370,
                'num_to_keep': 370,
            },
            'cmake_build_type': 'RelWithDebInfo',
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
                'build_discard': {
                    'days_to_keep': 370,
                    'num_to_keep': 370,
                    },
                'cmake_build_type': 'Debug',
                'mixed_overlay_pkgs': 'ros1_bridge',
                'time_trigger_spec': PERIODIC_JOB_SPEC,
                'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
                'ignore_rmw_default': ignore_rmw_default_packaging,
                'use_connext_debs_default': 'true',
            })

        # configure nightly triggered job
        job_name = 'nightly_' + job_os_name + '_debug'
        if os_name == 'windows':
            job_name = job_name[:15]
        create_job(os_name, job_name, 'ci_job.xml.em', {
            'cmake_build_type': 'Debug',
            'time_trigger_spec': PERIODIC_JOB_SPEC,
            'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
        })

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

        # configure nightly job for compiling with clang+libcxx on linux
        if os_name == 'linux':
            # Set the logging implementation to noop because log4cxx will not link properly when using libcxx.
            clang_libcxx_build_args = data['build_args_default'].replace('--cmake-args',
                '--cmake-args -DRCL_LOGGING_IMPLEMENTATION=rcl_logging_noop') + \
                ' --mixin clang-libcxx'
            create_job(os_name, 'nightly_' + os_name + '_clang_libcxx', 'ci_job.xml.em', {
                'cmake_build_type': 'Debug',
                'compile_with_clang_default': 'true',
                'time_trigger_spec': PERIODIC_JOB_SPEC,
                'mailer_recipients': DEFAULT_MAIL_RECIPIENTS + ' ros-contributions@amazon.com',
                'build_args_default': clang_libcxx_build_args,
                # Only running test from the lowest-level C package to ensure "working" binaries are generated.
                # We do not want to test more than this as we observe issues with the clang libcxx standard library
                # we don't plan to tackle for now. The important part of this nightly is to make sure the code compiles
                # without emitting thread-safety related warnings.
                'test_args_default': data['test_args_default'].replace(' --retest-until-pass 2', '') + ' --packages-select rcutils'
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
        if os_name == 'linux':
            create_job(os_name, 'ci_' + os_name + '_coverage', 'ci_job.xml.em', {
                'build_discard': {
                    'days_to_keep': 100,
                    'num_to_keep': 100,
                },
                'cmake_build_type': 'Debug',
                'enable_coverage_default': 'true',
                'build_args_default': data['build_args_default'] + ' --packages-skip qt_gui_cpp --packages-skip-by-dep qt_gui_cpp',
                'test_args_default': data['test_args_default'] + ' --packages-skip qt_gui_cpp --packages-skip-by-dep qt_gui_cpp',
            })
            create_job(os_name, 'test_' + os_name + '_coverage', 'ci_job.xml.em', {
                'build_discard': {
                    'days_to_keep': 100,
                    'num_to_keep': 100,
                },
                'cmake_build_type': 'Debug',
                'enable_coverage_default': 'true',
                'build_args_default': data['build_args_default'] + ' --packages-skip qt_gui_cpp --packages-skip-by-dep qt_gui_cpp',
                'test_args_default': data['test_args_default'] + ' --packages-skip qt_gui_cpp --packages-skip-by-dep qt_gui_cpp',
            })

        # configure nightly coverage job on x86 Linux only
        if os_name == 'linux':
            create_job(os_name, 'nightly_' + os_name + '_coverage', 'ci_job.xml.em', {
                'build_discard': {
                    'days_to_keep': 100,
                    'num_to_keep': 100,
                },
                'cmake_build_type': 'Debug',
                'enable_coverage_default': 'true',
                'time_trigger_spec': PERIODIC_JOB_SPEC,
                'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
            })

        # configure nightly triggered job using FastRTPS dynamic
        job_name = 'nightly_' + job_os_name + '_extra_rmw' + '_release'
        if os_name == 'windows':
            job_name = job_name[:25]
        create_job(os_name, job_name, 'ci_job.xml.em', {
            'cmake_build_type': 'Release',
            'time_trigger_spec': PERIODIC_JOB_SPEC,
            'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
            'ignore_rmw_default': {
                'rmw_connext_cpp',
                'rmw_connext_dynamic_cpp',
                'rmw_opensplice_cpp'},
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
        test_args_default = test_args_default.replace('--ctest-args -LE xfail', '--ctest-args -LE "(linter|xfail)"')
        test_args_default = test_args_default.replace('--pytest-args -m "not xfail"', '--pytest-args -m "not linter and not xfail"')
        if job_os_name == 'linux-aarch64':
            # skipping known to be flaky tests https://github.com/ros2/rviz/issues/368
            test_args_default += ' --packages-skip rviz_common rviz_default_plugins rviz_rendering rviz_rendering_tests'
        create_job(os_name, job_name, 'ci_job.xml.em', {
            'cmake_build_type': 'None',
            'time_trigger_spec': PERIODIC_JOB_SPEC,
            'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
            'test_args_default': test_args_default,
        })

        # configure nightly triggered job for excluded test
        job_name = 'nightly_' + job_os_name + '_xfail'
        test_args_default = os_configs.get(os_name, data).get('test_args_default', data['test_args_default'])
        test_args_default = test_args_default.replace('--ctest-args -LE xfail', '--ctest-args -L xfail')
        test_args_default = test_args_default.replace('--pytest-args -m "not xfail"', '--pytest-args -m xfail --runxfail')
        create_job(os_name, job_name, 'ci_job.xml.em', {
            'cmake_build_type': 'None',
            'time_trigger_spec': PERIODIC_JOB_SPEC,
            'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
            'test_args_default': test_args_default,
        })

        # configure turtlebot jobs on Linux only for now
        if os_name in ['linux', 'linux-aarch64']:
            create_job(os_name, 'ci_turtlebot-demo_' + os_name, 'ci_job.xml.em', {
                'cmake_build_type': 'None',
                'turtlebot_demo': True,
                'supplemental_repos_url': 'https://raw.githubusercontent.com/ros2/turtlebot2_demo/master/turtlebot2_demo.repos',
            })
            create_job(os_name, 'nightly_turtlebot-demo_' + os_name + '_release', 'ci_job.xml.em', {
                'disabled': True,
                'cmake_build_type': 'Release',
                'turtlebot_demo': True,
                'supplemental_repos_url': 'https://raw.githubusercontent.com/ros2/turtlebot2_demo/master/turtlebot2_demo.repos',
                'time_trigger_spec': PERIODIC_JOB_SPEC,
                'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
            })

    # configure the launch job
    os_specific_data = collections.OrderedDict()
    for os_name in sorted(os_configs.keys() - launcher_exclude):
        os_specific_data[os_name] = dict(data)
        os_specific_data[os_name].update(os_configs[os_name])
        os_specific_data[os_name]['job_name'] = 'ci_' + os_name
    job_data = dict(data)
    job_data['ci_scripts_default_branch'] = args.ci_scripts_default_branch
    job_data['label_expression'] = 'master'
    job_data['os_specific_data'] = os_specific_data
    job_data['cmake_build_type'] = 'None'
    job_config = expand_template('ci_launcher_job.xml.em', job_data)
    configure_job(jenkins, 'ci_launcher', job_config, **jenkins_kwargs)


if __name__ == '__main__':
    main()
