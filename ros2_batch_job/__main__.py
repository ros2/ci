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
from shutil import which
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
from osrf_pycommon.terminal_color import sanitize

from .packaging import build_and_test_and_package
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
    'catkin_pkg',
    'flake8',
    'flake8-blind-except',
    'flake8-builtins',
    'flake8-class-newline',
    'flake8-comprehensions',
    'flake8-deprecated',
    'flake8-docstrings',
    'flake8-import-order',
    'flake8-quotes',
    'git+https://github.com/lark-parser/lark.git@0.7d',
    'mock',
    'nose',
    'pep8',
    'pydocstyle',
    'pyflakes',
    'pyparsing',
    'pytest',
    'pytest-cov',
    'pytest-repeat',
    'pytest-rerunfailures',
    'pytest-runner',
    'pyyaml',
    'vcstool',
]
colcon_packages = [
    'colcon-core',
    'colcon-defaults',
    'colcon-library-path',
    'colcon-metadata',
    'colcon-output',
    'colcon-package-information',
    'colcon-package-selection',
    'colcon-parallel-executor',
    'colcon-powershell',
    'colcon-python-setup-py',
    'colcon-recursive-crawl',
    'colcon-test-result',
    'colcon-cmake',
    'colcon-ros',
]
if sys.platform != 'win32':
    colcon_packages += [
        'colcon-bash',
        'colcon-zsh',
    ]

gcov_flags = " -fprofile-arcs -ftest-coverage "

def main(sysargv=None):
    args = get_args(sysargv=sysargv)
    blacklisted_package_names = []
    if not args.packaging:
        build_function = build_and_test
        blacklisted_package_names += [
            'actionlib_msgs',
            'common_interfaces',
            'cv_bridge',
            'opencv_tests',
            'ros1_bridge',
            'shape_msgs',
            'stereo_msgs',
            'trajectory_msgs',
            'vision_opencv',
        ]
    else:
        build_function = build_and_test_and_package
        if sys.platform in ('darwin', 'win32'):
            blacklisted_package_names += [
                'pendulum_control',
                'ros1_bridge',
                'rttest',
                'tlsf',
                'tlsf_cpp',
            ]
    if sys.platform.lower().startswith('linux') and platform.linux_distribution()[2] == 'xenial':
        blacklisted_package_names += [
            'qt_dotgraph',
        ]
    return run(args, build_function, blacklisted_package_names=blacklisted_package_names)


def get_args(sysargv=None):
    parser = argparse.ArgumentParser(
        description="Builds the ROS2 repositories as a single batch job")
    parser.add_argument(
        '--packaging', default=False, action='store_true',
        help='create an archive of the install space')
    parser.add_argument(
        '--repo-file-url', required=True,
        help="url of the ros2.repos file to fetch and use for the basis of the batch job")
    parser.add_argument(
        '--supplemental-repo-file-url', default=None,
        help="url of a .repos file to fetch and merge with the ros2.repos file")
    parser.add_argument(
        '--test-branch', default=None,
        help="branch to attempt to checkout before doing batch job")
    parser.add_argument(
        '--colcon-branch', default=None,
        help='Use a specific branch of the colcon repositories, if the branch '
             "doesn't exist fall back to the default branch (default: latest "
             'release)')
    parser.add_argument(
        '--white-space-in', nargs='*', default=None,
        choices=['sourcespace', 'buildspace', 'installspace', 'workspace'],
        help="which folder structures in which white space should be added")
    parser.add_argument(
        '--do-venv', default=False, action='store_true',
        help="create and use a virtual env in the build process")
    parser.add_argument(
        '--os', default=None, choices=['linux', 'osx', 'windows'])
    parser.add_argument(
        '--ignore-rmw', nargs='*', default=[],
        help='ignore the passed RMW implementations as well as supporting packages')
    parser.add_argument(
        '--connext-debs', default=False, action='store_true',
        help="use Debian packages for Connext instead of binaries off the RTI website (Linux only)")
    parser.add_argument(
        '--isolated', default=False, action='store_true',
        help="build and install each package a separate folders")
    parser.add_argument(
        '--force-ansi-color', default=False, action='store_true',
        help="forces this program to output ansi color")
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
        '--build-args', default=None,
        help="arguments passed to the 'build' verb")
    parser.add_argument(
        '--test-args', default=None,
        help="arguments passed to the 'test' verb")
    parser.add_argument(
        '--src-mounted', default=False, action='store_true',
        help="src directory is already mounted into the workspace")
    parser.add_argument(
        '--coverage', default=False, action='store_true',
        help="enable collection of coverage statistics")
    parser.add_argument(
        '--workspace-path', default=None,
        help="base path of the workspace")
    parser.add_argument(
        '--python-interpreter', default=None,
        help='pass different Python interpreter')

    argv = sysargv[1:] if sysargv is not None else sys.argv[1:]
    argv, build_args = extract_argument_group(argv, '--build-args')
    if '--test-args' in argv:
        argv, test_args = extract_argument_group(argv, '--test-args')
    else:
        build_args, test_args = extract_argument_group(build_args, '--test-args')
    args = parser.parse_args(argv)
    args.build_args = build_args
    args.test_args = test_args
    return args


