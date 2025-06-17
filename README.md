[![PyPI](https://img.shields.io/pypi/v/mprofile)](https://pypi.org/project/mprofile/)
[![Build Status](https://travis-ci.org/timpalpant/mprofile.svg?branch=master)](https://travis-ci.org/timpalpant/mprofile)
![PyPI - License](https://img.shields.io/pypi/l/mprofile)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mprofile)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/mprofile.svg)](https://pypistats.org/packages/mprofile)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# mprofile

A low-overhead sampling memory profiler for Python, derived from [heapprof](https://github.com/humu/heapprof), with an interface similar to [tracemalloc](https://pytracemalloc.readthedocs.io).
mprofile attempts to give results comparable to tracemalloc, but uses statistical sampling to lower memory and CPU overhead. The sampling algorithm is the one used by [tcmalloc](https://github.com/gperftools/gperftools) and Golang heap profilers.

UPD @achopik:
    Has possibility to export samples in [pprof](https://github.com/google/pprof/tree/main) format
    Tested on Python 3.12

## Installation & usage

1.  Install the profiler package using PyPI:

    ```shell
    pip3 install mprofile
    ```

2.  Enable the profiler in your application, get a snapshot of (sampled) memory usage:

    ```python
    import mprofile

    mprofile.start(sample_rate=128 * 1024)
    snap = mprofile.take_snapshot()
    ```

See the [tracemalloc](https://docs.python.org/3/library/tracemalloc.html) for API documentation. The API and objects returned by mprofile are compatible.

## Compatibility

mprofile is compatible with Python >= 3.4.
It can also be used with earlier versions of Python, but you must build CPython from source and apply the [pytracemalloc patches](https://pytracemalloc.readthedocs.io/install.html#manual-installation).

# Contributing

Pull requests and issues are welcomed!

# License

mprofile is released under the [MIT License](https://opensource.org/licenses/MIT) and incorporates code from [heapprof](https://github.com/humu/heapprof), which is also released under the MIT license.
