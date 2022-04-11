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


# Future Modules:
from __future__ import annotations

# Built-in Modules:
from collections.abc import Iterable


class NamedBitFlags(object):
	def __init__(self, flags: Iterable[str]) -> None:
		self.map_by_name: dict[str, int] = {}
		self.map_by_number: dict[int, str] = {}
		for bit, name in enumerate(flags, 1):
			self.map_by_number[1 << (bit - 1)] = name
			self.map_by_name[name] = 1 << (bit - 1)

	def bits_to_flags(self, bits: int) -> set[str]:
		return {self.map_by_number[num] for num in self.map_by_number if bits & num}

	def flags_to_bits(self, flags: Iterable[str]) -> int:
		return sum(self.map_by_name[flag] for flag in flags if flag in self.map_by_name)


class MMapperException(Exception):
	pass


__all__: list[str] = ["coordinates", "database", "info_marks", "rooms", "qfile"]
__version__: str = "0.0.0"
