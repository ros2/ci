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
import importlib
import os
import platform
from shutil import which
import subprocess
import sys
import time

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
from .util import info
from .util import log
from .util import UnbufferedIO

# Enforce unbuffered output
sys.stdout = UnbufferedIO(sys.stdout)
sys.stderr = UnbufferedIO(sys.stderr)

PipPackage = collections.namedtuple('PipPackage', ['pkgname' ,'importname', 'version'])

pip_dependencies = [
    PipPackage('EmPy', 'em', '<4'),
    PipPackage('catkin_pkg', 'catkin_pkg', ''),
    PipPackage('cryptography', 'cryptography', '<=3.0'),
    PipPackage('coverage', 'coverage', ''),
    PipPackage('flake8', 'flake8', '<5.0.0'),
    PipPackage('flake8-blind-except', 'flake8_blind_except', '==0.1.1'),
    PipPackage('flake8-builtins', 'flake8_builtins', ''),
    PipPackage('flake8-class-newline', 'flake8_class_newline', ''),
    PipPackage('flake8-comprehensions', 'flake8_comprehensions', ''),
    PipPackage('flake8-deprecated', 'flake8_deprecated', ''),
    PipPackage('flake8-docstrings', 'flake8_docstrings', ''),
    PipPackage('flake8-import-order', 'flake8_import_order', ''),
    PipPackage('flake8-quotes', 'flake8_quotes', ''),
    PipPackage('importlib-metadata', 'importlib_metadata', ''),
    PipPackage('lark', 'lark', '==1.1.1'),
    PipPackage('mypy', 'mypy', '==0.931'),
    PipPackage('nose', 'nose', ''),
    PipPackage('osrf-pycommon', 'osrf_pycommon', ''),
    PipPackage('pathspec', 'pathspec', ''),
    PipPackage('pydocstyle', 'pydocstyle', ''),
    PipPackage('pyflakes', 'pyflakes', ''),
    PipPackage('pyparsing', 'pyparsing', '==2.4.7'),
    PipPackage('pytest', 'pytest', '==6.2.5'),
    PipPackage('pytest-cov', 'pytest_cov', ''),
    PipPackage('pytest-mock', 'pytest_mock', ''),
    PipPackage('pytest-repeat', 'pytest_repeat', ''),
    PipPackage('pytest-rerunfailures', 'pytest_rerunfailures', ''),
    PipPackage('pytest-runner', 'ptr', ''),
    PipPackage('pytest-timeout', 'pytest_timeout', '==2.1.0'),
    PipPackage('pyyaml', 'yaml', ''),
    PipPackage('setuptools', 'setuptools', '==59.6.0'),
    PipPackage('vcstool', 'vcstool', ''),
    PipPackage('yamllint', 'yamllint', ''),
]

colcon_packages = [
    PipPackage('colcon-core', 'colcon_core', ''),
    PipPackage('colcon-defaults', 'colcon_defaults', ''),
    PipPackage('colcon-library-path', 'colcon_library_path', ''),
    PipPackage('colcon-metadata', 'colcon_metadata', ''),
    PipPackage('colcon-mixin', 'colcon_mixin', ''),
    PipPackage('colcon-output', 'colcon_output', ''),
    PipPackage('colcon-package-information', 'colcon_package_information', ''),
    PipPackage('colcon-package-selection', 'colcon_package_selection', ''),
    PipPackage('colcon-parallel-executor', 'colcon_parallel_executor', ''),
    PipPackage('colcon-pkg-config', 'colcon_pkg_config', ''),
    PipPackage('colcon-powershell', 'colcon_powershell', ''),
    PipPackage('colcon-python-setup-py', 'colcon_python_setup_py', ''),
    PipPackage('colcon-recursive-crawl', 'colcon_recursive_crawl', ''),
    PipPackage('colcon-test-result', 'colcon_test_result', ''),
    PipPackage('colcon-cmake', 'colcon_cmake', ''),
    PipPackage('colcon-ros', 'colcon_ros', ''),
    PipPackage('colcon-ros-domain-id-coordinator', 'colcon_ros_domain_id_coordinator', ''),
]
if sys.platform != 'win32':
    colcon_packages += [
        PipPackage('colcon-bash', 'colcon_bash', ''),
        PipPackage('colcon-zsh', 'colcon_zsh', ''),
    ]

