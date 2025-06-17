from __future__ import absolute_import

import fnmatch
import glob
import io
import os
import re
import sys

from setuptools import Extension, setup

README = os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md")
with io.open(README, encoding="utf-8") as f:
    long_description = f.read()


def globex(pattern, exclude=None):
    if exclude is None:
        exclude = []

    return [
        fn
        for fn in glob.iglob(pattern)
        if not any(fnmatch.fnmatch(fn, pattern) for pattern in exclude)
    ]


ext = Extension(
    "mprofile._profiler",
    language="c++",
    sources=globex("src/*.cc", exclude=["*_test.cc", "*_bench.cc"])
    + ["third_party/google/tcmalloc/sampler.cc"],
    depends=glob.glob("src/*.h"),
    include_dirs=[os.getcwd(), "src"],
    define_macros=[("PY_SSIZE_T_CLEAN", None)],
    extra_compile_args=["-std=c++11"],
    extra_link_args=["-std=c++11", "-static-libstdc++"],
)


def get_version():
    """Read the version from __init__.py."""

    with open("mprofile/__init__.py") as fp:
        # Do not handle exceptions from open() so setup will fail when it cannot
        # open the file
        line = fp.read()
        version = re.search(
            r'^__version__ = "([0-9]+\.[0-9]+(\.[0-9]+)?-?.*)"', line, re.M
        )
        if version:
            return version.group(1)

    raise RuntimeError("Cannot determine version from mprofile/__init__.py.")

setup(
    ext_modules=[ext],
)
