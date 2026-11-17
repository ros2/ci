# Licensed under the Apache License, Version 2.0

from collections import defaultdict

from colcon_core.event.command import Command
from colcon_core.event.job import JobEnded
from colcon_core.event.output import StderrLine
from colcon_core.event.output import StdoutLine
from colcon_core.event.test import TestFailure
from colcon_core.event_handler import EventHandlerExtensionPoint
from colcon_core.plugin_system import satisfies_version
from colcon_core.subprocess import SIGINT_RESULT

# colcon_cmake appends this to ctest on a retry (--retest-until-pass)
CTEST_RERUN_FLAG = '--rerun-failed'
# pytest-rerunfailures prints this marker for every retried test
PYTEST_RERUN_MARKER = b'RERUN'


class ConsoleCohesionOnFailureEventHandler(EventHandlerExtensionPoint):
    """
    Pass task output at once to stdout, but only for unsuccessful jobs.

    Output is buffered per job and printed when the job ends if:
    - the job returned a non-zero code,
    - a test failure was reported (ctest failures leave the job rc at 0),
    - the tests had to be retried, i.e. a flaky test (ctest was re-invoked
      with ``--rerun-failed``, or pytest printed ``RERUN``).

    For all other jobs only the stderr output (if any) is printed, so that
    warnings stay visible; stdout is discarded.
    """

    # disabled by default, enable with `--event-handlers
    # console_cohesion_on_failure+`
    ENABLED_BY_DEFAULT = False

    # same as `console_cohesion`: stderr output appears below the block
    PRIORITY = 130

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(
            EventHandlerExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')
        self.enabled = ConsoleCohesionOnFailureEventHandler.ENABLED_BY_DEFAULT
        self._lines = defaultdict(list)
        self._stderr_lines = defaultdict(list)
        self._reasons = defaultdict(list)

    def __call__(self, event):  # noqa: D102
        data = event[0]

        if isinstance(data, (StdoutLine, StderrLine)):
            job = event[1]
            self._lines[job].append(data.line)
            if isinstance(data, StderrLine):
                self._stderr_lines[job].append(data.line)
            if (
                PYTEST_RERUN_MARKER in data.line
                and 'flaky test (pytest rerun)' not in self._reasons[job]
            ):
                self._reasons[job].append('flaky test (pytest rerun)')

        elif isinstance(data, Command):
            job = event[1]
            if CTEST_RERUN_FLAG in (str(c) for c in data.cmd):
                if 'flaky test (ctest rerun)' not in self._reasons[job]:
                    self._reasons[job].append('flaky test (ctest rerun)')

        elif isinstance(data, TestFailure):
            job = event[1]
            if 'test failure' not in self._reasons[job]:
                self._reasons[job].append('test failure')

        elif isinstance(data, JobEnded):
            job = event[1]
            lines = self._lines.pop(job, [])
            stderr_lines = self._stderr_lines.pop(job, [])
            reasons = self._reasons.pop(job, [])
            if data.rc == SIGINT_RESULT:
                return
            if data.rc:
                reasons.insert(0, 'return code {}'.format(data.rc))
            if reasons:
                if lines:
                    self._print_block(
                        'output', data.identifier, reasons, lines)
            elif stderr_lines:
                self._print_block(
                    'stderr', data.identifier, [], stderr_lines)

    @staticmethod
    def _print_block(kind, identifier, reasons, lines):
        title = '{}: {}'.format(kind, identifier)
        if reasons:
            title += ' ({})'.format(', '.join(reasons))
        msg = '--- {}\n'.format(title) + \
            b''.join(lines).decode(errors='replace') + '---'
        print(msg, flush=True)
