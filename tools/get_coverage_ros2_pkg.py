#!/usr/bin/env python3

import argparse
import os
import requests
import subprocess
import sys
import tempfile

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('jenkins_coverage_build', help='URL of a ci.ro2s.org build using coverage (i.e https://ci.ros2.org/job/ci_linux_coverage/182)')
    parser.add_argument('ros_package', help='ROS package name to get the coverage rate from (i.e: rcutils)')
    args = parser.parse_args()

    input_url = args.jenkins_coverage_build
    input_pkg = args.ros_package

    # Compare if a list is inside other list in order
    # From here: https://stackoverflow.com/a/20789669
    def is_slice_in_list(s, l):
        len_s = len(s)
        return any(s == l[i:len_s + i] for i in range(len(l) - len_s + 1))

    def create_colcon_workspace():
        ros2_ws_path = os.path.join(tempfile.gettempdir(), 'ros2_coverage_tool')
        ros2_repos_path = os.path.join(ros2_ws_path, 'ros2.repos')
        # create the workspace if it does not exist
        if not os.path.isdir(ros2_ws_path):
            os.mkdir(ros2_ws_path)
            ros2_repos = requests.get('https://raw.githubusercontent.com/ros2/ros2/master/ros2.repos')
            if ros2_repos.status_code != requests.codes.ok:
                print('Failed to download ros2.repos file', file=sys.stderr)
                sys.exit(-1)
            with open(ros2_repos_path, 'wb') as file:
                file.write(ros2_repos.content)

        cmd = ['vcs', 'import', ros2_ws_path, '--shallow', '--retry', '5', '--input', ros2_repos_path]
        try:
            print('Getting ros2.repos sources to get packages source paths. Please wait')
            subprocess.check_output(cmd)
        except subprocess.CalledProcessError as e:
            print(e.output, file=sys.stderr)
            sys.exit(-1)

        return ros2_ws_path

    def get_src_path(package_name, colcon_ws):
        cmd = ['colcon', 'list', '--paths-only', '--base-paths', colcon_ws, '--packages-select', package_name]
        try:
            path = subprocess.check_output(cmd).decode('ascii').strip()
        except subprocess.CalledProcessError as e:
            print(e.output, file=sys.stderr)
            sys.exit(-1)
        if not path:
            print('Package not found: ' + input_pkg, file=sys.stderr)
            sys.exit(-1)
        return path

    r = requests.get(url=input_url + '/cobertura/api/json?depth=3')
    if r.status_code != 200:
        print('Wrong input URL ' + input_url, file=sys.stderr)
        sys.exit(-1)

    ros2_ws_path = create_colcon_workspace()
# Get relative path in ROS workspace to real the package source code
    ros_package_path_in_ws = get_src_path(input_pkg, ros2_ws_path)
    input_pkg_rel_path = os.path.relpath(ros_package_path_in_ws, ros2_ws_path).split(os.path.sep)

    coverage_entries = r.json()['results']['children']
    total_lines_under_testing = 0
    total_lines_tested = 0

    for e in coverage_entries:
        if e['name'] == '.':
            continue
        # e has children, elements or name
        entry_name = e['name'].replace("'", "")
        lines_coverage = e['elements'][2]
        assert lines_coverage['name'] == 'Lines', 'Error expecting lines of coverage'
        name_parts = entry_name.split('.')

        if len(name_parts) == 1:
            package_under_cov = name_parts[0]
        elif name_parts[0].startswith('test'):
            # no interest in test code
            continue
        elif name_parts[0].startswith('install'):
            # integration/system testing, out by now
            continue
        elif name_parts[0].startswith('build'):
            # in build the first part is always the ROS package name
            package_under_cov = name_parts[1]
        elif is_slice_in_list(input_pkg_rel_path, name_parts):
            # source code: check if coverage entry contains exactly the source path
            package_under_cov = input_pkg
        else:
            package_under_cov = 'NOT-FOUND'

        if package_under_cov == input_pkg:
            total_lines_under_testing += lines_coverage['denominator']
            total_lines_tested += lines_coverage['numerator']
            print(' * %s [%04.2f] -- %i/%i' % (
                  entry_name,
                  lines_coverage['ratio'],
                  lines_coverage['numerator'],
                  lines_coverage['denominator']))

    if total_lines_under_testing == 0:
        print('Package not found: ' + input_pkg, file=sys.stderr)
        sys.exit(-1)

    print('\nCombined unit testing for %s: %04.2f%% %i/%i' % (
        input_pkg,
        total_lines_tested / total_lines_under_testing * 100,
        total_lines_tested,
        total_lines_under_testing))
