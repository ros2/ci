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
        'pixi_toml_url': '',
        'time_trigger_spec': '',
        'mailer_recipients': '',
        'ignore_rmw_default': {''},
        'use_connext_debs_default': 'false',
        'use_isolated_default': 'true',
        'colcon_mixin_url': 'https://raw.githubusercontent.com/colcon/colcon-mixin-repository/master/index.yaml',
        'build_args_default': '--event-handlers console_cohesion+ console_package_list+ --cmake-args -DINSTALL_EXAMPLES=OFF -DSECURITY=ON -DAPPEND_PROJECT_NAME_TO_INCLUDEDIR=ON',
        'test_args_default': '--event-handlers console_cohesion+ --retest-until-pass 2 --ctest-args -LE xfail --pytest-args -m "not xfail"',
        'compile_with_clang_default': 'false',
        'dont_notify_every_unstable_build': 'false',
        'build_timeout_mins': 600,
        'ubuntu_distro': 'resolute',
        'el_release': '10',
        'ros_distro': 'rolling',
    }

    jenkins = connect(args.jenkins_url)

    os_configs = {
        'linux': {
            'label_expression': 'linux',
            'shell_type': 'Shell',
        },
        'windows': {
            'label_expression': 'windows-container',
            'shell_type': 'BatchFile',
            'use_isolated_default': 'false',
        },
        'linux-aarch64': {
            'label_expression': 'linux_aarch64',
            'shell_type': 'Shell',
            'use_connext_debs_default': 'true',
            'test_args_default': re.sub(r'(--ctest-args +-LE +)"?([^ "]+)"?', r'\1"(mimick|\2)"', data['test_args_default']),
        },
        'linux-rhel': {
            'label_expression': 'linux',
            'shell_type': 'Shell',
            'build_args_default': re.sub(r'(--cmake-args)', r'\1 -DPython3_EXECUTABLE=/usr/bin/python3', data['build_args_default']),
        },
    }

    os_config_overrides = {
        'linux-rhel': {
            'use_connext_debs_default': 'false',
        },
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
            'test_args_default': os_configs.get(os_name, {}).get('test_args_default', data['test_args_default']) + ' --executor sequential',
        })
        # configure test jobs for experimenting with job config changes
        # Keep parameters the same as the manual triggered job above.
        create_job(os_name, 'test_ci_' + os_name, 'ci_job.xml.em', {
            'cmake_build_type': 'None',
        })

        packaging_label_expression = os_configs[os_name]['label_expression']

        # configure a manual version of the packaging job
        ignore_rmw_default_packaging = set()
        create_job(os_name, 'ci_packaging_' + os_name, 'packaging_job.xml.em', {
            'cmake_build_type': 'RelWithDebInfo',
            'label_expression': packaging_label_expression,
            'ignore_rmw_default': ignore_rmw_default_packaging,
            'use_connext_debs_default': 'true',
        })
        # configure manual test packaging job
        create_job(os_name, 'test_packaging_' + os_name, 'packaging_job.xml.em', {
            'cmake_build_type': 'RelWithDebInfo',
            'label_expression': packaging_label_expression,
            'ignore_rmw_default': ignore_rmw_default_packaging,
            'use_connext_debs_default': 'true',
        })

        # configure packaging job
        create_job(os_name, 'packaging_' + os_name, 'packaging_job.xml.em', {
            'cmake_build_type': 'RelWithDebInfo',
            'disabled': False,
            'label_expression': packaging_label_expression,
            'time_trigger_spec': PERIODIC_JOB_SPEC,
            'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
            'ignore_rmw_default': ignore_rmw_default_packaging,
            'use_connext_debs_default': 'true',
        })

        # configure nightly triggered job
        if not os_name in ['windows']:
            job_name = 'nightly_' + job_os_name + '_debug'
            debug_build_args = data['build_args_default']
            create_job(os_name, job_name, 'ci_job.xml.em', {
                'cmake_build_type': 'Debug',
                'time_trigger_spec': PERIODIC_JOB_SPEC,
                'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
                'build_args_default': debug_build_args,
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

        # configure nightly triggered job
        job_name = 'nightly_' + job_os_name + '_release'
        if os_name in ['windows']:
            job_name = job_name[:15]
        create_job(os_name, job_name, 'ci_job.xml.em', {
            'cmake_build_type': 'Release',
            'time_trigger_spec': PERIODIC_JOB_SPEC,
            'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
        })

        # configure nightly triggered job with repeated testing
        job_name = 'nightly_' + job_os_name + '_repeated'
        if os_name in ['windows']:
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

    # configure the launch job
    for launch_prefix in ('', 'test_'):
        launcher_job_name = launch_prefix + 'ci_launcher'
        if not pattern_select_jobs_regexp or pattern_select_jobs_regexp.match(launcher_job_name):
            os_specific_data = collections.OrderedDict()
            
            for os_name in sorted(os_configs.keys()):
                os_specific_data[os_name] = dict(data)
                os_specific_data[os_name].update(os_configs[os_name])
                os_specific_data[os_name]['job_name'] = launch_prefix + 'ci_' + os_name
            job_data = dict(data)
            job_data['ci_scripts_default_branch'] = args.ci_scripts_default_branch
            job_data['label_expression'] = 'built-in || master'
            job_data['os_specific_data'] = os_specific_data
            job_data['cmake_build_type'] = 'None'
            job_data['test_args_default'] += ' --executor sequential'
            job_data.update(retention_data_by_job_type(launcher_job_name))
            job_config = expand_template('ci_launcher_job.xml.em', job_data)
            configure_job(jenkins, launcher_job_name, job_config, **jenkins_kwargs)


if __name__ == '__main__':
    main()
