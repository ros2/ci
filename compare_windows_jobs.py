import argparse
import re

from collections import defaultdict
from jenkinsapi.jenkins import Jenkins

def get_build_data(jenkins_job, job_name, console_text):
    # print('Console text\n{}'.format(console_text))
    regex = '(?:job={}&build=)(\d+)'.format(job_name)
    # print('Regex string "{}"'.format(regex))
    re_match = re.search(regex, console_text)
    # print('Match {}'.format(re_match))
    if re_match is None:
        return None

    build_id = int(re_match.group(1))
    try:
        return jenkins_job.get_build(build_id)
    except:
        print('\tJob {}: could not get build id {}'.format(job_name, build_id))
        return None

def compare_test_results(windows_test_results, container_test_results):
    windows_src_dir = 'C:\\J\\workspace\\ci_windows\\ws\\src'
    container_src_dir = 'C:\\ci\\ws\\src'
    windows_tests = defaultdict(set)
    container_tests = defaultdict(set)
    statuses = set()

    for test_name, result in windows_test_results.items():
        windows_tests[result.status].add(test_name.replace(windows_src_dir, 'src'))
        statuses.add(result.status)

    for test_name, result in container_test_results.items():
        container_tests[result.status].add(test_name.replace(container_src_dir, 'src'))
        statuses.add(result.status)

    if not statuses:
        print('\tNo tests found')
        return

    for status in statuses:
        only_in_windows = windows_tests[status] - container_tests[status]
        if only_in_windows:
            print('\tUnique tests with result {} for ci_windows'.format(status))
            for test_name in sorted(only_in_windows):
                print('\t\t{}'.format(test_name))
        only_in_container = container_tests[status] - windows_tests[status]
        if only_in_container:
            print('\tUnique tests with result {} for ci_windows-container'.format(status))
            for test_name in sorted(only_in_container):
                print('\t\t{}'.format(test_name))
        if not only_in_windows and not only_in_container:
            print('\tTests match for status {}'.format(status))

def main():
    parser = argparse.ArgumentParser('Compare windows container CI builds with windows builds')
    parser.add_argument('--username', help='Username for logging in to ci farm')
    parser.add_argument('--password', help='Password token for user')
    parser.add_argument('--jenkins-url', help='Jenkins master url')
    args = parser.parse_args()

    if not args.jenkins_url.startswith('https://'):
        raise Exception('Jenkins url must start with https://')

    server = Jenkins(args.jenkins_url, username=args.username, password=args.password)
    ci_launcher = server.jobs['ci_launcher']
    ci_windows = server.jobs['ci_windows']
    ci_container = server.jobs['ci_windows-container']
    for build_id in ci_launcher.get_build_ids():
        ci_launcher_build = ci_launcher.get_build(build_id)
        console_text = ci_launcher_build.get_console()
        if 'ci_windows-container' not in console_text:
            print('No more ci_windows-container jobs')
            return

        windows_build_data = get_build_data(ci_windows, 'ci_windows', console_text)
        container_build_data = get_build_data(ci_container, 'ci_windows-container', console_text)

        if windows_build_data is None or container_build_data is None:
            print('Failed to get build data for ci_launcher build: {}'.format(build_id))
            continue

        print('ci_launcher: {}\tci_windows: {}\tci_windows-container: {}'.format(
                ci_launcher_build.buildno, windows_build_data.buildno, container_build_data.buildno))
        print('    Duration ci_windows: {:.2f} minutes\t ci_windows-container: {:.2f} minutes'.format(
                windows_build_data.get_duration().total_seconds()/60,
                container_build_data.get_duration().total_seconds()/60))

        if windows_build_data.is_running() or container_build_data.is_running():
            print('\tA build is still running. ci_windows: {} ci_windows-container: {}'.format(
                windows_build_data.is_running(), container_build_data.is_running()))
            continue

        if windows_build_data.get_status() != container_build_data.get_status():
            print('\tStatuses do not match. ci_windows: {} ci_windows-container: {}'.format(
                windows_build_data.get_status(), container_build_data.get_status()))
            continue

        if not windows_build_data.has_resultset() or not container_build_data.has_resultset():
            print('\thas_resultset() does not match ci_windows: {} ci_windows-container: {}'.format(
                windows_build_data.has_resultset(), container_build_data.has_resultset()))
            continue

        compare_test_results(windows_build_data.get_resultset(), container_build_data.get_resultset())

if __name__ == '__main__':
    main()
