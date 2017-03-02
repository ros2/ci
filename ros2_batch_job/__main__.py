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
import os
import platform
import subprocess
import sys

# Make sure we're using Python3
assert sys.version.startswith('3'), "This script is only meant to work with Python3"

# Make sure to get osrf_pycommon from the vendor folder
vendor_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'vendor'))
sys.path.insert(0, os.path.join(vendor_path, 'osrf_pycommon'))
import osrf_pycommon
# Assert that we got it from the right place
assert osrf_pycommon.__file__.startswith(vendor_path), \
    ("osrf_pycommon imported from '{0}' which is not in the vendor folder '{1}'"
     .format(osrf_pycommon.__file__, vendor_path))
from osrf_pycommon.cli_utils.common import extract_argument_group

from . import DEFAULT_REPOS_URL
from .util import change_directory
from .util import remove_folder
from .util import force_color
from .util import generated_venv_vars
from .util import info
from .util import log
from .util import UnbufferedIO

# Enforce unbuffered output
sys.stdout = UnbufferedIO(sys.stdout)
sys.stderr = UnbufferedIO(sys.stderr)

pip_dependencies = [
    'EmPy',
    'coverage',
    'flake8',
    'flake8-import-order',
    'mock',
    'nose',
    'pep8',
    'pydocstyle',
    'pyflakes',
    'vcstool',
]

gcov_flags = " -fprofile-arcs -ftest-coverage "

def main(sysargv=None):
    args = get_args(sysargv=sysargv)
    blacklisted_package_names = [
        'actionlib_msgs',
        'shape_msgs',
        'std_srvs',
        'stereo_msgs',
        'trajectory_msgs',
        'visualization_msgs'
    ]
    return run(args, build_and_test, blacklisted_package_names=blacklisted_package_names)


def get_args(sysargv=None, skip_white_space_in=False, skip_connext=False, add_ros1=False):
    parser = argparse.ArgumentParser(
        description="Builds the ROS2 repositories as a single batch job")
    parser.add_argument(
        '--repo-file-url',
        default=DEFAULT_REPOS_URL,
        help="url of the ros2.repos file to fetch and use for the basis of the batch job")
    parser.add_argument(
        '--test-branch', default=None,
        help="branch to attempt to checkout before doing batch job")
    if not skip_white_space_in:
        parser.add_argument(
            '--white-space-in', nargs='*', default=None,
            choices=['sourcespace', 'buildspace', 'installspace', 'workspace'],
            help="which folder structures in which white space should be added")
    parser.add_argument(
        '--do-venv', default=False, action='store_true',
        help="create and use a virtual env in the build process")
    parser.add_argument(
        '--os', default=None, choices=['linux', 'osx', 'windows'])
    if not skip_connext:
        parser.add_argument(
            '--connext', default=False, action='store_true',
            help="try to build with connext")
        parser.add_argument(
            '--disable-connext-static', default=False, action='store_true',
            help="disable connext static")
        parser.add_argument(
            '--disable-connext-dynamic', default=False, action='store_true',
            help="disable connext dynamic")
    parser.add_argument(
        '--osrf-connext-debs', default=False, action='store_true',
        help="use OSRF-built debs for Connext instead of binaries off the RTI website (linux only)")
    parser.add_argument(
        '--fastrtps', default=False, action='store_true',
        help="try to build with FastRTPS")
    parser.add_argument(
        '--opensplice', default=False, action='store_true',
        help="try to build with OpenSplice")
    parser.add_argument(
        '--isolated', default=False, action='store_true',
        help="build and install each package a separate folders")
    parser.add_argument(
        '--force-ansi-color', default=False, action='store_true',
        help="forces this program to output ansi color")
    if add_ros1:
        parser.add_argument(
            '--ros1-path', default=None,
            help="path of ROS 1 workspace to be sourced")
    parser.add_argument(
        '--test-bridge', default=False, action='store_true',
        help='test ros1_bridge')
    parser.add_argument(
        '--cmake-build-type', default=None,
        help='select the CMake build type')
    parser.add_argument(
        '--ament-build-args', default=None,
        help="arguments passed to 'ament build'")
    parser.add_argument(
        '--ament-test-args', default=None,
        help="arguments passed to 'ament test'")
    parser.add_argument(
        '--src-mounted', default=False, action='store_true',
        help="src directory is already mounted into the workspace")
    parser.add_argument(
        '--coverage', default=False, action='store_true',
        help="enable collection of coverage statistics")
    parser.add_argument(
        '--workspace-path', default=None,
        help="base path of the workspace")

    argv = sysargv[1:] if sysargv is not None else sys.argv[1:]
    argv, ament_build_args = extract_argument_group(argv, '--ament-build-args')
    if '--ament-test-args' in argv:
        argv, ament_test_args = extract_argument_group(argv, '--ament-test-args')
    else:
        ament_build_args, ament_test_args = extract_argument_group(ament_build_args, '--ament-test-args')
    args = parser.parse_args(argv)
    args.ament_build_args = ament_build_args
    args.ament_test_args = ament_test_args
    if skip_white_space_in:
        args.white_space_in = None
    if skip_connext:
        args.connext = False
        args.disable_connext_dynamic = False
        args.disable_connext_static = False
    if not add_ros1:
        args.ros1_path = None
    return args


