#!/usr/bin/env python3

import argparse
import os
import re
import sys

PLUGIN_ENTRY_RE = re.compile(r'"([\w.-]+)"\s*=>\s*"([^"]+)"')
PLUGIN_REF_RE = re.compile(r'plugin="([\w.-]+)(@{1,2})([^"]*)"')


def parse_plugin_versions(plugins_rb_path):
    with open(plugins_rb_path) as f:
        content = f.read()
    return dict(PLUGIN_ENTRY_RE.findall(content))


def update_file(path, plugin_versions):
    with open(path) as f:
        original = f.read()

    changes = []

    def repl(match):
        name, at_signs, old_version = match.groups()
        new_version = plugin_versions.get(name)
        if new_version is None or new_version == old_version:
            return match.group(0)
        changes.append((name, old_version, new_version))
        return f'plugin="{name}{at_signs}{new_version}"'

    updated = PLUGIN_REF_RE.sub(repl, original)
    return updated, changes


def find_template_files(root, suffix):
    matches = []
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith(suffix):
                matches.append(os.path.join(dirpath, filename))
    return sorted(matches)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Update plugin="name@version" references in empy templates to match '
                    'the versions declared in a plugins.rb-style attributes file. '
                    'The plugins.rb versions can be regenerated from a live Jenkins server with '
                    'https://github.com/osrf/chef-osrf/blob/latest/scripts/jenkins_plugins.rb '
                    '(./scripts/jenkins_plugins.rb <Server> <User> <Password/Token>).')
    parser.add_argument('plugins_file', help='Path to a plugins.rb attributes file '
                                              '(e.g. https://github.com/osrf/chef-osrf/blob/latest/'
                                              'cookbooks/ros2ci/attributes/plugins.rb)')
    parser.add_argument('templates_dir', nargs='?', default='job_templates',
                         help='Directory to search recursively (default: job_templates)')
    parser.add_argument('--suffix', default='.xml.em', help='File suffix to match (default: .xml.em)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would change without writing files')
    args = parser.parse_args()

    plugin_versions = parse_plugin_versions(args.plugins_file)
    if not plugin_versions:
        print(f'No plugin entries found in {args.plugins_file}', file=sys.stderr)
        sys.exit(1)

    template_files = find_template_files(args.templates_dir, args.suffix)
    if not template_files:
        print(f'No files matching "{args.suffix}" found under {args.templates_dir}', file=sys.stderr)
        sys.exit(1)

    total_changes = 0
    for path in template_files:
        updated, changes = update_file(path, plugin_versions)
        if not changes:
            continue
        total_changes += len(changes)
        rel_path = os.path.relpath(path)
        for name, old_version, new_version in changes:
            print(f'{rel_path}: {name} {old_version} -> {new_version}')
        if not args.dry_run:
            with open(path, 'w') as f:
                f.write(updated)

    if total_changes == 0:
        print('All plugin references already up to date.')
    elif args.dry_run:
        print(f'\n{total_changes} change(s) would be applied (dry run, nothing written).')
    else:
        print(f'\n{total_changes} change(s) applied.')
