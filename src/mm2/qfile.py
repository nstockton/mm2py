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
import struct
from typing import BinaryIO

# Local Modules:
from . import MMapperException


INT8_MAX: int = 0x7F
UINT8_MAX: int = 0xFF
INT16_MAX: int = 0x7FFF
UINT16_MAX: int = 0xFFFF
INT32_MAX: int = 0x7FFFFFFF
UINT32_MAX: int = 0xFFFFFFFF


class IncompleteQFileException(MMapperException):
	pass


class QFile(object):
	def __init__(self, stream: BinaryIO) -> None:
		self._stream: BinaryIO = stream

	def _read(self, length: int) -> bytes:
		data: bytes = self._stream.read(length)
		if len(data) != length:
			raise IncompleteQFileException(f"{length} bytes expected, got {len(data)}")
		return data

	def read_int8(self) -> int:
		data: bytes = self._read(1)
		return int(struct.unpack("b", data)[0])

	def read_uint8(self) -> int:
		data: bytes = self._read(1)
		return int(struct.unpack("B", data)[0])

	def read_int16(self) -> int:
		data: bytes = self._read(2)
		return int(struct.unpack(">h", data)[0])

	def read_uint16(self) -> int:
		data: bytes = self._read(2)
		return int(struct.unpack(">H", data)[0])

	def read_int32(self) -> int:
		data: bytes = self._read(4)
		return int(struct.unpack(">i", data)[0])

	def read_uint32(self) -> int:
		data: bytes = self._read(4)
		return int(struct.unpack(">I", data)[0])

	def read_string(self) -> str:
		length: int = self.read_uint32()
		if length == UINT32_MAX:
			return ""
		return self._read(length).decode("UTF_16_BE")

	def write_int8(self, value: int) -> None:
		self._stream.write(struct.pack("b", value))

	def write_uint8(self, value: int) -> None:
		self._stream.write(struct.pack("B", value))

	def write_int16(self, value: int) -> None:
		self._stream.write(struct.pack(">h", value))

	def write_uint16(self, value: int) -> None:
		self._stream.write(struct.pack(">H", value))

	def write_int32(self, value: int) -> None:
		self._stream.write(struct.pack(">i", value))

	def write_uint32(self, value: int) -> None:
		self._stream.write(struct.pack(">I", value))

	def write_string(self, text: str) -> None:
		if text:
			data: bytes = text.encode("UTF_16_BE")
			self.write_uint32(len(data))
			self._stream.write(data)
		else:
			self.write_uint32(UINT32_MAX)
