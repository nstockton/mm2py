# Copyright (C) 2024 Chris Brannon and Nick Stockton
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

"""Database loading and saving."""

# Future Modules:
from __future__ import annotations

# Built-in Modules:
import io
import zlib
from collections import OrderedDict
from decimal import ROUND_HALF_UP, Decimal
from enum import IntEnum
from functools import partial
from pathlib import Path
from typing import Any, BinaryIO, Optional

# Local Modules:
from . import MMapperError
from .coordinates import Coordinates
from .info_marks import (
	INFO_MARK_CLASS,
	INFO_MARK_CLASS_TO_BITS,
	INFO_MARK_HALF_ROOM_OFFSET,
	INFO_MARK_OFFSET1,
	INFO_MARK_OFFSET2,
	INFO_MARK_SCALE,
	INFO_MARK_TEXT_OFFSET,
	INFO_MARK_TYPE,
	INFO_MARK_TYPE_TO_BITS,
	InfoMark,
)
from .qfile import UINT32_MAX, QFile
from .rooms import (
	Alignment,
	DoorFlags,
	Exit,
	ExitFlags,
	Light,
	LoadFlags,
	MobFlags,
	Portable,
	Ridable,
	Room,
	Sundeath,
	Terrain,
)


MMAPPER_MAGIC: int = 0xFFB2AF01
DIRECTIONS: tuple[str, ...] = ("north", "south", "east", "west", "up", "down", "unknown")


class MMapperVersion(IntEnum):
	V2_0_0_INITIAL = 17  # Initial schema (Apr 2006).
	V2_0_2_RIDABLE = 24  # Ridable flag (Oct 2006).
	V2_0_4_ZLIB = 25  # Zlib compression (Jun 2009).
	V2_3_7_DOOR_FLAGS_NO_MATCH = 32  # 16bit door flags, NoMatch (Dec 2016).
	V2_4_0_SUNDEATH_LARGER_FLAGS = 33  # SUNDEATH Flag, 16bit exit flags, 32bit mob and load flags (Dec 2017).
	V2_4_3_QCOMPRESS = 34  # qCompress (Jan 2018).
	V2_5_1_DISCARD_NO_MATCH = 35  # Discard all previous no_match flags (Aug 2018).
	# Starting in 2019, versions are date based, VYY_MM_REV.
	V19_10_0_NEW_COORDS = 36  # Switch to new coordinate system.
	V25_02_0_NO_INBOUND_LINKS = 38  # Stops loading and saving inbound links.
	V25_02_1_REMOVE_UP_TO_DATE = 39  # Removes upToDate.
	V25_02_2_SERVER_ID = 40  # adds server_id.


def lround(value: float) -> int:
	return int(Decimal(str(value)).quantize(Decimal(0), rounding=ROUND_HALF_UP))


class BadMagicNumberError(MMapperError):
	pass


class UnsupportedVersionError(MMapperError):
	def __init__(self, version: int) -> None:
		MMapperError.__init__(self, f"Do not support version 0{version:o} of MMapper data")


