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

import asyncio
import atexit
import os
import shutil
import stat
import sys
import time

# Make sure to get osrf_pycommon from the vendor folder
vendor_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'vendor'))
sys.path.insert(0, os.path.join(vendor_path, 'osrf_pycommon'))
import osrf_pycommon
# Assert that we got it from the right place
assert osrf_pycommon.__file__.startswith(vendor_path), \
    ("osrf_pycommon imported from '{0}' which is not in the vendor folder '{1}'"
     .format(osrf_pycommon.__file__, vendor_path))
from osrf_pycommon.process_utils import async_execute_process
from osrf_pycommon.process_utils import AsyncSubprocessProtocol
from osrf_pycommon.process_utils import get_loop
from osrf_pycommon.terminal_color import format_color as format_color_actual
from osrf_pycommon.terminal_color import enable_ansi_color_substitution_globally

IS_JENKINS = 'JOB_NAME' in os.environ


def close_asyncio_loop():
    try:
        get_loop().close()
    except RuntimeError as exc:
        # A runtime error can occur if the loop was not used.
        if 'There is no current event loop in thread' not in str(exc):
            raise

atexit.register(close_asyncio_loop)

format_color = format_color_actual


def force_color():
    global format_color
    enable_ansi_color_substitution_globally()

    def forced_format_color(msg):
        from osrf_pycommon.terminal_color.impl import _ansi
        from osrf_pycommon.terminal_color.impl import _enabled
        from osrf_pycommon.terminal_color.impl import _format_color
        from osrf_pycommon.terminal_color.impl import _null_ansi
        ansi_dict = _ansi if _enabled else _null_ansi
        return _format_color(msg, ansi_dict)

    format_color = forced_format_color


def remove_folder(path):
    if os.path.exists(path):
        if IS_JENKINS:
            warn("Deleting the folder at '@!{0}@|@{yb}'.", fargs=(path,))
        else:
            warn("@{rf}@!DELETING ALL FILES@|@{yf} in the folder '@|@!{0}@|@{yf}', "
                 "you have 5 seconds to ctrl-c...", fargs=(path,))
            time.sleep(5)

        # Use custom on error handler for shutil.rmtree in order to remove
        # read-only files in writable folders (emulating unix behavior).
        # See: https://bugs.python.org/issue19643
        def del_rw(action, name, exc):
            os.chmod(name, stat.S_IWRITE)
            os.remove(name)
        shutil.rmtree(path, onerror=del_rw)
    assert not os.path.exists(path), "'{0}' should not exist.".format(path)


