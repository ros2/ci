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

import os
import subprocess

from ..batch_job import BatchJob
from ..util import log
from ..util import warn


class OSXBatchJob(BatchJob):
    def __init__(self, args):
        self.args = args
        # The BatchJob constructor will set self.run and self.python
        BatchJob.__init__(self, python_interpreter=args.python_interpreter)

    def pre(self):
        # Prepend the PATH with `/usr/local/bin` for global Homebrew binaries.
        os.environ['PATH'] = '/usr/local/bin' + os.pathsep + os.environ.get('PATH', '')
        # Check for ccache's directory, as installed by brew
        ccache_exe_dir = '/usr/local/opt/ccache/libexec'
        if os.path.isdir(ccache_exe_dir):
            os.environ['PATH'] = ccache_exe_dir + os.pathsep + os.environ.get('PATH', '')
        else:
            warn('ccache does not appear to be installed; not modifying PATH')
        if 'LANG' not in os.environ:
            os.environ['LANG'] = 'en_US.UTF-8'
        if 'ROS_DOMAIN_ID' not in os.environ:
            os.environ['ROS_DOMAIN_ID'] = '111'
        if 'OPENSSL_ROOT_DIR' not in os.environ:
            brew_openssl_prefix_result = subprocess.run(
                ['brew', '--prefix', 'openssl'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if not brew_openssl_prefix_result.stderr:
              os.environ['OPENSSL_ROOT_DIR'] = brew_openssl_prefix_result.stdout.decode().strip('\n')
        if 'OSPL_HOME' not in os.environ:
            os.environ['OSPL_HOME'] = os.path.join(os.environ['HOME'], 'opensplice', 'HDE', 'x86_64.darwin10_clang')

    def show_env(self):
        # Show the env
        self.run(['export'], shell=True)
        # Show what brew has
        self.run(['brew', 'list', '--versions'])
        # Show what pip has
        self.run(['"%s"' % self.python, '-m', 'pip', 'freeze'], shell=True)

    def setup_env(self):
        connext_env_file = None
        if self.args.connext:
            # Try to find the connext env file and source it
            connext_env_file = os.path.join(
                '/Applications', 'rti_connext_dds-5.3.0', 'resource', 'scripts',
                'rtisetenv_x64Darwin16clang8.0.bash')
            if not os.path.exists(connext_env_file):
                warn("Asked to use Connext but the RTI env was not found at '{0}'".format(
                    connext_env_file))
                connext_env_file = None
        # There is nothing extra to be done for OpenSplice

        ros1_setup_file = None
        if self.args.ros1_path:
            # Try to find the setup file and source it
            ros1_setup_file = os.path.join(self.args.ros1_path, 'setup.sh')
            if not os.path.exists(ros1_setup_file):
                warn("Asked to use ROS 1 but the setup file was not found at '{0}'".format(
                    ros1_setup_file))
                ros1_setup_file = None

        current_run = self.run

        def with_vendors(cmd, **kwargs):
            # Ensure shell is on since we're using &&
            kwargs['shell'] = True
            # If the connext file is there, source it.
            if connext_env_file is not None:
                cmd = ['.', '"%s"' % connext_env_file, '&&'] + cmd
                log('(RTI)')
            if ros1_setup_file:
                cmd = ['.', '"%s"' % ros1_setup_file, '&&'] + cmd
                log('(ROS1)')
            # Pass along to the original runner
            return current_run(cmd, **kwargs)

        # Push the custom runner
        self.push_run(with_vendors)
