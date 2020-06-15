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

from ..batch_job import BatchJob
from ..util import log
from ..util import warn


class LinuxBatchJob(BatchJob):
    def __init__(self, args):
        self.args = args
        self.use_ccache = False
        # The BatchJob constructor will set self.run and self.python
        BatchJob.__init__(self, python_interpreter=args.python_interpreter)

    def pre(self):
        # Linux jobs are run on machines in the cloud
        # Assume machines won't crosstalk even if they have the same default ROS_DOMAIN_ID
        if 'ROS_DOMAIN_ID' not in os.environ:
            os.environ['ROS_DOMAIN_ID'] = '108'
        # Check for ccache's directory, as installed by apt-get
        ccache_exe_dir = '/usr/lib/ccache'
        if os.path.isdir(ccache_exe_dir):
            self.use_ccache = True
            os.environ['PATH'] = ccache_exe_dir + os.pathsep +\
                os.environ.get('PATH', '')
            print('# BEGIN SUBSECTION: ccache stats (before)')
            self.run(['ccache', '-s'])
            print('# END SUBSECTION')
        else:
            warn('ccache does not appear to be installed; not modifying PATH')

    def post(self):
        if self.use_ccache:
            print('# BEGIN SUBSECTION: ccache stats (after)')
            self.run(['ccache', '-s'])
            print('# END SUBSECTION')

    def show_env(self):
        # Show the env
        self.run(['export'], shell=True)
        # Show what pip has
        self.run(['"%s"' % self.python, '-m', 'pip', 'freeze', '--all'], shell=True)

    def setup_env(self):
        connext_env_file = None
        # Update the script provided by Connext to work in dash
        if 'rmw_connext_cpp' not in self.args.ignore_rmw:  # or 'rmw_connext_dynamic_cpp' not in self.args.ignore_rmw:
            # Location of the original Connext script
            if self.args.connext_debs:
                connext_env_file = '/opt/rti.com'
            else:
                connext_env_file = os.path.expanduser('~')
            connext_env_file = os.path.join(
                connext_env_file, 'rti_connext_dds-5.3.1',
                'resource', 'scripts', 'rtisetenv_x64Linux3gcc5.4.0.bash')

            if os.path.exists(connext_env_file):
                # Make script compatible with dash
                with open(connext_env_file, 'r') as env_file:
                    env_file_data = env_file.read()
                env_file_data = env_file_data.replace('${BASH_SOURCE[0]}', connext_env_file)
                # Create the new script to a writable location
                connext_env_file = os.path.join(os.getcwd(), 'rti.sh')
                with open(connext_env_file, 'w') as env_file:
                    env_file.write(env_file_data)
            else:
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
