# -*- coding: utf-8 -*-

# Original module written by Chris Brannon (https://github.com/CMB).
# Maintained by Nick Stockton (https://github.com/nstockton).

# This is free and unencumbered software released into the public domain.

# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
#of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# For more information, please refer to <http://unlicense.org>


from __future__ import print_function
import sys

if sys.version_info <= (2, 7):
	error = "Requires Python Version 2.7 or above... exiting."
	print(error, file=sys.stderr)
	sys.exit(1)

from setuptools import setup, find_packages

from mm2 import __version__ as VERSION

requirements = []

setup(
	name="mm2py",
	author="Nick Stockton",
	author_email="nstockton@gmail.com",
	version=str(VERSION),
	description="A Python library for reading and modifying MMapper databases",
	scripts=[],
	url="https://github.com/nstockton/mm2py",
	package_dir={"mm2": "mm2"},
	packages=find_packages(),
	zip_safe=False,
	license="The Unlicense",
	platforms="Posix; MacOS X; Windows",
	setup_requires=requirements,
	install_requires=requirements,
	classifiers=[
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"License :: Public Domain",
		"Natural Language :: English",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Topic :: Software Development :: Libraries",
	]
)
