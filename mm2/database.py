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


import io
import zlib

from . import __version__ as VERSION
from . import MMAPPER_MAGIC, MMAPPER_VERSIONS, MMapperException
from .qfile import UINT8_MAX, UINT32_MAX, QFile


# For Python 3 compatibility.
try:
	xrange
except NameError:
	xrange = range

DIRECTIONS = ("north", "south", "east", "west", "up", "down", "unknown")


class BadMagicNumberException(MMapperException):
	pass


class UnsupportedVersionException(MMapperException):
	def __init__(self, version):
		MMapperException.__init__(self, "Do not support version 0{:o} of MMapper data".format(version))


class NamedBitFlags(object):
	def __init__(self, flags):
		self.map_by_name = {}
		self.map_by_number = {}
		for bit, name in enumerate(flags, 1):
			self.map_by_number[1 << (bit - 1)] = name
			self.map_by_name[name] = 1 << (bit - 1)

	def bits_to_flags(self, bits):
		return {self.map_by_number[num] for num in self.map_by_number if bits & num}

	def flags_to_bits(self, flags):
		return sum(self.map_by_name[flag] for flag in flags if flag in self.map_by_name)


mob_flags = NamedBitFlags([
	"rent",
	"shop",
	"weaponshop",
	"armourshop",
	"foodshop",
	"petshop",
	"guild",
	"scoutguild",
	"mageguild",
	"clericguild",
	"warriorguild",
	"rangerguild",
	"smob", # Aggressive mob.
	"quest",
	"any" # Nonaggressive mob.
])

load_flags = NamedBitFlags([
	"treasure",
	"armour",
	"weapon",
	"water",
	"food",
	"herb",
	"key",
	"mule",
	"horse",
	"packhorse",
	"trainedhorse",
	"rohirrim",
	"warg",
	"boat",
	"attention",
	"tower", # Player can 'watch' surrounding rooms from this one.
	"clock",
	"mail",
	"stable"
])

exit_flags = NamedBitFlags([
	"exit",
	"door",
	"road",
	"climb",
	"random",
	"special",
	"no_match",
	"flow",
	"no_flee",
	"damage",
	"fall",
	"guarded"
])

door_flags = NamedBitFlags([
	"hidden",
	"needkey",
	"noblock",
	"nobreak",
	"nopick",
	"delayed",
	"callable",
	"knockable",
	"magic",
	"action", # Action controlled
	"no_bash"
])

alignment_type = {
	0: "undefined",
	1: "good",
	2: "neutral",
	3: "evil"}

info_mark_type = {
	0: "text",
	1: "line",
	2: "arrow"
}

info_mark_class = {
	0: "generic",
	1: "herb",
	2: "river",
	3: "place",
	4: "mob",
	5: "comment",
	6: "road",
	7: "object",
	8: "action",
	9: "locality"
}

light_type = {
	0: "undefined",
	1: "dark",
	2: "lit"}

portable_type = {
	0: "undefined",
	1: "portable",
	2: "notportable"}

ridable_type = {
	0: "undefined",
	1: "ridable",
	2: "notridable"}

sundeath_type = {
	0: "undefined",
	1: "sundeath",
	2: "nosundeath"}

terrain_type = {
	0: "undefined",
	1: "indoors",
	2: "city",
	3: "field",
	4: "forest",
	5: "hills",
	6: "mountains",
	7: "shallowwater",
	8: "water",
	9: "rapids",
	10: "underwater",
	11: "road",
	12: "brush",
	13: "tunnel",
	14: "cavern",
	15: "death",
	16: "random"
}


class Exit(object):
	def __init__(self, parent):
		self._parent = parent
		self.exit_flags = set()
		self.door_flags = set()
		self.door_name = ""
		self.inbound_connections = []
		self.outbound_connections = []

	@property
	def parent(self):
		return self._parent


class InfoMark(object):
	def __init__(self):
		self.name = ""
		self.type = "text"
		self.julian_day = None
		self.ms = None
		self.time_zone = None
		self.cls = "generic"
		self.rotation_angle = 0.0
		self.pos1 = (0, 0, 0)
		self.pos2 = (0, 0, 0)


class Room(object):
	def __init__(self, parent):
		self._parent = parent
		self.name = ""
		self.static_desc = ""
		self.dynamic_desc = ""
		self.note = ""
		self.terrain = terrain_type[0]
		self.light = light_type[0]
		self.alignment = alignment_type[0]
		self.portable = portable_type[0]
		self.ridable = ridable_type[0]
		self.sundeath = sundeath_type[0]
		self.mob_flags = set()
		self.load_flags = set()
		self.updated = False
		self.x = 0
		self.y = 0
		self.z = 0
		self._exits = {}

	@property
	def parent(self):
		return self._parent

	@property
	def id(self):
		for vnum, room in self.parent.iteritems():
			if room is self:
				return vnum

	@property
	def exits(self):
		return {direction: self._exits[direction] for direction in self._exits if self._exits and self._exits[direction].exit_flags}


