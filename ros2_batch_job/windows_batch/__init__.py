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

import glob
import os
import shutil

from ..batch_job import BatchJob
from ..util import info
from ..util import warn

WORKSPACE_DRIVE = 'W:'


class WindowsBatchJob(BatchJob):
    def __init__(self, args):
        self.args = args
        # The BatchJob constructor will set self.run and self.python
        BatchJob.__init__(self)

    def pre(self):
        self._map_workspace_drive()

    def _map_workspace_drive(self):
        """Map the workspace onto a drive letter, to shorten object paths."""
        target = os.path.abspath(self.args.workspace)
        self._real_workspace = target
        self.run(['subst', WORKSPACE_DRIVE, '/D'], exit_on_error=False)
        rc = self.run(
            ['subst', WORKSPACE_DRIVE, '"%s"' % target],
            exit_on_error=False, shell=True)
        mapped = WORKSPACE_DRIVE + os.sep
        if rc != 0 or not os.path.isdir(mapped):
            warn('could not map {0} onto {1}; building from the long path, '
                 'which may overrun MAX_PATH'.format(target, WORKSPACE_DRIVE))
            return
        info('Mapped {0} onto {1}'.format(target, mapped))
        self.args.workspace = mapped

    def post(self):
        self._unmap_log_paths()

    def _unmap_log_paths(self):
        """Point paths in the build logs back at the real workspace.

        The warnings publishers cannot resolve files under the subst drive.
        """
        real = getattr(self, '_real_workspace', None)
        if real is None:
            return
        pattern = os.path.join(real, 'log', 'build_*', '*', 'stdout_stderr.log')
        for path in glob.glob(pattern):
            with open(path, 'r', encoding='utf-8', errors='replace', newline='') as f:
                text = f.read()
            for sep in ('\\', '/'):
                text = text.replace(WORKSPACE_DRIVE + sep, real.rstrip('\\') + sep)
            with open(path, 'w', encoding='utf-8', newline='') as f:
                f.write(text)

    def show_env(self):
        # Show the env
        self.run(['set'], shell=True)
        # Show what pip has
        self.run([self.python, '-m', 'pip', 'list'])

    def setup_env(self):
        # Generate the env file
        if os.path.exists('env.bat'):
            os.remove('env.bat')
        with open('env.bat', 'w') as f:
            f.write("@echo off" + os.linesep)
            assert self.args.visual_studio_version is not None
            vs = self.args.visual_studio_version
            f.write(f'call "C:\\Program Files (x86)\\Microsoft Visual Studio\\{vs}\\BuildTools\\VC\\Auxiliary\\Build\\vcvarsall.bat" x86_amd64' + os.linesep)
            f.write("%*" + os.linesep)
            f.write("if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%" + os.linesep)

        # Show the result
        info("Contents of 'env.bat':")
        with open('env.bat', 'r') as f:
            print(f.read(), end='')
        current_run = self.run

        def with_vendors(cmd, **kwargs):
            # Ensure shell is on since we're using &&
            kwargs['shell'] = True
            # Use the env file to call the commands
            # ensure that quoted arguments are passed through as quoted arguments
            cmd = ['env.bat'] + [
                '"%s"' % c if (' ' in c or '|' in c) and not (c.startswith('"') and c.endswith('"')) else c
                for c in cmd]
            # Pass along to the original runner
            return current_run(cmd, **kwargs)

        # Push the custom runner
        self.push_run(with_vendors)
