import sys

from inspect import isclass, currentframe
from pathlib import Path
from functools import wraps
from traceback import format_stack, extract_tb, extract_stack, format_exception_only, FrameSummary
from sys import exc_info
from typing import Optional, Union, Callable, Generator, NamedTuple
from types import ModuleType, TracebackType




try:
    import xbmc
    import xbmcaddon
    from xbmc import LOGDEBUG, LOGINFO, LOGWARNING, LOGERROR, LOGFATAL

except ModuleNotFoundError:
    # TESTS: direct run
    xbmcaddon = None
    LOGDEBUG, LOGINFO, LOGWARNING, LOGERROR, LOGFATAL = 0, 1, 2, 3, 4
    _stdout = sys.stdout

    class xbmc:
        @staticmethod
        def log(msg: str, level: int = LOGINFO):
            print(f'<{level}> {msg}', file=_stdout)

#: Special log level.
LOGSPECIAL = -1


class Options:
    """Simple global logging options."""

    def __init__(self) -> None:
        self._show_log = None

    @property
    def show_log(self) -> bool:
        if self._show_log is None:
            if xbmcaddon:
                addon = xbmcaddon.Addon()
                settings = addon.getSettings()
                #from .control import settings  # local import to avoid circular import
                self._show_log = settings.getBool('debug_mode') or True
            else:
                # wymuszone true
                self._show_log = True
        return self._show_log

    @show_log.setter
    def show_log(self, value: bool) -> None:
        self._show_log = bool(value)

    @show_log.deleter
    def show_log(self) -> None:
        self._show_log = None


#: Global logging options
options = Options()


if xbmcaddon:
    addon_name = xbmcaddon.Addon().getAddonInfo('name')
else:
    addon_name = 'Wtyczka'  #Do poprawek

class CallerInfo(NamedTuple):
    """Nicer caller frame info."""

    #: Source filename.
    filename: str
    #: Code line.
    lineno: int
    #: Caller function.
    funcname: str
    #: Caller function.
    func_short_name: str
    #: Caller module.
    module: ModuleType

    @property
    def is_exec(self) -> bool:
        """True if code is dynamic (exec)."""
        return self.filename == '<string>'

    @property
    def full_name(self) -> bool:
        """Full name: modula and function."""
        return f'{self.module}.{self.funcname}'

    @classmethod
    def from_frame(cls, frame) -> 'CallerInfo':
        """Create CallerInfo form given frame."""
        caller = frame.f_code
        module = frame.f_globals.get('__name__')
        co_qualname: str = caller.co_name
        if sys.version_info >= (3, 11):
            co_qualname = caller.co_qualname
        else:
            if 'self' in caller.co_varnames:
                this = frame.f_locals.get('self')
                if this:
                    try:
                        co_qualname = f'{this.__class__.__name__}.{caller.co_name}'
                    except KeyError:
                        pass
            elif 'cls' in caller.co_varnames:
                this = frame.f_locals.get('cls')
                if this and isclass(this):
                    try:
                        co_qualname = f'{this.__name__}.{caller.co_name}'
                    except KeyError:
                        pass
        return cls(caller.co_filename, frame.f_lineno, co_qualname, caller.co_name, module)

    @classmethod
    def info(cls, n: int = 1, *, skip_empty_frames: bool = True) -> Optional['CallerInfo']:
        """Return CallerInfo from `n` depth caller frame."""
        frame = currentframe().f_back  # back from get_caller_info()
        try:
            for _ in range(n):
                if frame is None:
                    break
                back = frame.f_back
                del frame
                frame = back
            while frame:
                info = cls.from_frame(frame)
                if not skip_empty_frames or not info.is_exec:
                    return info
                back = frame.f_back
                del frame
                frame = back
        finally:
            # see https://docs.python.org/3/library/inspect.html#inspect.Traceback
            del frame


def log(msg: str, level: int = LOGINFO, *,
        module: Optional[str] = None,    # force module name
        title: Optional[str] = None,     # add extra == TITLE ==
        stack_depth: int = 1,            # stack depth, how many frame omits, default is 1 – log() caller
        skip_empty_frames: bool = True,  # hide frames with no info
        ) -> None:
    """Nicer logging (with addon name and caller info)."""

    # Support extended levels.
    try:
        #level = custom_log_levels.get(level, level)  # TODO:  outdated, remove it
        if level == LOGSPECIAL:
            if not options.show_log:
                return
            level = LOGINFO
    except Exception as exc:
        xbmc_log(f'log(FF) failed: {exc}', LOGDEBUG)
        return

    # Get info about caller.
    caller = CallerInfo.info(n=stack_depth, skip_empty_frames=skip_empty_frames)
    if not caller:
        caller = CallerInfo('<string>', 0, '-', '-', '-')

    # Module / source.
    if module is None:
        # a) module name.
        # module = caller.module
        # b) source:line.
        if caller.is_exec:
            module = '-'
        else:
            module = f'{Path(caller.filename).name}:{caller.lineno}'

    # kodi bug, each `sys.stderr.flush()` generates message "."
    if msg == '.' and caller:
        direct = CallerInfo.info(n=stack_depth, skip_empty_frames=False)
        if direct.func_short_name == 'flush':
            return
    # reformat
    #msg = log.format.sub(3 * "\052", str(msg))

    # Extra == TITLE ==.
    if title is None:
        title = ''
    else:
        title = f' == {title} =='

    # Function name.
    funcname = caller.funcname
    if funcname == '<module>':
        funcname = '-'

    try:
        if msg:  # Sprawdzanie, czy msg nie jest puste
            xbmc_log(f"[{addon_name}][{module}][{funcname}]{title} {msg}", level)
    except Exception as exc:
        try:
            if not isinstance(level, int):
                level = LOGINFO
            xbmc_log(f"Logging Failure: {exc}", level)
        except Exception:
            pass  # just give up


