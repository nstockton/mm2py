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

# Local Modules:
from .coordinates import Coordinates


INFO_MARK_SCALE: int = 100
INFO_MARK_TWENTIETH: int = INFO_MARK_SCALE // 20
INFO_MARK_TENTH: int = INFO_MARK_SCALE // 10
INFO_MARK_HALF: int = INFO_MARK_SCALE // 2
INFO_MARK_HALF_ROOM_OFFSET: Coordinates = Coordinates(INFO_MARK_HALF, -INFO_MARK_HALF, 0)  # Note: Y inverted.
INFO_MARK_OFFSET1: Coordinates = Coordinates(0, INFO_MARK_TWENTIETH, 0)
INFO_MARK_OFFSET2: Coordinates = Coordinates(INFO_MARK_TENTH, INFO_MARK_TENTH, 0)
INFO_MARK_TEXT_OFFSET: Coordinates = Coordinates(INFO_MARK_TENTH, 3 * INFO_MARK_TENTH, 0)


INFO_MARK_TYPE: dict[int, str] = {0: "text", 1: "line", 2: "arrow"}
INFO_MARK_TYPE_TO_BITS: dict[str, int] = {v: k for k, v in INFO_MARK_TYPE.items()}

INFO_MARK_CLASS: dict[int, str] = {
	0: "generic",
	1: "herb",
	2: "river",
	3: "place",
	4: "mob",
	5: "comment",
	6: "road",
	7: "object",
	8: "action",
	9: "locality",
}
INFO_MARK_CLASS_TO_BITS: dict[str, int] = {v: k for k, v in INFO_MARK_CLASS.items()}


class InfoMark(object):
	def __init__(self) -> None:
		self.text: str = ""
		self.type: str = INFO_MARK_TYPE[0]
		self.cls: str = INFO_MARK_CLASS[0]
		self.rotation_angle: int = 0
		self.pos1: Coordinates = Coordinates()
		self.pos2: Coordinates = Coordinates()
