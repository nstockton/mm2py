﻿# -*- coding: utf-8 -*-

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


from collections import OrderedDict
from decimal import Decimal, ROUND_HALF_UP
import io
import zlib

from . import MMAPPER_MAGIC, MMAPPER_VERSIONS, MMapperException
from .coordinates import Coordinates
from .info_marks import (
	INFO_MARK_SCALE,
	INFO_MARK_HALF_ROOM_OFFSET,
	INFO_MARK_OFFSET1,
	INFO_MARK_OFFSET2,
	INFO_MARK_TEXT_OFFSET,
	INFO_MARK_TYPE,
	INFO_MARK_TYPE_TO_BITS,
	INFO_MARK_CLASS,
	INFO_MARK_CLASS_TO_BITS,
	InfoMark
)
from .rooms import (
	MOB_FLAGS,
	LOAD_FLAGS,
	EXIT_FLAGS,
	DOOR_FLAGS,
	ALIGNMENT_TYPE,
	ALIGNMENT_TYPE_TO_BITS,
	LIGHT_TYPE,
	LIGHT_TYPE_TO_BITS,
	PORTABLE_TYPE,
	PORTABLE_TYPE_TO_BITS,
	RIDABLE_TYPE,
	RIDABLE_TYPE_TO_BITS,
	SUN_DEATH_TYPE,
	SUN_DEATH_TYPE_TO_BITS,
	TERRAIN_TYPE,
	TERRAIN_TYPE_TO_BITS,
	Exit,
	Room
)
from .qfile import UINT32_MAX, QFile


DIRECTIONS = ("north", "south", "east", "west", "up", "down", "unknown")


def lround(value):
	return int(Decimal(str(value)).quantize(Decimal(0), rounding=ROUND_HALF_UP))


class BadMagicNumberException(MMapperException):
	pass


class UnsupportedVersionException(MMapperException):
	def __init__(self, version):
		MMapperException.__init__(self, "Do not support version 0{:o} of MMapper data".format(version))


