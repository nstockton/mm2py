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


import struct

from . import MMapperException

UINT8_MAX = 0xff
UINT16_MAX = 0xffff
UINT32_MAX = 0xffffffff


class IncompleteQFileException(MMapperException):
	pass


class QFile(object):
	def __init__(self, stream):
		self._stream = stream

	def read_int8(self):
		data = self._stream.read(1)
		if len(data) != 1:
			raise IncompleteQFileException()
		return struct.unpack("b", data)[0]

	def read_uint8(self):
		data = self._stream.read(1)
		if len(data) != 1:
			raise IncompleteQFileException()
		return struct.unpack("B", data)[0]

	def read_int16(self):
		data = self._stream.read(2)
		if len(data) != 2:
			raise IncompleteQFileException()
		return struct.unpack(">h", data)[0]

	def read_uint16(self):
		data = self._stream.read(2)
		if len(data) != 2:
			raise IncompleteQFileException()
		return struct.unpack(">H", data)[0]

	def read_int32(self):
		data = self._stream.read(4)
		if len(data) != 4:
			raise IncompleteQFileException()
		return struct.unpack(">i", data)[0]

	def read_uint32(self):
		data = self._stream.read(4)
		if len(data) != 4:
			raise IncompleteQFileException()
		return struct.unpack(">I", data)[0]

	def read_string(self):
		length = self.read_uint32()
		if length == UINT32_MAX:
			return ""
		data = self._stream.read(length)
		if len(data) != length:
			raise IncompleteQFileException()
		return data.decode("UTF_16_BE")

	def write_int8(self, data):
		self._stream.write(struct.pack("b", data))

	def write_uint8(self, data):
		self._stream.write(struct.pack("B", data))

	def write_int16(self, data):
		self._stream.write(struct.pack(">h", data))

	def write_uint16(self, data):
		self._stream.write(struct.pack(">H", data))

	def write_int32(self, data):
		self._stream.write(struct.pack(">i", data))

	def write_uint32(self, data):
		self._stream.write(struct.pack(">I", data))

	def write_string(self, data):
		if data:
			data = data.encode("UTF_16_BE")
			self.write_uint32(len(data))
			self._stream.write(data)
		else:
			self.write_uint32(UINT32_MAX)
