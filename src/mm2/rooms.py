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
from collections import OrderedDict
from collections.abc import Mapping
from typing import Union

# Local Modules:
from . import NamedBitFlags
from .coordinates import Coordinates


MOB_FLAGS: NamedBitFlags = NamedBitFlags(
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
		"super_mob",
		"milkable",
		"rattlesnake",
	]
)

LOAD_FLAGS: NamedBitFlags = NamedBitFlags(
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
		"ferry",
	]
)

EXIT_FLAGS: NamedBitFlags = NamedBitFlags(
	[
		"exit",
		"door",
		"road",
		"climb",
		"random",
		"special",
		"no_match",  # Exit not always visible, ignore it when syncing against available exits.
		"flow",  # Water flow.
		"no_flee",
		"damage",
		"fall",
		"guarded",  # Mobs prevent movement.
	]
)

DOOR_FLAGS: NamedBitFlags = NamedBitFlags(
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
		"no_bash",
	]
)

ALIGNMENT_TYPE: dict[int, str] = {0: "undefined", 1: "good", 2: "neutral", 3: "evil"}
ALIGNMENT_TYPE_TO_BITS: dict[str, int] = {v: k for k, v in ALIGNMENT_TYPE.items()}

LIGHT_TYPE: dict[int, str] = {0: "undefined", 1: "dark", 2: "lit"}
LIGHT_TYPE_TO_BITS: dict[str, int] = {v: k for k, v in LIGHT_TYPE.items()}

PORTABLE_TYPE: dict[int, str] = {0: "undefined", 1: "portable", 2: "not_portable"}
PORTABLE_TYPE_TO_BITS: dict[str, int] = {v: k for k, v in PORTABLE_TYPE.items()}

RIDABLE_TYPE: dict[int, str] = {0: "undefined", 1: "ridable", 2: "not_ridable"}
RIDABLE_TYPE_TO_BITS: dict[str, int] = {v: k for k, v in RIDABLE_TYPE.items()}

SUN_DEATH_TYPE: dict[int, str] = {0: "undefined", 1: "sundeath", 2: "no_sundeath"}
SUN_DEATH_TYPE_TO_BITS: dict[str, int] = {v: k for k, v in SUN_DEATH_TYPE.items()}

TERRAIN_TYPE: dict[int, str] = {
	0: "undefined",
	1: "building",  # Note that MMapper still calls this "indoors".
	2: "city",
	3: "field",
	4: "forest",
	5: "hills",
	6: "mountains",
	7: "shallows",  # Note that MMapper still calls this "shallow".
	8: "water",
	9: "rapids",
	10: "underwater",
	11: "road",
	12: "brush",
	13: "tunnel",
	14: "cavern",
	15: "deathtrap",
}
TERRAIN_TYPE_TO_BITS: dict[str, int] = {v: k for k, v in TERRAIN_TYPE.items()}


class Exit(object):
	def __init__(self, parent: Room) -> None:
		self._parent: Room = parent
		self.exit_flags: set[str] = set()
		self.door_flags: set[str] = set()
		self.door_name: str = ""
		self.inbound_connections: list[int] = []
		self.outbound_connections: list[int] = []

	@property
	def parent(self) -> Room:
		return self._parent


class Room(object):
	def __init__(self, parent: Mapping[int, Room]) -> None:
		self._parent: Mapping[int, Room] = parent
		self.name: str = ""
		self.description: str = ""
		self.contents: str = ""
		self.note: str = ""
		self.terrain: str = TERRAIN_TYPE[0]
		self.light: str = LIGHT_TYPE[0]
		self.alignment: str = ALIGNMENT_TYPE[0]
		self.portable: str = PORTABLE_TYPE[0]
		self.ridable: str = RIDABLE_TYPE[0]
		self.sundeath: str = SUN_DEATH_TYPE[0]
		self.mob_flags: set[str] = set()
		self.load_flags: set[str] = set()
		self.updated: bool = False
		self.coordinates: Coordinates = Coordinates()
		self._exits: dict[str, Exit] = OrderedDict()

	@property
	def x(self) -> int:
		return self.coordinates.x

	@x.setter
	def x(self, value: int) -> None:
		self.coordinates.x = int(value)

	@property
	def y(self) -> int:
		return self.coordinates.y

	@y.setter
	def y(self, value: int) -> None:
		self.coordinates.y = int(value)

	@property
	def z(self) -> int:
		return self.coordinates.z

	@z.setter
	def z(self, value: int) -> None:
		self.coordinates.z = int(value)

	@property
	def parent(self) -> Mapping[int, Room]:
		return self._parent

	@property
	def id(self) -> Union[int, None]:
		for vnum, room in self.parent.items():
			if room is self:
				return vnum
		else:
			return None

	@property
	def exits(self) -> dict[str, Exit]:
		return {
			direction: self._exits[direction]
			for direction in self._exits
			if self._exits and self._exits[direction].exit_flags
		}
