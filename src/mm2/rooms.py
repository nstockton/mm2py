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

"""Room definitions."""

# Future Modules:
from __future__ import annotations

# Built-in Modules:
from collections import OrderedDict
from collections.abc import Mapping
from enum import Enum, Flag, auto
from typing import Union

# Local Modules:
from .coordinates import Coordinates


class MobFlags(Flag):
	RENT = auto()
	SHOP = auto()
	WEAPON_SHOP = auto()
	ARMOUR_SHOP = auto()
	FOOD_SHOP = auto()
	PET_SHOP = auto()
	GUILD = auto()
	SCOUT_GUILD = auto()
	MAGE_GUILD = auto()
	CLERIC_GUILD = auto()
	WARRIOR_GUILD = auto()
	RANGER_GUILD = auto()
	AGGRESSIVE_MOB = auto()
	QUEST_MOB = auto()
	PASSIVE_MOB = auto()
	ELITE_MOB = auto()
	SUPER_MOB = auto()
	MILKABLE = auto()
	RATTLESNAKE = auto()


class LoadFlags(Flag):
	TREASURE = auto()
	ARMOUR = auto()
	WEAPON = auto()
	WATER = auto()
	FOOD = auto()
	HERB = auto()
	KEY = auto()
	MULE = auto()
	HORSE = auto()
	PACK_HORSE = auto()
	TRAINED_HORSE = auto()
	ROHIRRIM = auto()
	WARG = auto()
	BOAT = auto()
	ATTENTION = auto()
	TOWER = auto()  # Player can watch surrounding rooms from this one.
	CLOCK = auto()
	MAIL = auto()
	STABLE = auto()
	WHITE_WORD = auto()
	DARK_WORD = auto()
	EQUIPMENT = auto()
	COACH = auto()
	FERRY = auto()
	DEATHTRAP = auto()


class ExitFlags(Flag):
	EXIT = auto()
	DOOR = auto()
	ROAD = auto()
	CLIMB = auto()
	RANDOM = auto()
	SPECIAL = auto()
	NO_MATCH = auto()  # Exit not always visible, ignore it when syncing against available exits.
	FLOW = auto()  # Water flow.
	NO_FLEE = auto()
	DAMAGE = auto()
	FALL = auto()
	GUARDED = auto()  # Mobs prevent movement.
	UNMAPPED = auto()


class DoorFlags(Flag):
	HIDDEN = auto()
	NEED_KEY = auto()
	NO_BLOCK = auto()
	NO_BREAK = auto()
	NO_PICK = auto()
	DELAYED = auto()
	CALLABLE = auto()
	KNOCKABLE = auto()
	MAGIC = auto()
	ACTION = auto()  # Action controlled.
	NO_BASH = auto()


class Alignment(Enum):
	UNDEFINED = 0
	GOOD = auto()
	NEUTRAL = auto()
	EVIL = auto()


class Light(Enum):
	UNDEFINED = 0
	DARK = auto()
	LIT = auto()


class Portable(Enum):
	UNDEFINED = 0
	PORTABLE = auto()
	NOT_PORTABLE = auto()


class Ridable(Enum):
	UNDEFINED = 0
	RIDABLE = auto()
	NOT_RIDABLE = auto()


class Sundeath(Enum):
	UNDEFINED = 0
	SUNDEATH = auto()
	NO_SUNDEATH = auto()


class Terrain(Enum):
	UNDEFINED = 0
	BUILDING = auto()  # Note that MMapper still calls this "indoors".
	CITY = auto()
	FIELD = auto()
	FOREST = auto()
	HILLS = auto()
	MOUNTAINS = auto()
	SHALLOWS = auto()  # Note that MMapper still calls this "shallow".
	WATER = auto()
	RAPIDS = auto()
	UNDERWATER = auto()
	ROAD = auto()
	BRUSH = auto()
	TUNNEL = auto()
	CAVERN = auto()


class Exit:
	def __init__(self, parent: Room) -> None:
		self._parent: Room = parent
		self.exit_flags: ExitFlags = ExitFlags(0)
		self.door_flags: DoorFlags = DoorFlags(0)
		self.door_name: str = ""
		self.outbound_connections: list[int] = []

	@property
	def parent(self) -> Room:
		return self._parent


class Room:
	def __init__(self, parent: Mapping[int, Room]) -> None:
		self._parent: Mapping[int, Room] = parent
		self.area: str = ""
		self.name: str = ""
		self.description: str = ""
		self.contents: str = ""
		self.server_id: int = 0
		self.note: str = ""
		self.terrain: Terrain = Terrain(0)
		self.light: Light = Light(0)
		self.alignment: Alignment = Alignment(0)
		self.portable: Portable = Portable(0)
		self.ridable: Ridable = Ridable(0)
		self.sundeath: Sundeath = Sundeath(0)
		self.mob_flags: MobFlags = MobFlags(0)
		self.load_flags: LoadFlags = LoadFlags(0)
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
		return None

	@property
	def exits(self) -> dict[str, Exit]:
		return {direction: ext for direction, ext in self._exits.items() if ext.exit_flags}