class Database(object):
	def __init__(self, file_name=None):
		self.version = VERSION
		self.selected = (0, 0, 0) # (x, y, z)
		self.rooms = {}
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
			self.version = version
			if version >= 243:
				# As of MMapper V2.43, MMapper uses qCompress and qUncompress from the QByteArray class for data compression.
				# From the web page at
				# https://doc.qt.io/archives/qt-5.7/qbytearray.html#qUncompress
				# "Note: If you want to use this function to uncompress external data that was compressed using zlib, you first need to prepend a four byte header to the byte array containing the data. The header must contain the expected length (in bytes) of the uncompressed data, expressed as an unsigned, big-endian, 32-bit integer."
				# We can therefore assume that MMapper data files stored by V2.43 or later are compressed using standard zlib with a non-standard 4-byte header.
				header = qstream.read_uint32()
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
		self.selected = (qstream.read_int32(), qstream.read_int32(), qstream.read_int32()) # (x, y, z)
		for i in xrange(total_rooms):
			room = Room(parent=self.rooms)
			room.name = qstream.read_string()
			room.static_desc = qstream.read_string()
			room.dynamic_desc = qstream.read_string()
			vnum = qstream.read_uint32()
			room.note = qstream.read_string()
			room.terrain = terrain_type.get(qstream.read_uint8(), 0)
			room.light = light_type.get(qstream.read_uint8(), 0)
			room.alignment = alignment_type.get(qstream.read_uint8(), 0)
			room.portable = portable_type.get(qstream.read_uint8(), 0)
			if version >= 202:
				room.ridable = ridable_type.get(qstream.read_uint8(), 0)
			if version >= 240:
				room.sundeath = sundeath_type.get(qstream.read_uint8(), 0)
				room.mob_flags.update(mob_flags.bits_to_flags(qstream.read_uint32()))
				room.load_flags.update(load_flags.bits_to_flags(qstream.read_uint32()))
			else:
				room.mob_flags.update(mob_flags.bits_to_flags(qstream.read_uint16()))
				room.load_flags.update(load_flags.bits_to_flags(qstream.read_uint16()))
			room.updated = bool(qstream.read_uint8())
			room.x = qstream.read_int32()
			room.y = qstream.read_int32()
			room.z = qstream.read_int32()
			for direction in DIRECTIONS:
				ext = Exit(parent=room) # 'exit' is a built in function in Python. Use 'ext' instead.
				if version >= 240:
					ext.exit_flags.update(exit_flags.bits_to_flags(qstream.read_uint16()))
				else:
					ext.exit_flags.update(exit_flags.bits_to_flags(qstream.read_uint8()))
					if "door" in ext.exit_flags:
						ext.exit_flags.add("exit")
				# Exits saved after MMapper V2.04 were offset by 1 bit causing corruption and excessive NO_MATCH exits.
				if version >= 204 and version < 251 and "no_match" in ext.exit_flags:
					ext.exit_flags.remove("no_match")
				if version >= 237:
					ext.door_flags.update(door_flags.bits_to_flags(qstream.read_uint16()))
				else:
					ext.door_flags.update(door_flags.bits_to_flags(qstream.read_uint8()))
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
		for i in xrange(total_marks):
			mark = InfoMark()
			mark.name = qstream.read_string()
			mark.text = qstream.read_string()
			jd = qstream.read_uint32()
			mark.julian_day = jd if jd else None # QDate objects don't have a year 0.
			ms = qstream.read_uint32() # Milliseconds since midnight.
			mark.ms = ms if ms != UINT32_MAX else None
			tz = qstream.read_uint8() # mark time zone 0 = local time, 1 = UTC
			mark.time_zone = tz if tz != UINT8_MAX else None
			mark.type = info_mark_type.get(qstream.read_uint8(), 0)
			if version >= 237:
				mark.cls = info_mark_class.get(qstream.read_uint8(), 0)
				mark.rotation_angle = qstream.read_uint32()
			mark.pos1 = (qstream.read_int32(), qstream.read_int32(), qstream.read_int32())
			mark.pos2 = (qstream.read_int32(), qstream.read_int32(), qstream.read_int32())
			self.info_marks.append(mark)
		# Free up the memory
		del qstream
		decompressed_stream.seek(0)
		decompressed_stream.truncate()
		decompressed_stream.close()
		del decompressed_stream
