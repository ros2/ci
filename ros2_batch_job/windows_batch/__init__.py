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
import shutil

from ..batch_job import BatchJob
from ..util import info
from ..util import warn

SCCACHE_EXECUTABLE = 'sccache'
DEFAULT_SCCACHE_CACHE_SIZE = '8G'
WORKSPACE_DRIVE = 'W:'


class WindowsBatchJob(BatchJob):
    def __init__(self, args):
        self.args = args
        self.use_sccache = False
        # The BatchJob constructor will set self.run and self.python
        BatchJob.__init__(self)
        # post() runs outside the workspace, where env.bat does not exist.
        self.run_without_env_bat = self.run

    def pre(self):
        self._setup_compiler_cache()
        self._map_workspace_drive()

    def _setup_compiler_cache(self):
        if shutil.which(SCCACHE_EXECUTABLE) is None:
            warn('sccache does not appear to be installed; '
                 'building without a compiler cache')
            return
        self.use_sccache = True

        # Exported rather than passed as -D, so ament_vendor sub-builds see them.
        os.environ['CMAKE_C_COMPILER_LAUNCHER'] = SCCACHE_EXECUTABLE
        os.environ['CMAKE_CXX_COMPILER_LAUNCHER'] = SCCACHE_EXECUTABLE
        os.environ['RUSTC_WRAPPER'] = SCCACHE_EXECUTABLE
        os.environ['CARGO_INCREMENTAL'] = '0'

        # The Jenkins workspace outlives the container; run() only removes 'ws'.
        os.environ.setdefault(
            'SCCACHE_DIR', os.path.join(os.getcwd(), '.sccache'))
        os.environ.setdefault('SCCACHE_CACHE_SIZE', DEFAULT_SCCACHE_CACHE_SIZE)
        # Keep the server, and its stats, alive until post().
        os.environ.setdefault('SCCACHE_IDLE_TIMEOUT', '0')
        info("Using sccache with SCCACHE_DIR='{0}' and SCCACHE_CACHE_SIZE='{1}'"
             .format(
                 os.environ['SCCACHE_DIR'],
                 os.environ['SCCACHE_CACHE_SIZE']))

        print('# BEGIN SUBSECTION: sccache stats (before)')
        self.run_without_env_bat(
            [SCCACHE_EXECUTABLE, '--show-stats'], exit_on_error=False)
        print('# END SUBSECTION')

    def _map_workspace_drive(self):
        """Map the workspace onto a drive letter, to shorten object paths."""
        target = os.path.abspath(self.args.workspace)
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
        if not self.use_sccache:
            return
        print('# BEGIN SUBSECTION: sccache stats (after)')
        self.run_without_env_bat(
            [SCCACHE_EXECUTABLE, '--show-stats'], exit_on_error=False)
        self.run_without_env_bat(
            [SCCACHE_EXECUTABLE, '--stop-server'], exit_on_error=False)
        print('# END SUBSECTION')

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
