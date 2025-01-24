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
        BatchJob.__init__(self)

    def pre(self):
        # Linux jobs are run on machines in the cloud
        # Assume machines won't crosstalk even if they have the same default ROS_DOMAIN_ID
        if 'ROS_DOMAIN_ID' not in os.environ:
            os.environ['ROS_DOMAIN_ID'] = '1'
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
        current_run = self.run

        def with_vendors(cmd, **kwargs):
            # Ensure shell is on since we're using &&
            kwargs['shell'] = True
            # Pass along to the original runner
            return current_run(cmd, **kwargs)

        # Push the custom runner
        self.push_run(with_vendors)
