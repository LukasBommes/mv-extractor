# -*- coding: utf-8 -*-
# Copyright (c) 2013 Matthias Vogelgesang <matthias.vogelgesang@gmail.com>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""pkgconfig is a Python module to interface with the pkg-config command line
tool."""

import os
import shlex
import re
import collections
from functools import wraps
from subprocess import call, PIPE, Popen


class PackageNotFoundError(Exception):
    """
    Raised if a package was not found.
    """
    def __init__(self, package):
        message = '%s not found' % package
        super(PackageNotFoundError, self).__init__(message)


def _compare_versions(v1, v2):
    """
    Compare two version strings and return -1, 0 or 1 depending on the equality
    of the subset of matching version numbers.

    The implementation is inspired by the top answer at
    http://stackoverflow.com/a/1714190/997768.
    """
    def normalize(v):
        # strip trailing .0 or .00 or .0.0 or ...
        v = re.sub(r'(\.0+)*$', '', v)
        result = []
        for part in v.split('.'):
            # just digits
            m = re.match(r'^(\d+)$', part)
            if m:
                result.append(int(m.group(1)))
                continue
            # digits letters
            m = re.match(r'^(\d+)([a-zA-Z]+)$', part)
            if m:
                result.append(int(m.group(1)))
                result.append(m.group(2))
                continue
            # digits letters digits
            m = re.match(r'^(\d+)([a-zA-Z]+)(\d+)$', part)
            if m:
                result.append(int(m.group(1)))
                result.append(m.group(2))
                result.append(int(m.group(3)))
                continue
        return tuple(result)

    n1 = normalize(v1)
    n2 = normalize(v2)

    return (n1 > n2) - (n1 < n2)


def _split_version_specifier(spec):
    """Splits version specifiers in the form ">= 0.1.2" into ('0.1.2', '>=')"""
    m = re.search(r'([<>=]?=?)?\s*([0-9.a-zA-Z]+)', spec)
    return m.group(2), m.group(1)


def _convert_error(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OSError as e:
            raise EnvironmentError("pkg-config probably not installed: %r" % e)
    return _wrapper


def _build_options(option, static=False):
    return (option, '--static') if static else (option,)


def _raise_if_not_exists(package):
    if not exists(package):
        raise PackageNotFoundError(package)


@_convert_error
def _query(package, *options):
    pkg_config_exe = os.environ.get('PKG_CONFIG', None) or 'pkg-config'
    cmd = '{0} {1} {2}'.format(pkg_config_exe, ' '.join(options), package)
    proc = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()

    return out.rstrip().decode('utf-8')


@_convert_error
def exists(package):
    """
    Return True if package information is available.

    If ``pkg-config`` not on path, raises ``EnvironmentError``.
    """
    pkg_config_exe = os.environ.get('PKG_CONFIG', None) or 'pkg-config'
    cmd = '{0} --exists {1}'.format(pkg_config_exe, package).split()
    return call(cmd) == 0


@_convert_error
def requires(package):
    """
    Return a list of package names that is required by the package.

    If ``pkg-config`` not on path, raises ``EnvironmentError``.
    """
    return _query(package, '--print-requires').split('\n')


def cflags(package):
    """
    Return the CFLAGS string returned by pkg-config.

    If ``pkg-config`` is not on path, raises ``EnvironmentError``.
    """
    _raise_if_not_exists(package)
    return _query(package, '--cflags')


def modversion(package):
    """
    Return the version returned by pkg-config.

    If `pkg-config` is not in the path, raises ``EnvironmentError``.
    """
    _raise_if_not_exists(package)
    return _query(package, '--modversion')


def libs(package, static=False):
    """
    Return the LDFLAGS string returned by pkg-config.

    The static specifier will also include libraries for static linking (i.e.,
    includes any private libraries).
    """
    _raise_if_not_exists(package)
    return _query(package, *_build_options('--libs', static=static))


def variables(package):
    """
    Return a dictionary of all the variables defined in the .pc pkg-config file
    of 'package'.
    """
    _raise_if_not_exists(package)
    result = _query(package, '--print-variables')
    names = (x.strip() for x in result.split('\n') if x != '')
    return dict(((x, _query(package, '--variable={0}'.format(x)).strip()) for x in names))


def installed(package, version):
    """
    Check if the package meets the required version.

    The version specifier consists of an optional comparator (one of =, ==, >,
    <, >=, <=) and an arbitrarily long version number separated by dots. The
    should be as you would expect, e.g. for an installed version '0.1.2' of
    package 'foo':

    >>> installed('foo', '==0.1.2')
    True
    >>> installed('foo', '<0.1')
    False
    >>> installed('foo', '>= 0.0.4')
    True

    If ``pkg-config`` not on path, raises ``EnvironmentError``.
    """
    if not exists(package):
        return False

    number, comparator = _split_version_specifier(version)
    modversion = _query(package, '--modversion')

    try:
        result = _compare_versions(modversion, number)
    except ValueError:
        msg = "{0} is not a correct version specifier".format(version)
        raise ValueError(msg)

    if comparator in ('', '=', '=='):
        return result == 0

    if comparator == '>':
        return result > 0

    if comparator == '>=':
        return result >= 0

    if comparator == '<':
        return result < 0

    if comparator == '<=':
        return result <= 0


_PARSE_MAP = {
    '-D': 'define_macros',
    '-I': 'include_dirs',
    '-L': 'library_dirs',
    '-l': 'libraries'
}


def parse(packages, static=False):
    """
    Parse the output from pkg-config about the passed package or packages.

    Builds a dictionary containing the 'libraries', the 'library_dirs', the
    'include_dirs', and the 'define_macros' that are presented by pkg-config.
    *package* is a string with space-delimited package names.

    The static specifier will also include libraries for static linking (i.e.,
    includes any private libraries).

    If ``pkg-config`` is not on path, raises ``EnvironmentError``.
    """
    for package in packages.split():
        _raise_if_not_exists(package)

    out = _query(packages, *_build_options('--cflags --libs', static=static))
    out = out.replace('\\"', '')
    result = collections.defaultdict(list)

    for token in re.split(r'(?<!\\) ', out):
        key = _PARSE_MAP.get(token[:2])
        if key:
            result[key].append(token[2:].strip())

    def split(m):
        t = tuple(m.split('='))
        return t if len(t) > 1 else (t[0], None)

    result['define_macros'] = [split(m) for m in result['define_macros']]

    # only have members with values not being the empty list (which is default
    # anyway):
    return collections.defaultdict(list, ((k, v) for k, v in result.items() if v))


def list_all():
    """Return a list of all packages found by pkg-config."""
    packages = [line.split()[0] for line in _query('', '--list-all').split('\n')]
    return packages
