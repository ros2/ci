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
    sys.exit("Could not import ros_buildfarm, please add to the PYTHONPATH.")

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
        '--jenkins-url', '-u', default='https://ci.ros2.org/',
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
        help='Actually modify the Jenkis jobs instead of only doing a dry run',
    )
    args = parser.parse_args(argv)

    data = {
        'ci_scripts_repository': args.ci_scripts_repository,
        'ci_scripts_default_branch': args.ci_scripts_default_branch,
        'default_repos_url': DEFAULT_REPOS_URL,
        'supplemental_repos_url': '',
        'time_trigger_spec': '',
        'mailer_recipients': '',
        'use_connext_default': 'true',
        'disable_connext_static_default': 'false',
        'disable_connext_dynamic_default': 'true',
        'use_osrf_connext_debs_default': 'false',
        'use_fastrtps_default': 'true',
        'use_opensplice_default': 'false',
        'build_args_default': '--event-handler console_cohesion+ --cmake-args " -DSECURITY=ON"',
        'test_args_default': '--event-handler console_cohesion+ --retest-until-pass 10',
        'enable_c_coverage_default': 'false',
        'dont_notify_every_unstable_build': 'false',
        'turtlebot_demo': False,
        'build_timeout_mins': 0,
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
        'windows': {
            'label_expression': 'windows',
            'shell_type': 'BatchFile',
        },
        'linux-aarch64': {
            'label_expression': 'linux_aarch64',
            'shell_type': 'Shell',
            'use_connext_default': 'false',
        },
    }

    jenkins_kwargs = {}
    if not args.commit:
        jenkins_kwargs['dry_run'] = True

    def create_job(os_name, job_name, template_file, additional_dict):
        job_data = dict(data)
        job_data['os_name'] = os_name
        job_data.update(os_configs[os_name])
        job_data.update(additional_dict)
        job_config = expand_template(template_file, job_data)
        configure_job(jenkins, job_name, job_config, **jenkins_kwargs)

    # configure os specific jobs
    for os_name in sorted(os_configs.keys()):
        # We need the keep the paths short on Windows, so on that platform make
        # the os_name shorter just for the jobs
        job_os_name = os_name
        if os_name == 'windows':
            job_os_name = 'win'

        # configure manual triggered job
        create_job(os_name, 'ci_' + os_name, 'ci_job.xml.em', {
            'cmake_build_type': 'None',
        })

        # configure a manual version of the packaging job
        create_job(os_name, 'ci_packaging_' + os_name, 'packaging_job.xml.em', {
            'cmake_build_type': 'RelWithDebInfo',
            'test_bridge_default': 'true',
        })

        # configure packaging job
        create_job(os_name, 'packaging_' + os_name, 'packaging_job.xml.em', {
            'cmake_build_type': 'RelWithDebInfo',
            'test_bridge_default': 'true',
            'time_trigger_spec': PERIODIC_JOB_SPEC,
            'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
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

        # configure nightly coverage job on x86 Linux only
        if os_name == 'linux':
            create_job(os_name, 'nightly_' + os_name + '_coverage', 'ci_job.xml.em', {
                'cmake_build_type': 'Debug',
                'enable_c_coverage_default': 'true',
                'time_trigger_spec': PERIODIC_JOB_SPEC,
                'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
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
        create_job(os_name, job_name, 'ci_job.xml.em', {
            'cmake_build_type': 'None',
            'time_trigger_spec': PERIODIC_JOB_SPEC,
            'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
            'test_args_default': '--retest-until-fail 20 --ctest-args " -LE" linter',
        })

        # configure turtlebot jobs on Linux only for now
        if os_name in ['linux', 'linux-aarch64']:
            create_job(os_name, 'ci_turtlebot-demo_' + os_name, 'ci_job.xml.em', {
                'cmake_build_type': 'None',
                'turtlebot_demo': True,
                'supplemental_repos_url': 'https://raw.githubusercontent.com/ros2/turtlebot2_demo/master/turtlebot2_demo.repos',
            })
            create_job(os_name, 'nightly_turtlebot-demo_' + os_name + '_release', 'ci_job.xml.em', {
                'cmake_build_type': 'Release',
                'turtlebot_demo': True,
                'supplemental_repos_url': 'https://raw.githubusercontent.com/ros2/turtlebot2_demo/master/turtlebot2_demo.repos',
                'time_trigger_spec': PERIODIC_JOB_SPEC,
                'mailer_recipients': DEFAULT_MAIL_RECIPIENTS,
            })

    # configure the launch job
    os_specific_data = collections.OrderedDict()
    for os_name in sorted(os_configs.keys()):
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