gcov_flags = '--coverage'

colcon_space_defaults = {
    'sourcespace': 'src',
    'buildspace': 'build',
    'installspace': 'install',
}

def main(sysargv=None):
    args = get_args(sysargv=sysargv)
    blacklisted_package_names = []
    if not args.packaging:
        build_function = build_and_test
    else:
        build_function = build_and_test_and_package
        if sys.platform == 'win32':
            blacklisted_package_names += [
                'pendulum_control',
                'rttest',
                'tlsf',
                'tlsf_cpp',
            ]

    # There are no Windows debug packages available for PyQt5 and PySide2, so
    # python_qt_bindings can't be imported to run or test rqt_graph or
    # rqt_py_common.
    if sys.platform == 'win32' and args.cmake_build_type == 'Debug':
        blacklisted_package_names.append('rqt_graph')
        blacklisted_package_names.append('rqt_py_common')
        blacklisted_package_names.append('rqt_reconfigure')

    # TODO(wjwwood): remove this when a better solution is found, as
    #   this is just a work around for https://github.com/ros2/build_cop/issues/161
    # If on Windows, kill any still running `colcon` processes to avoid
    # problems when trying to delete files from pip or the workspace during
    # this job.
    if sys.platform == 'win32':
        os.system('taskkill /f /im colcon.exe')
        time.sleep(2)  # wait a bit to avoid a race

    return run(args, build_function, blacklisted_package_names=blacklisted_package_names)


def get_args(sysargv=None):
    parser = argparse.ArgumentParser(
        description="Builds the ROS 2 repositories as a single batch job")

    # TODO(clalancette): Python 3.6 on RHEL-8 doesn't have the 'extend' action
    # available in argparse.  If we are on a Python version earlier than 3.8
    # (where 'extend' was added), register it ourselves.
    if sys.version_info < (3, 8):
        class ExtendAction(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                items = getattr(namespace, self.dest) or []
                items.extend(values)
                setattr(namespace, self.dest, items)

        parser.register('action', 'extend', ExtendAction)

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
        '--white-space-in', nargs='*', default=[],
        choices=['sourcespace', 'buildspace', 'installspace', 'workspace'],
        help="which folder structures in which white space should be added")
    parser.add_argument(
        '--os', default=None, choices=['linux', 'windows'])
    parser.add_argument(
        '--ignore-rmw', nargs='*', default=[], action='extend',
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
        '--ros-distro', required=True,
        help="The ROS distribution being built")
    parser.add_argument(
        '--colcon-mixin-url', default=None,
        help='A mixin index url to be included by colcon')
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
        '--compile-with-clang', default=False, action='store_true',
        help="compile with clang instead of gcc")
    parser.add_argument(
        '--coverage', default=False, action='store_true',
        help="enable collection of coverage statistics")
    parser.add_argument(
        '--workspace-path', default=None,
        help="base path of the workspace")
    parser.add_argument(
        '--python-interpreter', default=None,
        help='pass different Python interpreter')
    parser.add_argument(
        '--visual-studio-version', default=None, required=(os.name == 'nt'),
        help='select the Visual Studio version')
    parser.add_argument(
        '--source-space', dest='sourcespace',
        help='source directory path')
    parser.add_argument(
        '--build-space', dest='buildspace',
        help='build directory path')
    parser.add_argument(
        '--install-space', dest='installspace',
        help='install directory path')

    argv = sysargv[1:] if sysargv is not None else sys.argv[1:]
    argv, build_args = extract_argument_group(argv, '--build-args')
    if '--test-args' in argv:
        argv, test_args = extract_argument_group(argv, '--test-args')
    else:
        build_args, test_args = extract_argument_group(build_args, '--test-args')
    args = parser.parse_args(argv)
    args.build_args = build_args
    args.test_args = test_args

    for name in ('sourcespace', 'buildspace', 'installspace'):
        space_directory = getattr(args, name)
        if name in args.white_space_in and space_directory is not None:
            raise Exception('Argument {} and "--white-space-in" cannot both be used'.format(name))
        elif space_directory is None:
            space_directory = colcon_space_defaults[name]
            if name in args.white_space_in:
                space_directory += ' space'
            setattr(args, name, space_directory)
    return args

