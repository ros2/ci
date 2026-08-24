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

# Kept in the image by pixi.toml, see windows_docker_resources/README.md.
SCCACHE_EXECUTABLE = 'sccache'

# sccache's default is 10G.  A full ROS 2 workspace does not need that much and
# the agents run several jobs, each with a cache directory of its own.
DEFAULT_SCCACHE_CACHE_SIZE = '8G'


class WindowsBatchJob(BatchJob):
    def __init__(self, args):
        self.args = args
        self.use_sccache = False
        # The BatchJob constructor will set self.run and self.python
        BatchJob.__init__(self)

    def pre(self):
        # The Linux jobs get their compiler cache by putting /usr/lib/ccache on
        # the PATH, where the symlinks in it masquerade as the compilers.  There
        # is no equivalent on Windows, so the cache has to be named to CMake
        # instead, which is what CMAKE_<LANG>_COMPILER_LAUNCHER does.
        if shutil.which(SCCACHE_EXECUTABLE) is None:
            warn('sccache does not appear to be installed; '
                 'building without a compiler cache')
            return
        self.use_sccache = True

        # Set as environment variables rather than passed as -D on the colcon
        # command line, because CMake initializes CMAKE_<LANG>_COMPILER_LAUNCHER
        # from the environment variable of the same name.  That is what carries
        # the cache into the vendor packages: ament_vendor and
        # ExternalProject_Add run nested CMake configures that forward only a
        # fixed list of variables, and the launchers are not among them, so
        # with -D alone every vendored package still compiles uncached.
        os.environ['CMAKE_C_COMPILER_LAUNCHER'] = SCCACHE_EXECUTABLE
        os.environ['CMAKE_CXX_COMPILER_LAUNCHER'] = SCCACHE_EXECUTABLE

        # CMAKE_<LANG>_COMPILER_LAUNCHER only reaches the C and C++ compilers.
        # zenoh_cpp_vendor builds several hundred Rust crates through cargo,
        # so wrap rustc as well.  sccache refuses to cache incremental
        # compilation, hence CARGO_INCREMENTAL.
        os.environ['RUSTC_WRAPPER'] = SCCACHE_EXECUTABLE
        os.environ['CARGO_INCREMENTAL'] = '0'

        # SCCACHE_DIR is pointed at a directory mounted in from the agent by the
        # job template, so that the cache outlives the container.  When it is
        # not set -- a local run, say -- sccache falls back to a directory under
        # the profile and the cache is still worth having within one build.
        os.environ.setdefault('SCCACHE_CACHE_SIZE', DEFAULT_SCCACHE_CACHE_SIZE)
        info("Using sccache with SCCACHE_DIR='{0}' and SCCACHE_CACHE_SIZE='{1}'"
             .format(
                 os.environ.get('SCCACHE_DIR', '<unset>'),
                 os.environ['SCCACHE_CACHE_SIZE']))

        # Starts the server, which picks up the environment set above.  Every
        # sccache the build invokes afterwards talks to this one process.
        print('# BEGIN SUBSECTION: sccache stats (before)')
        self.run([SCCACHE_EXECUTABLE, '--show-stats'], exit_on_error=False)
        print('# END SUBSECTION')

    def post(self):
        if not self.use_sccache:
            return
        print('# BEGIN SUBSECTION: sccache stats (after)')
        # 'Non-cacheable compilations' and 'Cache errors' are the numbers to
        # watch here: they are compilations the cache could not help with, and
        # they are how a silently ineffective cache shows up.
        self.run([SCCACHE_EXECUTABLE, '--show-stats'], exit_on_error=False)
        # Flush the server so that the cache directory the agent keeps is
        # consistent for the next build that mounts it.
        self.run([SCCACHE_EXECUTABLE, '--stop-server'], exit_on_error=False)
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