def process_coverage(args, job):
    print('# BEGIN SUBSECTION: coverage analysis')
    # Collect all .gcda files in args.workspace
    ament_py = get_ament_script(args.sourcespace)
    output = subprocess.check_output(
        [job.python, '-u', ament_py, 'list_packages', args.sourcespace])
    for line in output.decode().splitlines():
        package_name, package_path = line.split(' ', 1)
        print(package_name)
        package_build_path = os.path.join(args.buildspace, package_name)
        gcda_files = []
        for root, dirs, files in os.walk(package_build_path):
            gcda_files.extend(
                    [os.path.abspath(os.path.join(root, f))
                        for f in files if f.endswith('.gcda')])
        if len(gcda_files) is 0:
            continue

        # Run one gcov command for all gcda files for this package.
        cmd = ['gcov', '--preserve-paths', '--relative-only', '--source-prefix', os.path.abspath('.')] + gcda_files
        print(cmd)
        subprocess.run(cmd, check=True, cwd=package_build_path)

        # Write one report for the entire package.
        # cobertura plugin looks for files of the regex *coverage.xml
        outfile = os.path.join(package_build_path, package_name + '.coverage.xml')
        print('Writing coverage.xml report at path {}'.format(outfile))
        # -e /usr  Ignore files from /usr
        # -xml  Output cobertura xml
        # -output=<outfile>  Pass name of output file
        # -g  use existing .gcov files in the directory
        cmd = [
            'gcovr',
            '--object-directory=' + package_build_path,
            '-k',
            '-r', os.path.abspath('.'),
            '--xml', '--output=' + outfile,
            '-g']
        print(cmd)
        subprocess.run(cmd, check=True)

    # remove Docker specific base path from coverage files
    if args.workspace_path:
        docker_base_path = os.path.dirname(os.path.abspath('.'))
        for root, dirs, files in os.walk(args.buildspace):
            for f in sorted(files):
                if not f.endswith('coverage.xml'):
                    continue
                coverage_path = os.path.join(root, f)
                with open(coverage_path, 'r') as h:
                    content = h.read()
                content = content.replace(
                    '<source>%s/' % docker_base_path,
                    '<source>%s/' % args.workspace_path)
                with open(coverage_path, 'w') as h:
                    h.write(content)

    print('# END SUBSECTION')
    return 0