def plog(msg: str, level: int = LOGSPECIAL, *,
          stack_depth: int = 1,          # stack depth, how many frame omits, default is plog() caller
          **kwargs,                      # rest of log() keyword args
          ) -> None:
    """
    plog = plain log()
    Just log() but with default LOGSPECIAL level."""
    return log(msg, level=level, stack_depth=stack_depth+1, **kwargs)


class _LogExcContext:
    """Helper for `with log_exc()`."""

    def __init__(self, stack_depth: int = 1, **kwargs):
        self.stack_depth: int = stack_depth
        self.kwargs = kwargs

    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        if exc:
            log_exc(exc, stack_depth=self.stack_depth, **self.kwargs)

    def __call__(self, func: Callable):
        """Return callable for  decorator()."""
        return log_exc(func, stack_depth=self.stack_depth, **self.kwargs)


def traceback_string(traceback: TracebackType, *,  # traceback object
                     stack_depth: int = 1,         # stack depth, how many frame omits, default is caller
                     current_stack: bool = True,   # prepend current frame stack, useful with decorators
                     indent: int = 4,              # lines indent
                     ) -> None:
    """Format traceback to string."""

    def frame_str(frame: FrameSummary) -> Generator[str, None, None]:
        if frame.name == '#':
            yield f'{ind}{frame.filename}'
        else:
            yield f'{ind}  File "{frame.filename}", line {frame.lineno}, in {frame.name}'
            yield f'{ind}    {frame.line}'

    # exception
    ind: str = ' ' * indent
    own = {'log_exc', 'plog_exc', 'log_exc_wrapped', 'traceback_string', '__exit__'}
    stack = []
    # print('          >>', stack_depth, ', '.join(f.name for f in extract_stack()))  # DEBUG of DEBUG
    if current_stack:
        stack.append(FrameSummary('Logger traceback (most recent call last):', 0, '#'))
        stack.extend(extract_stack()[:-stack_depth or None])
    if traceback:
        stack.append(FrameSummary('Exception traceback (most recent call last):', 0, '#'))
        stack.extend(extract_tb(traceback))
    stack = [frame for frame in stack
             if not frame.filename.endswith('log_utils.py') or frame.name not in own]
    bt_str = '\n'.join(line for frame in stack for line in frame_str(frame))
    return bt_str


def log_exc(exc: Exception = None, level: int = LOGINFO, *,
            stack_depth: int = 1,        # stack depth, how many frame omits, default is log_exc() caller
            traceback: bool = True,      # log fill exception traceback or traceback object directly
            current_stack: bool = True,  # prepend current frame stack, useful with decorators
            indent: int = 4,             # traceback lines indent
            **kwargs,                    # rest of log() keyword args
            ) -> None:
    """
    Nicer exception logging.

    If `exc` is None `log_exc` must be called from `except:`.
    >>> try:
    >>>     ...
    >>> except Exception:
    >>>     log_exc()

    Or as with statement:
    >>> with log_exc():
    >>>     ...

    Or as decorator:
    >>> @log_exc
    >>> def foo():
    >>>     ...
    """
    if exc is None:
        etype, exc, bt = exc_info()
    elif isinstance(exc, BaseException):
        etype = type(exc)
        bt = exc.__traceback__
    if isinstance(exc, BaseException):
        if traceback:
            ind = ' ' * indent
            exc_str = '\n'.join(format_exception_only(etype, exc)).rstrip().replace('\n', f'\n{ind}')
            bt_str = traceback_string(bt, current_stack=current_stack, stack_depth=stack_depth+1, indent=indent)
            bt_str = f'\n{bt_str}\n{ind}{exc_str}'
        else:
            bt_str = ''
        log(f"EXCEPTION: {exc!r}{bt_str}", level=level, stack_depth=stack_depth+1, **kwargs)
    elif callable(exc):
        # decorator
        @wraps(exc)
        def log_exc_wrapped(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception:
                log_exc(current_stack=True, level=level, stack_depth=stack_depth,
                        traceback=traceback, indent=indent, **kwargs)
                raise

        func = exc
        return log_exc_wrapped
    else:
        return _LogExcContext(level=level, stack_depth=stack_depth, traceback=traceback,
                              current_stack=current_stack, indent=indent, **kwargs)

def plog_exc(exc: Exception = None, level: int = LOGSPECIAL, *,
              stack_depth: int = 1,          # stack depth, how many frame omits, default is log_exc() caller
              **kwargs,                      # rest of log_exc() keyword args
              ) -> None:
    """Just log_exc() but with defailt LOGSPECIAL level."""
    return log_exc(exc, level=level, stack_depth=stack_depth+1, **kwargs)


xbmc_log = xbmc.log
xbmc.log = log