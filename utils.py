import itertools
import os
import pathlib
import subprocess
import sys
import functools

from typing import List, Optional

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

try:
    import importlib.metadata as importlib_metadata
except (ModuleNotFoundError, ImportError):
    import importlib_metadata
from packaging.version import Version

# some of the source code are from hbutils

def join_continuation(lines):
    """
    Based on https://github.com/jaraco/jaraco.text/blob/main/jaraco/text/__init__.py#L575 .
    Join lines continued by a trailing backslash.
    >>> list(join_continuation(['foo \\', 'bar', 'baz']))
    ['foobar', 'baz']
    >>> list(join_continuation(['foo \\', 'bar', 'baz']))
    ['foobar', 'baz']
    >>> list(join_continuation(['foo \\', 'bar \\', 'baz']))
    ['foobarbaz']
    Not sure why, but...
    The character preceding the backslash is also elided.
    >>> list(join_continuation(['goo\\', 'dly']))
    ['godly']
    A terrible idea, but...
    If no line is available to continue, suppress the lines.
    >>> list(join_continuation(['foo', 'bar\\', 'baz\\']))
    ['foo']
    """
    lines = iter(lines)
    for item in lines:
        while item.endswith('\\'):
            try:  # pragma: no cover
                item = item[:-2].strip() + next(lines)
            except StopIteration:
                return
        yield item
def drop_comment(line):
    """
    Based on https://github.com/jaraco/jaraco.text/blob/main/jaraco/text/__init__.py#L560 .
    Drop comments.
    >>> drop_comment('foo # bar')
    'foo'
    A hash without a space may be in a URL.
    >>> drop_comment('https://example.com/foo#bar')
    'https://example.com/foo#bar'
    """
    return line.partition(' #')[0]

def _nonblank(text):
    return text and not text.startswith('#')

@functools.singledispatch
def yield_lines(iterable):
    r"""
    Based on https://github.com/jaraco/jaraco.text/blob/main/jaraco/text/__init__.py#L537 .
    Yield valid lines of a string or iterable.
    >>> list(yield_lines(''))
    []
    >>> list(yield_lines(['foo', 'bar']))
    ['foo', 'bar']
    >>> list(yield_lines('foo\nbar'))
    ['foo', 'bar']
    >>> list(yield_lines('\nfoo\n#bar\nbaz #comment'))
    ['foo', 'baz #comment']
    >>> list(yield_lines(['foo\nbar', 'baz', 'bing\n\n\n']))
    ['foo', 'bar', 'baz', 'bing']
    """
    return itertools.chain.from_iterable(map(yield_lines, iterable))


@yield_lines.register(str)
def _(text):
    return filter(_nonblank, map(str.strip, text.splitlines()))


def load_req_file(requirements_file: str) -> List[str]:
    """
    Overview:
        Load requirements items from a ``requirements.txt`` file.

    :param requirements_file: Requirements file.
    :return requirements: List of requirements.

    Examples::
        >>> from hbutils.system import load_req_file
        >>> load_req_file('requirements.txt')
        ['packaging>=21.3', 'setuptools>=50.0']
    """
    with pathlib.Path(requirements_file).open() as reqfile:
        return list(map(
            lambda x: str(Requirement(x)),
            join_continuation(map(drop_comment, yield_lines(reqfile)))
        ))
        
class ReqCheckItem:
    def __init__(self, name, version, reqSpec, isSatisfied:bool):
        self.name = name
        self.version = version
        self.reqSpec = reqSpec
        self.isSatisfied = isSatisfied
        
    def print(self):
        print(f"{self.name} {self.version} {self.reqSpec} {self.isSatisfied}")
        
        

def _yield_reqs_to_install(req: Requirement, current_extra: str = ''):
    
    reqCheckItem = ReqCheckItem(name=req.name,reqSpec=req.specifier,version="0",isSatisfied=False)
    if req.marker and not req.marker.evaluate({'extra': current_extra}):
        return

    try:
        version = importlib_metadata.distribution(req.name).version
    except importlib_metadata.PackageNotFoundError:  # req not installed
        # print("Package not Found")
        reqCheckItem.version="not Found"
        reqCheckItem.isSatisfied=False
        yield reqCheckItem
    else:
        reqCheckItem.version=version
        if req.specifier.contains(version):
            for child_req in (importlib_metadata.metadata(req.name).get_all('Requires-Dist') or []):
                child_req_obj = Requirement(child_req)

                need_check, ext = False, None
                for extra in req.extras:
                    if child_req_obj.marker and child_req_obj.marker.evaluate({'extra': extra}):
                        need_check = True
                        ext = extra
                        break

                if need_check:  # check for extra reqs
                    print("check for extra reqs")
                    yield from _yield_reqs_to_install(child_req_obj, ext)
            reqCheckItem.isSatisfied=True
            yield reqCheckItem

        else:  # main version not match
            yield reqCheckItem



def check_reqs(reqs: List[str]):
    """
    Overview:
        Check if the given requirements are all satisfied.

    :param reqs: List of requirements.
    :return satisfied: All the requirements in ``reqs`` satisfied or not.

    Examples::
        >>> from hbutils.system import check_reqs
        >>> check_reqs(['pip>=20.0'])
        True
        >>> check_reqs(['pip~=19.2'])
        False
        >>> check_reqs(['pip>=20.0', 'setuptools>=50.0'])
        True

    .. note::
        If a requirement's marker is not satisfied in this environment,
        **it will be ignored** instead of return ``False``.
    """
    return map(lambda x: _yield_reqs_to_install(Requirement(x)), reqs)
    
    # for reqItem in reqItems:
    #     for req in list(reqItem):
    #         req.print()
    
    


def check_req_file(requirements_file: str):
    """
    Overview:
        Check if the requirements in the given ``requirements_file`` is satisfied.

    :param requirements_file: Requirements file, such as ``requirements.txt``.
    :return satisfied: All the requirements in ``requirements_file`` satisfied or not.

    Examples::
        >>> from hbutils.system import check_req_file
        >>>
        >>> check_req_file('requirements.txt')
        True
        >>> check_req_file('requirements-test.txt')
        True
    """
    return check_reqs(load_req_file(requirements_file))