def build_and_test(args, job):
    ament_py = get_ament_script(args.sourcespace)
    coverage = args.coverage and args.os == 'linux'

    print('# BEGIN SUBSECTION: ament build')
    # Now run ament build
    ret_build = job.run([
        '"%s"' % job.python, '-u', '"%s"' % ament_py, 'build',
        '"%s"' % args.sourcespace,
        '--build-tests',
        '--build-space', '"%s"' % args.buildspace,
        '--install-space', '"%s"' % args.installspace,
    ] + (['--isolated'] if args.isolated else []) +
        (
            ['--cmake-args', '-DCMAKE_BUILD_TYPE=' +
                args.cmake_build_type + ' --']
            if args.cmake_build_type else []
        ) + args.ament_build_args +
        (['--ament-cmake-args -DCMAKE_CXX_FLAGS="${CMAKE_CXX_FLAGS} ' +
            gcov_flags + ' " -DCMAKE_C_FLAGS="${CMAKE_C_FLAGS} ' +
            gcov_flags + '" --']
            if coverage else []), shell=True)
    info("ament.py build returned: '{0}'".format(ret_build))
    print('# END SUBSECTION')
    if ret_build:
        return ret_build

    print('# BEGIN SUBSECTION: ament test')
    # Run tests
    ret_test = job.run([
        '"%s"' % job.python, '-u', '"%s"' % ament_py, 'test',
        '"%s"' % args.sourcespace,
        '--build-space', '"%s"' % args.buildspace,
        '--install-space', '"%s"' % args.installspace,
        # Skip building and installing, since we just did that successfully.
        '--skip-build', '--skip-install',
    ] + (['--isolated'] if args.isolated else []) + args.ament_test_args,
        exit_on_error=False, shell=True)
    info("ament.py test returned: '{0}'".format(ret_test))
    print('# END SUBSECTION')
    if ret_test:
        return ret_test

    print('# BEGIN SUBSECTION: ament test_results')
    # Collect the test results
    ret_test_results = job.run(
        ['"%s"' % job.python, '-u', '"%s"' % ament_py, 'test_results', '"%s"' % args.buildspace],
        exit_on_error=False, shell=True
    )
    info("ament.py test_results returned: '{0}'".format(ret_test_results))
    print('# END SUBSECTION')
    if coverage:
        process_coverage(args, job)

    # Uncomment this line to failing tests a failrue of this command.
    # return 0 if ret_test == 0 and ret_testr == 0 else 1
    return 0