class Database(object):
	def __init__(self, file_name=None):
		self.selected = Coordinates()
		self.rooms = OrderedDict()
		self.info_marks = []
		if file_name is not None:
			self.load(file_name)

	def load(self, file_name):
		decompressed_stream = io.BytesIO()
		with open(file_name, "rb") as compressed_stream:
			qstream = QFile(compressed_stream)
			magic = qstream.read_uint32()
			if magic != MMAPPER_MAGIC:
				raise BadMagicNumberException()
			version = qstream.read_int32()
			if version not in MMAPPER_VERSIONS:
				raise UnsupportedVersionException(version)
			else:
				version = MMAPPER_VERSIONS[version]
			if version >= 243:
				# As of MMapper V2.43, MMapper uses qCompress and qUncompress
				# from the QByteArray class for data compression.
				# From the web page at
				# https://doc.qt.io/archives/qt-5.7/qbytearray.html#qUncompress
				# "Note: If you want to use this function to uncompress external data
				# that was compressed using zlib, you first need to prepend a four byte header
				# to the byte array containing the data. The header must contain
				# the expected length (in bytes) of the uncompressed data, expressed as
				# an unsigned, big-endian, 32-bit integer."
				# We can therefore assume that MMapper data files stored by V2.43
				# or later are compressed using standard zlib with a non-standard 4-byte header.
				qstream.read_uint32()  # We don't need the header.
			block_size = 8192
			decompressor = zlib.decompressobj()
			data = compressed_stream.read(block_size)
			while data:
				decompressed_stream.write(decompressor.decompress(data))
				data = compressed_stream.read(block_size)
			del qstream
		decompressed_stream.seek(0)
		qstream = QFile(decompressed_stream)
		total_rooms = qstream.read_uint32()
		total_marks = qstream.read_uint32()
		self.selected += (qstream.read_int32(), qstream.read_int32(), qstream.read_int32())  # (x, y, z)
		if version <= 251:
			# In version 251 and below, moving north would decrement the y coordinate.
			self.selected.y = -self.selected.y
		for i in range(total_rooms):
			room = Room(parent=self.rooms)
			room.name = qstream.read_string()
			room.static_desc = qstream.read_string()
			room.dynamic_desc = qstream.read_string()
			vnum = qstream.read_uint32()
			room.note = qstream.read_string()
			room.terrain = TERRAIN_TYPE.get(qstream.read_uint8(), TERRAIN_TYPE[0])
			room.light = LIGHT_TYPE.get(qstream.read_uint8(), LIGHT_TYPE[0])
			room.alignment = ALIGNMENT_TYPE.get(qstream.read_uint8(), ALIGNMENT_TYPE[0])
			room.portable = PORTABLE_TYPE.get(qstream.read_uint8(), PORTABLE_TYPE[0])
			if version >= 202:
				room.ridable = RIDABLE_TYPE.get(qstream.read_uint8(), RIDABLE_TYPE[0])
			if version >= 240:
				room.sundeath = SUN_DEATH_TYPE.get(qstream.read_uint8(), SUN_DEATH_TYPE[0])
				room.mob_flags.update(MOB_FLAGS.bits_to_flags(qstream.read_uint32()))
				room.load_flags.update(LOAD_FLAGS.bits_to_flags(qstream.read_uint32()))
			else:
				room.mob_flags.update(MOB_FLAGS.bits_to_flags(qstream.read_uint16()))
				room.load_flags.update(LOAD_FLAGS.bits_to_flags(qstream.read_uint16()))
			room.updated = bool(qstream.read_uint8())
			room.coordinates += (qstream.read_int32(), qstream.read_int32(), qstream.read_int32())
			if version <= 251:
				# In version 251 and below, moving north would decrement the y coordinate.
				room.y = -room.y
			for direction in DIRECTIONS:
				ext = Exit(parent=room)  # 'exit' is a built in function in Python. Use 'ext' instead.
				if version >= 240:
					ext.exit_flags.update(EXIT_FLAGS.bits_to_flags(qstream.read_uint16()))
				else:
					ext.exit_flags.update(EXIT_FLAGS.bits_to_flags(qstream.read_uint8()))
					if "door" in ext.exit_flags:
						ext.exit_flags.add("exit")
				# Exits saved after MMapper V2.04 were offset by 1 bit causing corruption and excessive NO_MATCH exits.
				if version >= 204 and version < 251 and "no_match" in ext.exit_flags:
					ext.exit_flags.remove("no_match")
				if version >= 237:
					ext.door_flags.update(DOOR_FLAGS.bits_to_flags(qstream.read_uint16()))
				else:
					ext.door_flags.update(DOOR_FLAGS.bits_to_flags(qstream.read_uint8()))
				ext.door_name = qstream.read_string()
				connection = qstream.read_uint32()
				while connection != UINT32_MAX:
					ext.inbound_connections.append(connection)
					connection = qstream.read_uint32()
				connection = qstream.read_uint32()
				while connection != UINT32_MAX:
					ext.outbound_connections.append(connection)
					connection = qstream.read_uint32()
				room._exits[direction] = ext
			self.rooms[vnum] = room
		for i in range(total_marks):
			mark = InfoMark()
			if version <= 251:
				# Value ignored; called for side effect.
				qstream.read_string()  # Mark name.
			mark.text = qstream.read_string()
			if version <= 251:
				# Value ignored; called for side effect.
				qstream.read_uint32()  # Julian day.
				qstream.read_uint32()  # Milliseconds since midnight.
				qstream.read_uint8()  # Time zone (0 = local time, 1 = UTC).
			mark.type = INFO_MARK_TYPE.get(qstream.read_uint8(), INFO_MARK_TYPE[0])
			if version >= 237:
				mark.cls = INFO_MARK_CLASS.get(qstream.read_uint8(), INFO_MARK_CLASS[0])
				mark.rotation_angle = qstream.read_int32()
				if version < 260:
					mark.rotation_angle /= INFO_MARK_SCALE
			mark.pos1 += (qstream.read_int32(), qstream.read_int32(), qstream.read_int32())
			mark.pos2 += (qstream.read_int32(), qstream.read_int32(), qstream.read_int32())
			if version <= 251:
				mark.pos1 += INFO_MARK_HALF_ROOM_OFFSET
				mark.pos2 += INFO_MARK_HALF_ROOM_OFFSET
				if mark.type == "text":
					mark.pos1 += INFO_MARK_TEXT_OFFSET
					mark.pos2 += INFO_MARK_TEXT_OFFSET
				elif mark.type == "arrow":
					mark.pos1 += INFO_MARK_OFFSET1
					mark.pos2 += INFO_MARK_OFFSET2
				mark.rotation_angle = -mark.rotation_angle
				# In version 251 and below, moving north would decrement the y coordinate.
				mark.pos1.y = -mark.pos1.y
				mark.pos2.y = -mark.pos2.y
			if mark.type != "text" and mark.text:
				mark.text = ""
			elif mark.type == "text" and not mark.text:
				mark.text = "New Marker"
			self.info_marks.append(mark)
		# Free up the memory
		del qstream
		decompressed_stream.seek(0)
		decompressed_stream.truncate()
		decompressed_stream.close()
		del decompressed_stream

	def save(self, file_name):
		uncompressed_stream = io.BytesIO()
		qstream = QFile(uncompressed_stream)
		qstream.write_uint32(len(self.rooms))
		qstream.write_uint32(len(self.info_marks))
		for coord in self.selected:
			qstream.write_int32(coord)
		for vnum, room in self.rooms.items():
			qstream.write_string(room.name)
			qstream.write_string(room.static_desc)
			qstream.write_string(room.dynamic_desc)
			qstream.write_uint32(vnum)
			qstream.write_string(room.note)
			qstream.write_uint8(TERRAIN_TYPE_TO_BITS[room.terrain])
			qstream.write_uint8(LIGHT_TYPE_TO_BITS[room.light])
			qstream.write_uint8(ALIGNMENT_TYPE_TO_BITS[room.alignment])
			qstream.write_uint8(PORTABLE_TYPE_TO_BITS[room.portable])
			qstream.write_uint8(RIDABLE_TYPE_TO_BITS[room.ridable])
			qstream.write_uint8(SUN_DEATH_TYPE_TO_BITS[room.sundeath])
			qstream.write_uint32(MOB_FLAGS.flags_to_bits(room.mob_flags))
			qstream.write_uint32(LOAD_FLAGS.flags_to_bits(room.load_flags))
			qstream.write_uint8(int(room.updated))
			for coord in room.coordinates:
				qstream.write_int32(coord)
			for direction in DIRECTIONS:
				ext = room._exits[direction]
				qstream.write_uint16(EXIT_FLAGS.flags_to_bits(ext.exit_flags))
				qstream.write_uint16(DOOR_FLAGS.flags_to_bits(ext.door_flags))
				qstream.write_string(ext.door_name)
				for connection in ext.inbound_connections:
					qstream.write_uint32(connection)
				qstream.write_uint32(UINT32_MAX)
				for connection in ext.outbound_connections:
					qstream.write_uint32(connection)
				qstream.write_uint32(UINT32_MAX)
		for mark in self.info_marks:
			qstream.write_string(mark.text)
			qstream.write_uint8(INFO_MARK_TYPE_TO_BITS[mark.type])
			qstream.write_uint8(INFO_MARK_CLASS_TO_BITS[mark.cls])
			qstream.write_int32(lround(mark.rotation_angle))
			for coord in mark.pos1:
				qstream.write_int32(coord)
			for coord in mark.pos2:
				qstream.write_int32(coord)
		del qstream
		with open(file_name, "wb") as output_stream:
			qstream = QFile(output_stream)
			qstream.write_uint32(MMAPPER_MAGIC)
			qstream.write_int32(max(MMAPPER_VERSIONS))
			qstream.write_uint32(uncompressed_stream.tell())
			uncompressed_stream.seek(0)
			block_size = 8192
			compressor = zlib.compressobj()
			data = uncompressed_stream.read(block_size)
			while data:
				output_stream.write(compressor.compress(data))
				data = uncompressed_stream.read(block_size)
			output_stream.write(compressor.flush())
			del qstream
		uncompressed_stream.seek(0)
		uncompressed_stream.truncate()
		uncompressed_stream.close()
		del uncompressed_stream