def process_coverage(args, job):
    print('# BEGIN SUBSECTION: coverage analysis')
    # Collect all .gcda files in args.workspace
    output = subprocess.check_output(
        [args.colcon_script, 'list', '--base-paths', args.sourcespace])
    for line in output.decode().splitlines():
        package_name, package_path, _ = line.split('\t', 2)
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
    coverage = args.coverage and args.os == 'linux'

    print('# BEGIN SUBSECTION: build')
    cmd = [
        args.colcon_script, 'build',
        '--base-paths', '"%s"' % args.sourcespace,
        '--build-base', '"%s"' % args.buildspace,
        '--install-base', '"%s"' % args.installspace,
    ] + (['--merge-install'] if not args.isolated else []) + \
        args.build_args

    cmake_args = ['-DBUILD_TESTING=ON', '--no-warn-unused-cli']
    if args.cmake_build_type:
        cmake_args.append(
            '-DCMAKE_BUILD_TYPE=' + args.cmake_build_type)
    if '--cmake-args' in cmd:
        index = cmd.index('--cmake-args')
        cmd[index + 1:index + 1] = cmake_args
    else:
        cmd.append('--cmake-args')
        cmd.extend(cmake_args)

    if coverage:
        ament_cmake_args = [
            '-DCMAKE_CXX_FLAGS="${CMAKE_CXX_FLAGS} ' + gcov_flags + '"',
            '-DCMAKE_C_FLAGS="${CMAKE_C_FLAGS} ' + gcov_flags + '"']
        if '--ament-cmake-args' in cmd:
            index = cmd.index('--ament-cmake-args')
            cmd[index + 1:index + 1] = ament_cmake_args
        else:
            cmd.append('--ament-cmake-args')
            cmd.extend(ament_cmake_args)

    ret_build = job.run(cmd, shell=True)
    info("colcon build returned: '{0}'".format(ret_build))
    print('# END SUBSECTION')
    if ret_build:
        return ret_build

    print('# BEGIN SUBSECTION: test')
    ret_test = job.run([
        args.colcon_script, 'test',
        '--base-paths', '"%s"' % args.sourcespace,
        '--build-base', '"%s"' % args.buildspace,
        '--install-base', '"%s"' % args.installspace,
    ] + (['--merge-install'] if not args.isolated else []) + args.test_args,
        exit_on_error=False, shell=True)
    info("colcon test returned: '{0}'".format(ret_test))
    print('# END SUBSECTION')
    if ret_test:
        return ret_test

    print('# BEGIN SUBSECTION: test-result --all')
    # Collect the test results
    ret_test_results = job.run(
        [args.colcon_script, 'test-result', '--test-result-base', '"%s"' % args.buildspace, '--all'],
        exit_on_error=False, shell=True
    )
    info("colcon test-result returned: '{0}'".format(ret_test_results))
    print('# END SUBSECTION')

    print('# BEGIN SUBSECTION: test-result')
    # Collect the test results
    ret_test_results = job.run(
        [args.colcon_script, 'test-result', '--test-result-base', '"%s"' % args.buildspace],
        exit_on_error=False, shell=True
    )
    info("colcon test-result returned: '{0}'".format(ret_test_results))
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
        info(sanitize("  - {0}={1}".format(arg, getattr(args, arg))))

    job = None

    args.white_space_in = args.white_space_in or []
    args.workspace = 'work space' if 'workspace' in args.white_space_in else 'ws'
    args.sourcespace = 'source space' if 'sourcespace' in args.white_space_in else 'src'
    args.buildspace = 'build space' if 'buildspace' in args.white_space_in else 'build'
    args.installspace = 'install space' if 'installspace' in args.white_space_in else 'install'

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

    # ROS_DOMAIN_ID must be unique to each CI machine on a network to avoid crosstalk
    if 'ROS_DOMAIN_ID' not in os.environ:
        raise KeyError('ROS_DOMAIN_ID environment variable must be set')

    # Check the env
    job.show_env()

    colcon_script = None
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
        job.run([
            sys.executable, '-m', 'virtualenv', '--system-site-packages',
            '-p', sys.executable, venv_subfolder])
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
        pip_packages = list(pip_dependencies)
        if not args.colcon_branch:
            pip_packages += colcon_packages
        if sys.platform == 'win32':
            job.run(
                ['"%s"' % job.python, '-m', 'pip', 'uninstall', '-y'] +
                colcon_packages, shell=True)

        pip_cmd = ['"%s"' % job.python, '-m', 'pip', 'install', '-U']
        if args.do_venv:
            # Force reinstall so all dependencies are in virtual environment
            pip_cmd.append('--force-reinstall')
        job.run(
             pip_cmd + pip_packages,
            shell=True)

        # OS X can't invoke a file which has a space in the shebang line
        # therefore invoking vcs explicitly through Python
        if args.do_venv:
            vcs_cmd = [
                '"%s"' % job.python,
                '"%s"' % os.path.join(venv_path, 'bin', 'vcs')]
        else:
            vcs_cmd = ['vcs']

        if args.colcon_branch:
            # create .repos file for colcon repositories
            os.makedirs('colcon', exist_ok=True)
            with open('colcon/colcon.repos', 'w') as h:
                h.write('repositories:\n')
                for name in colcon_packages:
                    h.write('  %s:\n' % name)
                    h.write('    type: git\n')
                    h.write(
                        '    url: https://github.com/colcon/%s.git\n' % name)
            # clone default branches
            job.run(
                vcs_cmd + [
                    'import', 'colcon', '--force', '--retry', '5', '--input',
                    'colcon/colcon.repos'],
                shell=True)
            # use -b and --track to checkout correctly when file/folder
            # with the same name exists
            job.run(
                vcs_cmd + [
                    'custom', 'colcon', '--args', 'checkout',
                    '-b', args.colcon_branch,
                    '--track', 'origin/' + args.colcon_branch],
                exit_on_error=False)
            # install colcon packages from local working copies
            job.run(
                ['"%s"' % job.python, '-m', 'pip', 'install', '-U'] +
                ['colcon/%s' % name for name in colcon_packages],
                shell=True)

        if sys.platform != 'win32':
            colcon_script = os.path.join(venv_path, 'bin', 'colcon')
        else:
            colcon_script = which('colcon')
        args.colcon_script = colcon_script
        # Show what pip has
        job.run(['"%s"' % job.python, '-m', 'pip', 'freeze'], shell=True)
        print('# END SUBSECTION')

        # Skip git operations on arm because git doesn't work in qemu. Assume
        # that somebody has already pulled the code on the host and mounted it
        # in.
        if not args.src_mounted:
            print('# BEGIN SUBSECTION: import repositories')
            repos_file_urls = [args.repo_file_url]
            if args.supplemental_repo_file_url is not None:
                repos_file_urls.append(args.supplemental_repo_file_url)
            repos_filenames = []
            for index, repos_file_url in enumerate(repos_file_urls):
                repos_filename = '{0:02d}-{1}'.format(index, os.path.basename(repos_file_url))
                _fetch_repos_file(repos_file_url, repos_filename, job)
                repos_filenames.append(repos_filename)
            # Use the repository listing and vcstool to fetch repositories
            if not os.path.exists(args.sourcespace):
                os.makedirs(args.sourcespace)
            for filename in repos_filenames:
                job.run(vcs_cmd + ['import', '"%s"' % args.sourcespace, '--force', '--retry', '5',
                                   '--input', filename], shell=True)
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

                # Attempt to merge the __ci_default branch into the branch.
                # This is to ensure that the changes on the branch still work
                # when applied to the latest version of the default branch.
                info("Attempting to merge all repositories to the '__ci_default' branch")
                vcs_custom_cmd = vcs_cmd + ['custom', '.', '--git', '--args', 'merge', '__ci_default']
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

        # blacklist rmw packages as well as their dependencies where possible
        if 'rmw_connext_cpp' in args.ignore_rmw:
            blacklisted_package_names += [
                'rmw_connext_cpp',
                'rosidl_typesupport_connext_c',
                'rosidl_typesupport_connext_cpp',
            ]
        if 'rmw_connext_dynamic_cpp' in args.ignore_rmw:
            blacklisted_package_names += [
                'rmw_connext_dynamic_cpp',
            ]
        if 'rmw_connext_cpp' in args.ignore_rmw:  # and 'rmw_connext_dynamic_cpp' in args.ignore_rmw:
            blacklisted_package_names += [
                'connext_cmake_module',
                'rmw_connext_shared_cpp',
            ]
        if 'rmw_fastrtps_cpp' in args.ignore_rmw:
            blacklisted_package_names += [
                'rmw_fastrtps_cpp',
                'rosidl_typesupport_fastrtps_c',
                'rosidl_typesupport_fastrtps_cpp',
            ]
        if 'rmw_fastrtps_dynamic_cpp' in args.ignore_rmw:
            blacklisted_package_names += [
                'rmw_fastrtps_dynamic_cpp',
            ]
        if 'rmw_fastrtps_cpp' in args.ignore_rmw and 'rmw_fastrtps_dynamic_cpp' in args.ignore_rmw:
            blacklisted_package_names += [
                'fastcdr',
                'fastrtps',
                'fastrtps_cmake_module',
                'rmw_fastrtps_shared_cpp',
            ]
        if 'rmw_opensplice_cpp' in args.ignore_rmw:
            blacklisted_package_names += [
                'opensplice_cmake_module',
                'rmw_opensplice_cpp',
                'rosidl_typesupport_opensplice_c',
                'rosidl_typesupport_opensplice_cpp',
            ]

        # Allow the batch job to push custom sourcing onto the run command
        job.setup_env()

        # create COLCON_IGNORE files in package folders which should not be used
        if blacklisted_package_names:
            print('# BEGIN SUBSECTION: ignored packages')
            print('Trying to ignore the following packages:')
            [print('- ' + name) for name in blacklisted_package_names]
            output = subprocess.check_output(
                [colcon_script, 'list', '--base-paths', args.sourcespace])
            for line in output.decode().splitlines():
                package_name, package_path, _ = line.split('\t', 2)
                if package_name in blacklisted_package_names:
                    marker_file = os.path.join(args.sourcespace, package_path, 'COLCON_IGNORE')
                    print('Create marker file: ' + marker_file)
                    with open(marker_file, 'w'):
                        pass
            print('# END SUBSECTION')

        rc = build_function(args, job)

    job.post()
    return rc


def _fetch_repos_file(url, filename, job):
    """Use curl to fetch a repos file and display the contents."""

    job.run(['curl', '-skL', url, '-o', filename])
    log("@{bf}==>@| Contents of `%s`:" % filename)
    with open(filename, 'r') as f:
        print(f.read())

if __name__ == '__main__':
    sys.exit(main())