def run(args, build_function, blacklisted_package_names=None):
    if blacklisted_package_names is None:
        blacklisted_package_names = []
    if args.force_ansi_color:
        force_color()

    info("run_ros2_batch called with args:")
    for arg in vars(args):
        info("  - {0}={1}".format(arg, getattr(args, arg)))

    job = None

    args.white_space_in = args.white_space_in or []
    args.workspace = 'work space' if 'workspace' in args.white_space_in else 'ws'
    args.sourcespace = 'source space' if 'sourcespace' in args.white_space_in else 'src'
    args.buildspace = 'build space' if 'buildspace' in args.white_space_in else 'build'
    args.installspace = 'install space' if 'installspace' in args.white_space_in else 'install'

    if args.disable_connext_static:
        os.environ["CONNEXT_STATIC_DISABLE"] = '1'
    if args.disable_connext_dynamic:
        os.environ["CONNEXT_DYNAMIC_DISABLE"] = '1'

    platform_name = platform.platform().lower()
    if args.os == 'linux' or platform_name.startswith('linux'):
        args.os = 'linux'
        from .linux_batch import LinuxBatchJob
        job = LinuxBatchJob(args)
    elif args.os == 'osx' or platform_name.startswith('darwin'):
        args.os = 'osx'
        from .osx_batch import OSXBatchJob
        job = OSXBatchJob(args)
    elif args.os == 'windows' or platform_name.startswith('windows'):
        args.os = 'windows'
        from .windows_batch import WindowsBatchJob
        job = WindowsBatchJob(args)

    if args.do_venv and args.os == 'windows':
        sys.exit("--do-venv is not supported on windows")

    # Set the TERM env variable to coerce the output of Make to be colored.
    os.environ['TERM'] = os.environ.get('TERM', 'xterm-256color')
    if args.os == 'windows':
        # Set the ConEmuANSI env variable to trick some programs (vcs) into
        # printing ANSI color codes on Windows.
        os.environ['ConEmuANSI'] = 'ON'

    info("Using workspace: @!{0}", fargs=(args.workspace,))
    # git doesn't work reliably inside qemu, so we're assuming that somebody
    # already checked out the code on the host and mounted it in at the right
    # place in <workspace>/src, which we don't want to remove here.
    if args.src_mounted:
        remove_folder(os.path.join(args.workspace, 'build'))
        remove_folder(os.path.join(args.workspace, 'install'))
    else:
        remove_folder(args.workspace)
    if not os.path.isdir(args.workspace):
        os.makedirs(args.workspace)

    # Allow batch job to do OS specific stuff
    job.pre()
    # Check the env
    job.show_env()

    # Enter a venv if asked to, the venv must be in a path without spaces
    if args.do_venv:
        print('# BEGIN SUBSECTION: enter virtualenv')

        # Make sure virtual env is installed
        if args.os != 'linux':
            # Do not try this on Linux, as elevated privileges are needed.
            # Also there is no good way to get elevated privileges.
            # So the Linux host or Docker vm will need to ensure a modern
            # version of virtualenv is available.
            job.run([sys.executable, '-m', 'pip', 'install', '-U', 'virtualenv'])

        venv_subfolder = 'venv'
        remove_folder(venv_subfolder)
        job.run([sys.executable, '-m', 'virtualenv', '-p', sys.executable, venv_subfolder])
        venv_path = os.path.abspath(os.path.join(os.getcwd(), venv_subfolder))
        venv, venv_python = generated_venv_vars(venv_path)
        job.push_run(venv)  # job.run is now venv
        job.push_python(venv_python)  # job.python is now venv_python
        job.show_env()
        print('# END SUBSECTION')

    # Now inside of the workspace...
    with change_directory(args.workspace):
        print('# BEGIN SUBSECTION: install Python packages')
        # Update setuptools
        job.run(['"%s"' % job.python, '-m', 'pip', 'install', '-U', 'pip', 'setuptools'],
                shell=True)
        # Print setuptools version
        job.run(['"%s"' % job.python, '-c', '"import setuptools; print(setuptools.__version__)"'],
                shell=True)
        # Print the pip version
        job.run(['"%s"' % job.python, '-m', 'pip', '--version'], shell=True)
        # Install pip dependencies
        job.run(['"%s"' % job.python, '-m', 'pip', 'install', '-U'] + pip_dependencies, shell=True)
        # Show what pip has
        job.run(['"%s"' % job.python, '-m', 'pip', 'freeze'], shell=True)
        print('# END SUBSECTION')

        # Skip git operations on arm because git doesn't work in qemu. Assume
        # that somebody has already pulled the code on the host and mounted it
        # in.
        if not args.src_mounted:
            print('# BEGIN SUBSECTION: import repositories')
            # Get the repositories
            job.run(['curl', '-sk', args.repo_file_url, '-o', 'ros2.repos'])
            # Show the contents
            log("@{bf}==>@| Contents of `ros2.repos`:")
            with open('ros2.repos', 'r') as f:
                print(f.read())
            # Use the repository listing and vcstool to fetch repositories
            if not os.path.exists(args.sourcespace):
                os.makedirs(args.sourcespace)
            # OS X can't invoke a file which has a space in the shebang line
            # therefore invoking vcs explicitly through Python
            if args.do_venv:
                vcs_cmd = ['"%s"' % job.python, '"%s"' % os.path.join(venv_path, 'bin', 'vcs')]
            else:
                vcs_cmd = ['vcs']
            job.run(vcs_cmd + ['import', '"%s"' % args.sourcespace, '--input', 'ros2.repos'],
                    shell=True)
            print('# END SUBSECTION')

            if args.test_branch is not None:
                print('# BEGIN SUBSECTION: checkout custom branch')
                # Store current branch as well-known branch name for later rebasing
                info('Attempting to create a well known branch name for all the default branches')
                job.run(vcs_cmd + ['custom', '.', '--git', '--args', 'checkout', '-b', '__ci_default'])

                # Attempt to switch all the repositories to a given branch
                info("Attempting to switch all repositories to the '{0}' branch"
                     .format(args.test_branch))
                # use -b and --track to checkout correctly when file/folder with the same name exists
                vcs_custom_cmd = vcs_cmd + [
                    'custom', '.', '--args', 'checkout',
                    '-b', args.test_branch, '--track', 'origin/' + args.test_branch]
                ret = job.run(vcs_custom_cmd, exit_on_error=False)
                info("'{0}' returned exit code '{1}'", fargs=(" ".join(vcs_custom_cmd), ret))
                print()

                # Attempt to rebase all the repositories to the __ci_default branch
                info("Attempting to rebase all repositories to the '__ci_default' branch")
                vcs_custom_cmd = vcs_cmd + ['custom', '.', '--git', '--args', 'rebase', '__ci_default']
                ret = job.run(vcs_custom_cmd)
                info("'{0}' returned exit code '{1}'", fargs=(" ".join(vcs_custom_cmd), ret))
                print()
                print('# END SUBSECTION')

            print('# BEGIN SUBSECTION: repository hashes')
            # Show the latest commit log on each repository (includes the commit hash).
            job.run(vcs_cmd + ['log', '-l1', '"%s"' % args.sourcespace], shell=True)
            print('# END SUBSECTION')

            print('# BEGIN SUBSECTION: vcs export --exact')
            # Show the output of 'vcs export --exact`
            job.run(
                vcs_cmd + ['export', '--exact', '"%s"' % args.sourcespace], shell=True,
                # if a repo has been rebased against the default branch vcs can't detect the remote
                exit_on_error=False)
            print('# END SUBSECTION')

        if not args.connext:
            blacklisted_package_names += [
                'connext_cmake_module',
                'rmw_connext_cpp',
                'rmw_connext_dynamic_cpp',
                'rmw_connext_shared_cpp',
                'rosidl_typesupport_connext_c',
                'rosidl_typesupport_connext_cpp',
            ]
        if not args.fastrtps:
            blacklisted_package_names += [
                'fastcdr',
                'fastrtps',
                'fastrtps_cmake_module',
                'rmw_fastrtps_cpp',
            ]
        if not args.opensplice:
            blacklisted_package_names += [
                'opensplice_cmake_module',
                'rmw_opensplice_cpp',
                'rosidl_typesupport_opensplice_c',
                'rosidl_typesupport_opensplice_cpp',
            ]

        # Allow the batch job to push custom sourcing onto the run command
        job.setup_env()

        # create AMENT_IGNORE files in package folders which should not be used
        if blacklisted_package_names:
            print('# BEGIN SUBSECTION: ignored packages')
            print('Trying to ignore the following packages:')
            [print('- ' + name) for name in blacklisted_package_names]
            ament_py = get_ament_script(args.sourcespace)
            output = subprocess.check_output(
                [job.python, '-u', ament_py, 'list_packages', args.sourcespace])
            for line in output.decode().splitlines():
                package_name, package_path = line.split(' ', 1)
                if package_name in blacklisted_package_names:
                    marker_file = os.path.join(args.sourcespace, package_path, 'AMENT_IGNORE')
                    print('Create marker file: ' + marker_file)
                    with open(marker_file, 'w'):
                        pass
            print('# END SUBSECTION')

        return build_function(args, job)


def get_ament_script(basepath):
    return os.path.join(basepath, 'ament', 'ament_tools', 'scripts', 'ament.py')


if __name__ == '__main__':
    sys.exit(main())