class Database:
	def __init__(self, file_name: Optional[str] = None) -> None:
		self.selected: Coordinates = Coordinates()
		self.rooms: dict[int, Room] = OrderedDict()
		self.info_marks: list[InfoMark] = []
		if file_name is not None:
			self.load(file_name)

	def load(self, file_name: str) -> None:  # NOQA: C901, PLR0912, PLR0915
		decompressed_stream: BinaryIO = io.BytesIO()
		qstream: QFile
		with Path(file_name).open("rb") as compressed_stream:
			qstream = QFile(compressed_stream)
			magic: int = qstream.read_uint32()
			if magic != MMAPPER_MAGIC:
				raise BadMagicNumberError
			version_number: int = qstream.read_int32()
			try:
				version: MMapperVersion = MMapperVersion(version_number)
			except ValueError:
				raise UnsupportedVersionError(version_number) from None
			if version >= MMapperVersion.V2_4_3_QCOMPRESS:
				# As of MMapper V2.43, MMapper uses qCompress and qUncompress
				# from the QByteArray class for data compression.
				# From the web page at
				"""https://doc.qt.io/archives/qt-5.7/qbytearray.html#qUncompress"""
				# "Note, If you want to use this function to uncompress external data
				# that was compressed using zlib, you first need to prepend a four byte header
				# to the byte array containing the data. The header must contain
				# the expected length in bytes of the uncompressed data, expressed as
				# an unsigned, big-endian, 32-bit integer."
				# We can therefore assume that MMapper data files stored by V2.43
				# or later are compressed using standard zlib with a non-standard 4-byte header.
				qstream.read_uint32()  # We don't need the header.
			block_size: int = 8192
			decompressor: Any = zlib.decompressobj()
			for data in iter(partial(compressed_stream.read, block_size), b""):  # NOQA: FURB122
				decompressed_stream.write(decompressor.decompress(data))
			del qstream
		decompressed_stream.seek(0)
		qstream = QFile(decompressed_stream)
		total_rooms: int = qstream.read_uint32()
		total_marks: int = qstream.read_uint32()
		self.selected += (qstream.read_int32(), qstream.read_int32(), qstream.read_int32())  # (x, y, z)
		if version < MMapperVersion.V19_10_0_NEW_COORDS:
			# In version 251 and below, moving north would decrement the y coordinate.
			self.selected.y *= -1
		for _ in range(total_rooms):
			room: Room = Room(parent=self.rooms)
			room.name = qstream.read_string()
			room.description = qstream.read_string()
			room.contents = qstream.read_string()
			vnum: int = qstream.read_uint32()
			room.note = qstream.read_string()
			room.terrain = Terrain(qstream.read_uint8())
			room.light = Light(qstream.read_uint8())
			room.alignment = Alignment(qstream.read_uint8())
			room.portable = Portable(qstream.read_uint8())
			if version >= MMapperVersion.V2_0_2_RIDABLE:
				room.ridable = Ridable(qstream.read_uint8())
			if version >= MMapperVersion.V2_4_0_SUNDEATH_LARGER_FLAGS:
				room.sundeath = Sundeath(qstream.read_uint8())
				room.mob_flags |= MobFlags(qstream.read_uint32())
				room.load_flags |= LoadFlags(qstream.read_uint32())
			else:
				room.mob_flags |= MobFlags(qstream.read_uint16())
				room.load_flags |= LoadFlags(qstream.read_uint16())
			room.updated = bool(qstream.read_uint8())
			room.coordinates += (qstream.read_int32(), qstream.read_int32(), qstream.read_int32())
			if version < MMapperVersion.V19_10_0_NEW_COORDS:
				# In version 251 and below, moving north would decrement the y coordinate.
				room.y *= -1
			for direction in DIRECTIONS:
				ext: Exit = Exit(parent=room)  # 'exit' is a built in function in Python. Use 'ext' instead.
				if version >= MMapperVersion.V2_4_0_SUNDEATH_LARGER_FLAGS:
					ext.exit_flags |= ExitFlags(qstream.read_uint16())
				else:
					ext.exit_flags |= ExitFlags(qstream.read_uint8())
					if ExitFlags.DOOR in ext.exit_flags:
						ext.exit_flags |= ExitFlags.EXIT
				# Exits saved after MMapper V2.04 were offset by 1 bit
				# causing corruption and excessive NO_MATCH exits.
				if (
					MMapperVersion.V2_0_4_ZLIB <= version <= MMapperVersion.V2_4_3_QCOMPRESS
					and ExitFlags.NO_MATCH in ext.exit_flags
				):
					ext.exit_flags &= ~ExitFlags.NO_MATCH  # Clear NO_MATCH flag.
				if version >= MMapperVersion.V2_3_7_DOOR_FLAGS_NO_MATCH:
					ext.door_flags |= DoorFlags(qstream.read_uint16())
				else:
					ext.door_flags |= DoorFlags(qstream.read_uint8())
				ext.door_name = qstream.read_string()
				for connection in iter(qstream.read_uint32, UINT32_MAX):
					ext.inbound_connections.append(connection)
				for connection in iter(qstream.read_uint32, UINT32_MAX):
					ext.outbound_connections.append(connection)
				room._exits[direction] = ext  # NOQA: SLF001
			self.rooms[vnum] = room
		for _ in range(total_marks):
			mark: InfoMark = InfoMark()
			if version < MMapperVersion.V19_10_0_NEW_COORDS:
				qstream.read_string()  # Mark name (ignored).
			mark.text = qstream.read_string()
			if version < MMapperVersion.V19_10_0_NEW_COORDS:
				qstream.read_uint32()  # Julian day (ignored).
				qstream.read_uint32()  # Milliseconds since midnight (ignored).
				qstream.read_uint8()  # Time zone (0 = local time, 1 = UTC) (ignored).
			mark.type = INFO_MARK_TYPE.get(qstream.read_uint8(), INFO_MARK_TYPE[0])
			if version >= MMapperVersion.V2_3_7_DOOR_FLAGS_NO_MATCH:
				mark.cls = INFO_MARK_CLASS.get(qstream.read_uint8(), INFO_MARK_CLASS[0])
				mark.rotation_angle = qstream.read_int32()
				if version < MMapperVersion.V19_10_0_NEW_COORDS:
					mark.rotation_angle //= INFO_MARK_SCALE
			mark.pos1 += (qstream.read_int32(), qstream.read_int32(), qstream.read_int32())
			mark.pos2 += (qstream.read_int32(), qstream.read_int32(), qstream.read_int32())
			if version < MMapperVersion.V19_10_0_NEW_COORDS:
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
				mark.pos1.y *= -1
				mark.pos2.y *= -1
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

	def save(self, file_name: str) -> None:
		uncompressed_stream: BinaryIO = io.BytesIO()
		qstream: QFile = QFile(uncompressed_stream)
		qstream.write_uint32(len(self.rooms))
		qstream.write_uint32(len(self.info_marks))
		for coord in self.selected:
			qstream.write_int32(coord)
		for vnum, room in self.rooms.items():
			qstream.write_string(room.name)
			qstream.write_string(room.description)
			qstream.write_string(room.contents)
			qstream.write_uint32(vnum)
			qstream.write_string(room.note)
			qstream.write_uint8(room.terrain.value)
			qstream.write_uint8(room.light.value)
			qstream.write_uint8(room.alignment.value)
			qstream.write_uint8(room.portable.value)
			qstream.write_uint8(room.ridable.value)
			qstream.write_uint8(room.sundeath.value)
			qstream.write_uint32(room.mob_flags.value)
			qstream.write_uint32(room.load_flags.value)
			qstream.write_uint8(int(room.updated))
			for coord in room.coordinates:
				qstream.write_int32(coord)
			for direction in DIRECTIONS:
				ext: Exit = room._exits[direction]  # NOQA: SLF001
				qstream.write_uint16(ext.exit_flags.value)
				qstream.write_uint16(ext.door_flags.value)
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
		with Path(file_name).open("wb") as output_stream:
			qstream = QFile(output_stream)
			qstream.write_uint32(MMAPPER_MAGIC)
			qstream.write_int32(max(MMapperVersion).value)
			qstream.write_uint32(uncompressed_stream.tell())
			uncompressed_stream.seek(0)
			block_size: int = 8192
			compressor: Any = zlib.compressobj()
			for data in iter(partial(uncompressed_stream.read, block_size), b""):  # NOQA: FURB122
				output_stream.write(compressor.compress(data))
			output_stream.write(compressor.flush())
			del qstream
		uncompressed_stream.seek(0)
		uncompressed_stream.truncate()
		uncompressed_stream.close()
		del uncompressed_stream