def get_lcov_version():
    try:
        result = subprocess.run(['lcov', '--version'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True, check=True)
        version_output = result.stdout.strip().replace('lcov: LCOV version ', '')
        return version_output
    except subprocess.CalledProcessError as e:
        return ""

def process_coverage(args, job):
    print('# BEGIN SUBSECTION: coverage analysis')
    # Capture all gdca/gcno files (all them inside buildspace)
    coverage_file = os.path.join(args.buildspace, 'coverage.info')

    version = get_lcov_version()
    lcov_arguments = []
    if version.startswith('2'):
        lcov_arguments = ['--ignore-errors', 'inconsistent,inconsistent',
                          '--ignore-errors', 'mismatch,mismatch',
                          '--ignore-errors', 'negative,negative',
                          '--ignore-errors', 'unused,unused',
                          '--ignore-errors', 'empty,empty']

    cmd = [
        'lcov',
        '--capture',
        '--directory', args.buildspace,
        '--output', str(coverage_file)] + lcov_arguments
    print(cmd)
    subprocess.run(cmd, check=True)
    # Filter out system coverage and test code
    cmd = [
        'lcov',
        '--remove', coverage_file,
        '--output', coverage_file,
        '/usr/*',  # no system files in reports
        '/home/rosbuild/*',  # remove rti_connext installed in rosbuild
        '*/test/*',
        '*/tests/*',
        '*gtest_vendor*',
        '*gmock_vendor*'] + lcov_arguments
    print(cmd)
    subprocess.run(cmd, check=True)
    # Transform results to the cobertura format
    outfile = os.path.join(args.buildspace, 'coverage.xml')
    print('Writing coverage.xml report at path {}'.format(outfile))
    cmd = ['lcov_cobertura', coverage_file, '--output', outfile]
    subprocess.run(cmd, check=True)

    print('# END SUBSECTION')
    return 0


def build_and_test(args, job, colcon_script):
    compile_with_clang = args.compile_with_clang and args.os == 'linux'

    print('# BEGIN SUBSECTION: build')
    cmd = [
        colcon_script, 'build',
        '--base-paths', '"%s"' % args.sourcespace,
        '--build-base', '"%s"' % args.buildspace,
        '--install-base', '"%s"' % args.installspace,
    ] + (['--merge-install'] if not args.isolated else []) + \
        args.build_args

    cmake_args = ['-DBUILD_TESTING=ON', '--no-warn-unused-cli']
    if args.cmake_build_type:
        cmake_args.append(
            '-DCMAKE_BUILD_TYPE=' + args.cmake_build_type)
    if compile_with_clang:
        cmake_args.extend(
            ['-DCMAKE_C_COMPILER=/usr/bin/clang', '-DCMAKE_CXX_COMPILER=/usr/bin/clang++'])
    if '--cmake-args' in cmd:
        index = cmd.index('--cmake-args')
        cmd[index + 1:index + 1] = cmake_args
    else:
        cmd.append('--cmake-args')
        cmd.extend(cmake_args)

    if args.coverage:
        if args.os == 'linux':
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

    test_cmd = [
        colcon_script, 'test',
        '--base-paths', '"%s"' % args.sourcespace,
        '--build-base', '"%s"' % args.buildspace,
        '--install-base', '"%s"' % args.installspace,
    ]
    if not args.isolated:
        test_cmd.append('--merge-install')
    if args.coverage:
        test_cmd.append('--pytest-with-coverage')
    test_cmd.extend(args.test_args)

    ret_test = job.run(test_cmd, exit_on_error=False, shell=True)
    info("colcon test returned: '{0}'".format(ret_test))
    print('# END SUBSECTION')
    if ret_test:
        return ret_test

    print('# BEGIN SUBSECTION: test-result --all')
    # Collect the test results
    ret_test_results = job.run(
        [colcon_script, 'test-result', '--test-result-base', '"%s"' % args.buildspace, '--all'],
        exit_on_error=False, shell=True
    )
    info("colcon test-result returned: '{0}'".format(ret_test_results))
    print('# END SUBSECTION')

    print('# BEGIN SUBSECTION: test-result')
    # Collect the test results
    ret_test_results = job.run(
        [colcon_script, 'test-result', '--test-result-base', '"%s"' % args.buildspace],
        exit_on_error=False, shell=True
    )
    info("colcon test-result returned: '{0}'".format(ret_test_results))
    print('# END SUBSECTION')
    if args.coverage and args.os == 'linux':
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

    args.workspace = 'work space' if 'workspace' in args.white_space_in else 'ws'

    platform_name = platform.platform().lower()
    if args.os == 'linux' or platform_name.startswith('linux'):
        args.os = 'linux'
        from .linux_batch import LinuxBatchJob
        job = LinuxBatchJob(args)
    elif args.os == 'windows' or platform_name.startswith('windows'):
        args.os = 'windows'
        from .windows_batch import WindowsBatchJob
        job = WindowsBatchJob(args)

    # Set the TERM env variable to coerce the output of Make to be colored.
    os.environ['TERM'] = os.environ.get('TERM', 'xterm-256color')
    if args.os == 'windows':
        # Set the ConEmuANSI env variable to trick some programs (vcs) into
        # printing ANSI color codes on Windows.
        os.environ['ConEmuANSI'] = 'ON'

    # Set the appropriate GIT_* env variables in case vcs needs to merge branches
    os.environ['GIT_AUTHOR_EMAIL'] = 'nobody@osrfoundation.org'
    os.environ['GIT_AUTHOR_NAME'] = 'nobody'
    os.environ['GIT_COMMITTER_EMAIL'] = 'nobody@osrfoundation.org'
    os.environ['GIT_COMMITTER_NAME'] = 'nobody'

    info("Using workspace: @!{0}", fargs=(args.workspace,))
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

    # Now inside of the workspace...
    with change_directory(args.workspace):
        def need_package_from_pipy(pkg_name):
            try:
                importlib.import_module(pkg_name)
            except ModuleNotFoundError:
                return True

            return False

        print('# BEGIN SUBSECTION: install Python packages')
        # Print setuptools version
        job.run(['"%s"' % job.python, '-c', '"import setuptools; print(setuptools.__version__)"'],
                shell=True)

        # Print the pip version
        job.run(['"%s"' % job.python, '-m', 'pip', '--version'], shell=True)

        # Install pip dependencies
        pip_packages = []
        constraints = []

        potential_pip_packages = pip_dependencies
        if not args.colcon_branch:
            potential_pip_packages += colcon_packages

        # We prefer to get packages from the distribution if they are already installed.
        # If not, we add to the list to install from pip.
        for pkgname, importname, version in pip_dependencies:
            if need_package_from_pipy(importname):
                pip_packages.append(pkgname)
            # Even if we don't need to install the package, we still add the constraints
            # (if they exist) so that other package installations will respect these.
            if version:
                constraints.append(f'{pkgname}{version}')

        if sys.platform == 'win32':
            # Install fork of pyreadline containing fix for deprecation warnings
            # TODO(jacobperron): Until upstream issue is resolved https://github.com/pyreadline/pyreadline/issues/65
            pip_packages += ['git+https://github.com/osrf/pyreadline']

            # Setuptools > 61 somehow have broken Windows Debug.  Pin it to 59.6.0 here which
            # matches Ubuntu Jammy, and wait until upstream setuptools settles down.
            pip_packages += ["setuptools==59.6.0"]

            if args.cmake_build_type == 'Debug':
                pip_packages += [
                    'https://github.com/ros2/ros2/releases/download/cryptography-archives/cffi-1.14.0-cp38-cp38d-win_amd64.whl',  # required by cryptography
                    'https://github.com/ros2/ros2/releases/download/cryptography-archives/cryptography-2.9.2-cp38-cp38d-win_amd64.whl',
                    'https://github.com/ros2/ros2/releases/download/lxml-archives/lxml-4.5.1-cp38-cp38d-win_amd64.whl',
                    'https://github.com/ros2/ros2/releases/download/numpy-archives/numpy-1.18.4-cp38-cp38d-win_amd64.whl',
                    'https://github.com/ros2/ros2/releases/download/psutil-archives/psutil-5.9.5-cp38-cp38d-win_amd64.whl',
                ]
                if args.ros_distro in ('humble', 'iron'):
                    pip_packages.append('https://github.com/ros2/ros2/releases/download/netifaces-archives/netifaces-0.10.9-cp38-cp38d-win_amd64.whl')
            else:
                pip_packages += ['cryptography', 'lxml', 'numpy']
                if args.ros_distro in ('humble', 'iron'):
                    pip_packages.append('netifaces')
        if sys.platform == 'win32':
            # to ensure that the build type specific package is installed
            job.run(
                ['"%s"' % job.python, '-m', 'pip', 'uninstall', '-y'] +
                ['cryptography', 'lxml', 'numpy'], shell=True)

        if pip_packages:
            print('Using constraints:')
            print('\n'.join(constraints))
            with open('constraints.txt', 'w') as outfp:
                outfp.write('\n'.join(constraints) + '\n')

            pip_cmd = ['"%s"' % job.python, '-m', 'pip', 'install', '-c', 'constraints.txt', '-U']
            if sys.platform == 'win32':
                # Force reinstall so all dependencies are in virtual environment
                # On Windows since we switch between the debug and non-debug
                # interpreter all packages need to be reinstalled too
                pip_cmd.append('--force-reinstall')

            job.run(
                pip_cmd + pip_packages,
                shell=True)

        vcs_cmd = ['vcs']

        if args.colcon_branch:
            # create .repos file for colcon repositories
            os.makedirs('colcon', exist_ok=True)
            with open('colcon/colcon.repos', 'w') as h:
                h.write('repositories:\n')
                for pkgname, importname, version in colcon_packages:
                    h.write('  %s:\n' % pkgname)
                    h.write('    type: git\n')
                    h.write(
                        '    url: https://github.com/colcon/%s.git\n' % pkgname)
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
                ['colcon/%s' % pkgname for pkgname, importname, version in colcon_packages],
                shell=True)

        colcon_script = which('colcon')

        # Show what pip has
        job.run(['"%s"' % job.python, '-m', 'pip', 'freeze', '--all'], shell=True)
        print('# END SUBSECTION')

        # Fetch colcon mixins
        if args.colcon_mixin_url:
            true_cmd = 'VER>NUL' if sys.platform == 'win32' else 'true'
            job.run([colcon_script, 'mixin', 'remove', 'default', '||', true_cmd], shell=True)
            job.run([colcon_script, 'mixin', 'add', 'default', args.colcon_mixin_url], shell=True)
            job.run([colcon_script, 'mixin', 'update', 'default'], shell=True)

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
        if 'rmw_connextdds' in args.ignore_rmw:
            blacklisted_package_names += [
                'rti_connext_dds_cmake_module',
                'rmw_connextdds_common',
                'rmw_connextdds',
                'rmw_connextddsmicro',
            ]
        if 'rmw_cyclonedds_cpp' in args.ignore_rmw:
            blacklisted_package_names += [
                'cyclonedds',
                'cyclonedds_cmake_module',
                'rmw_cyclonedds_cpp',
            ]
        if 'rmw_fastrtps_cpp' in args.ignore_rmw:
            blacklisted_package_names += [
                'rmw_fastrtps_cpp',
            ]
        if 'rmw_fastrtps_cpp' in args.ignore_rmw and 'rmw_connextdds' in args.ignore_rmw:
            blacklisted_package_names += [
                'rosidl_typesupport_fastrtps_c',
                'rosidl_typesupport_fastrtps_cpp',
            ]
        if 'rmw_fastrtps_dynamic_cpp' in args.ignore_rmw:
            blacklisted_package_names += [
                'rmw_fastrtps_dynamic_cpp',
            ]
        if ('rmw_fastrtps_cpp' in args.ignore_rmw and
            'rmw_fastrtps_dynamic_cpp' in args.ignore_rmw and
            # TODO(asorbini) Ideally `rmw_connextdds` would only depend on `fastcdr`
            # via `rosidl_typesupport_fastrtps_c[pp]`, but they depend on `fastrtps`.
            'rmw_connextdds' in args.ignore_rmw):
            blacklisted_package_names += [
                'fastrtps',
                'fastrtps_cmake_module',
                'rosidl_dynamic_typesupport_fastrtps',
            ]
        if 'rmw_fastrtps_cpp' in args.ignore_rmw and 'rmw_fastrtps_dynamic_cpp' in args.ignore_rmw:
            blacklisted_package_names += [
                'rmw_fastrtps_shared_cpp',
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
                    marker_file = os.path.join(package_path, 'COLCON_IGNORE')
                    print('Create marker file: ' + marker_file)
                    with open(marker_file, 'w'):
                        pass
            print('# END SUBSECTION')

        rc = build_function(args, job, colcon_script)

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