class UnbufferedIO(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        if self.stream.encoding != 'utf-8':
            data = data.encode(encoding=self.stream.encoding, errors='replace').decode()
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


def log(*args, **kwargs):
    msg = ''
    # Do color formatting for each arg and combine them.
    for arg in args:
        msg += format_color(arg)
    # Extract fargs and/or fkwargs and format the now colorized string.
    fargs, fkwargs = None, None
    if 'fargs' in kwargs:
        fargs = kwargs['fargs']
        del kwargs['fargs']
    if 'fkwargs' in kwargs:
        fkwargs = kwargs['fkwargs']
        del kwargs['fkwargs']
    if fargs is not None or fkwargs is not None:
        fargs = fargs or []
        fkwargs = fkwargs or {}
        msg = msg.format(*fargs, **kwargs)
    # If the user did not provide an end kwarg, automatically clear the coloring.
    if 'end' not in kwargs:
        msg += format_color("@|")
    # Hand off to print.
    print(msg, **kwargs)


def info(*args, **kwargs):
    log("@!II>@| ", *args, **kwargs)


def warn(*args, **kwargs):
    kwargs['file'] = kwargs.get('file', sys.stderr)
    if IS_JENKINS:
        log("@{yb}WW> ", *args, **kwargs)
    else:
        log("@{yf}WW> ", *args, **kwargs)


class MyProtocol(AsyncSubprocessProtocol):
    def __init__(self, cmd, exit_on_error, *args, **kwargs):
        self.cmd = cmd
        self.exit_on_error = exit_on_error
        AsyncSubprocessProtocol.__init__(self, *args, **kwargs)

    def on_stdout_received(self, data):
        sys.stdout.write(data.decode('utf-8', 'replace').replace(os.linesep, '\n'))

    def on_stderr_received(self, data):
        sys.stderr.write(data.decode('utf-8', 'replace').replace(os.linesep, '\n'))

    def on_process_exited(self, returncode):
        if self.exit_on_error and returncode != 0:
            log("@{rf}@!<==@| '{0}' exited with return code '{1}'",
                fargs=(" ".join(self.cmd), returncode))


class PipProtocol(AsyncSubprocessProtocol):
    def __init__(self, cmd, exit_on_error, *args, **kwargs):
        self.cmd = cmd
        self.exit_on_error = exit_on_error
        self.progress_bar = False
        self.progress_data = ''
        AsyncSubprocessProtocol.__init__(self, *args, **kwargs)

    def on_stdout_received(self, data):
        # The 'pip install' progress bar output can be pretty noisy in CI output. Print only last line 
        # every 1000 characters to reduce the noisiness.  We detect the pip progress bar by the beginning sequence of
        # '[?25l' and the end sequence of '[?25h'.
        if b'[?25l' in data:
            self.progress_bar = True
            sys.stdout.write(data.decode('utf-8', 'replace').replace('\r', '') + '\n')
        elif b'[?25h' in data:
            for display_line in self.progress_data.replace('\n', '').split('\r'):
                sys.stdout.write(display_line + '\n' if display_line else '')
            self.progress_bar = False
            self.progress_data = ''
            sys.stdout.write(data.decode('utf-8', 'replace').replace('\r', ''))
        elif self.progress_bar:
            self.progress_data += data.decode('utf-8', 'replace')
            if len(self.progress_data) >= 1000:
                sys.stdout.write(self.progress_data.split('\r')[-1] + '\n')
                self.progress_data = ''
        else:
            sys.stdout.write(data.decode('utf-8', 'replace').replace(os.linesep, '\n'))

    def on_stderr_received(self, data):
        sys.stderr.write(data.decode('utf-8', 'replace').replace(os.linesep, '\n'))

    def on_process_exited(self, returncode):
        if self.exit_on_error and returncode != 0:
            log("@{rf}@!<==@| '{0}' exited with return code '{1}'",
                fargs=(" ".join(self.cmd), returncode))


def run(cmd, exit_on_error=True, **kwargs):
    log("@{bf}==>@| @!{0}", fargs=(" ".join(cmd),))
    ret = _run(cmd, exit_on_error=exit_on_error, **kwargs)
    print()
    return ret


def run_with_prefix(prefix, cmd, exit_on_error=True, **kwargs):
    log("@{bf}==>@| @!{0}", fargs=(" ".join(cmd),))
    ret = _run(prefix + cmd, exit_on_error=exit_on_error, **kwargs)
    print()
    return ret


def _run(cmd, exit_on_error=True, **kwargs):
    def create_protocol(*args, **kwargs):
        if "pip" in cmd and "install" in cmd:
            return PipProtocol(cmd, exit_on_error, *args, **kwargs)
        else:
            return MyProtocol(cmd, exit_on_error, *args, **kwargs)

    async def run_coroutine(future):
        kwargs['emulate_tty'] = True
        transport, protocol = await async_execute_process(create_protocol, cmd, **kwargs)
        returncode = await protocol.complete
        future.set_result(returncode)

    future = asyncio.Future()
    get_loop().run_until_complete(run_coroutine(future))
    retcode = future.result()
    if exit_on_error and retcode != 0:
        sys.exit(retcode)
    return retcode


class change_directory:
    def __init__(self, directory=''):
        self.directory = directory
        self.original_cwd = None

    def __enter__(self):
        self.original_cwd = os.getcwd()
        os.chdir(self.directory)
        return self.directory

    def __exit__(self, exc_type, exc_value, traceback):
        if self.original_cwd and os.path.exists(self.original_cwd):
            os.chdir(self.original_cwd)
