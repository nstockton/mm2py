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


from collections import OrderedDict

from . import NamedBitFlags
from .coordinates import Coordinates


MOB_FLAGS = NamedBitFlags(
	[
		"rent",
		"shop",
		"weapon_shop",
		"armour_shop",
		"food_shop",
		"pet_shop",
		"guild",
		"scout_guild",
		"mage_guild",
		"cleric_guild",
		"warrior_guild",
		"ranger_guild",
		"aggressive_mob",
		"quest_mob",
		"passive_mob",
		"elite_mob",
		"super_mob"
	]
)

LOAD_FLAGS = NamedBitFlags(
	[
		"treasure",
		"armour",
		"weapon",
		"water",
		"food",
		"herb",
		"key",
		"mule",
		"horse",
		"pack_horse",
		"trained_horse",
		"rohirrim",
		"warg",
		"boat",
		"attention",
		"tower",  # Player can 'watch' surrounding rooms from this one.
		"clock",
		"mail",
		"stable",
		"white_word",
		"dark_word",
		"equipment",
		"coach",
		"ferry"
	]
)

EXIT_FLAGS = NamedBitFlags(
	[
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
	]
)

DOOR_FLAGS = NamedBitFlags(
	[
		"hidden",
		"need_key",
		"no_block",
		"no_break",
		"no_pick",
		"delayed",
		"callable",
		"knockable",
		"magic",
		"action",  # Action controlled
		"no_bash"
	]
)

ALIGNMENT_TYPE = {
	0: "undefined",
	1: "good",
	2: "neutral",
	3: "evil"
}
ALIGNMENT_TYPE_TO_BITS = {v: k for k, v in ALIGNMENT_TYPE.items()}

LIGHT_TYPE = {
	0: "undefined",
	1: "dark",
	2: "lit"
}
LIGHT_TYPE_TO_BITS = {v: k for k, v in LIGHT_TYPE.items()}

PORTABLE_TYPE = {
	0: "undefined",
	1: "portable",
	2: "notportable"
}
PORTABLE_TYPE_TO_BITS = {v: k for k, v in PORTABLE_TYPE.items()}

RIDABLE_TYPE = {
	0: "undefined",
	1: "ridable",
	2: "notridable"
}
RIDABLE_TYPE_TO_BITS = {v: k for k, v in RIDABLE_TYPE.items()}

SUN_DEATH_TYPE = {
	0: "undefined",
	1: "sundeath",
	2: "nosundeath"
}
SUN_DEATH_TYPE_TO_BITS = {v: k for k, v in SUN_DEATH_TYPE.items()}

TERRAIN_TYPE = {
	0: "undefined",
	1: "indoors",
	2: "city",
	3: "field",
	4: "forest",
	5: "hills",
	6: "mountains",
	7: "shallow",
	8: "water",
	9: "rapids",
	10: "underwater",
	11: "road",
	12: "brush",
	13: "tunnel",
	14: "cavern",
	15: "deathtrap"
}
TERRAIN_TYPE_TO_BITS = {v: k for k, v in TERRAIN_TYPE.items()}


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


class Room(object):
	def __init__(self, parent):
		self._parent = parent
		self.name = ""
		self.static_desc = ""
		self.dynamic_desc = ""
		self.note = ""
		self.terrain = TERRAIN_TYPE[0]
		self.light = LIGHT_TYPE[0]
		self.alignment = ALIGNMENT_TYPE[0]
		self.portable = PORTABLE_TYPE[0]
		self.ridable = RIDABLE_TYPE[0]
		self.sundeath = SUN_DEATH_TYPE[0]
		self.mob_flags = set()
		self.load_flags = set()
		self.updated = False
		self.coordinates = Coordinates()
		self._exits = OrderedDict()

	@property
	def x(self):
		return self.coordinates.x

	@x.setter
	def x(self, value):
		self.coordinates.x = int(value)

	@property
	def y(self):
		return self.coordinates.y

	@y.setter
	def y(self, value):
		self.coordinates.y = int(value)

	@property
	def z(self):
		return self.coordinates.z

	@z.setter
	def z(self, value):
		self.coordinates.z = int(value)

	@property
	def parent(self):
		return self._parent

	@property
	def id(self):
		for vnum, room in self.parent.items():
			if room is self:
				return vnum
		else:
			return None

	@property
	def exits(self):
		return {
			direction: self._exits[direction]
			for direction in self._exits if self._exits and self._exits[direction].exit_flags
		}
