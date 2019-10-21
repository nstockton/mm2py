# -*- coding: utf-8 -*-

# Original module written by Chris Brannon (https://github.com/CMB).
# Maintained by Nick Stockton (https://github.com/nstockton).

# This is free and unencumbered software released into the public domain.

# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
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
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# For more information, please refer to <http://unlicense.org>


MMAPPER_MAGIC = 0xffb2af01
MMAPPER_VERSIONS = {
	17: 200,  # MMapper 2.00 schema. (Initial supported version)
	24: 202,  # MMapper 2.02 schema. (Ridable flag)
	25: 204,  # MMapper 2.04 schema. (ZLib compression)
	32: 237,  # MMapper 2.37 schema. (16bit door flags, NoMatch)
	33: 240,  # MMapper 2.40 schema. (16bit exit flags, 32bit mob flags and load flags)
	34: 243,  # MMapper 2.43 schema. (qCompress, SunDeath flag)
	35: 251  # MMapper 2.51 schema. (discard all previous no_match flags)
}


class MMapperException(Exception):
	pass


__all__ = ["database", "qfile"]
__version__ = sorted(MMAPPER_VERSIONS.values())[-1]
