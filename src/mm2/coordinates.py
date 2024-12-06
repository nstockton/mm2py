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

"""Map coordinates."""

# Future Modules:
from __future__ import annotations

# Built-in Modules:
import operator
import sys
from collections.abc import Callable, Iterator, Sequence
from typing import Union, overload


if sys.version_info >= (3, 11):
	from typing import Self
else:
	from typing_extensions import Self


class Coordinates(Sequence[int]):  # NOQA: PLR0904
	"""Room coordinates."""

	__slots__: tuple[str, str, str] = ("x", "y", "z")

	def __init__(self, x: int = 0, y: int = 0, z: int = 0) -> None:
		"""
		Defines the constructor.

		Args:
			x: The x coordinate.
			y: The y coordinate.
			z: The z coordinate.
		"""
		self.x: int = int(x)
		self.y: int = int(y)
		self.z: int = int(z)

	@overload
	def __getitem__(self, i: int) -> int:
		pass

	@overload
	def __getitem__(self, i: slice) -> Sequence[int]:
		pass

	def __getitem__(self, i: Union[int, slice]) -> Union[int, Sequence[int]]:
		return (self.x, self.y, self.z)[i]

	def __iter__(self) -> Iterator[int]:
		yield self.x
		yield self.y
		yield self.z

	def __len__(self) -> int:
		return 3

	def __setitem__(self, i: int, value: int) -> None:
		x, y, z = range(3)
		if i == x:
			self.x = value
		elif i == y:
			self.y = value
		elif i == z:
			self.z = value
		else:
			raise IndexError

	def __repr__(self) -> str:
		return f"{type(self).__name__}({self.x}, {self.y}, {self.z})"

	def __hash__(self) -> int:
		return hash(tuple(self))

	def __eq__(self, other: object) -> bool:
		if isinstance(other, Sequence) and len(other) == len(self):
			return bool(self.x == other[0] and self.y == other[1] and self.z == other[2])
		return False

	def __ne__(self, other: object) -> bool:
		if isinstance(other, Sequence) and len(other) == len(self):
			return bool(self.x != other[0] or self.y != other[1] or self.z != other[2])
		return True

	def _operator(self, other: Sequence[int], func: Callable[[int, int], int]) -> Self:
		if isinstance(other, Coordinates):
			return type(self)(func(self.x, other.x), func(self.y, other.y), func(self.z, other.z))
		return type(self)(func(self.x, other[0]), func(self.y, other[1]), func(self.z, other[2]))

	def _roperator(self, other: Sequence[int], func: Callable[[int, int], int]) -> Self:
		if isinstance(other, Coordinates):
			return type(self)(func(other.x, self.x), func(other.y, self.y), func(other.z, self.z))
		return type(self)(func(other[0], self.x), func(other[1], self.y), func(other[2], self.z))

	def _ioperator(self, other: Sequence[int], func: Callable[[int, int], int]) -> Self:
		if isinstance(other, Coordinates):
			self.x = func(self.x, other.x)
			self.y = func(self.y, other.y)
			self.z = func(self.z, other.z)
		else:
			self.x = func(self.x, other[0])
			self.y = func(self.y, other[1])
			self.z = func(self.z, other[2])
		return self

	def __add__(self, other: Sequence[int]) -> Self:
		return self._operator(other, operator.add)

	__radd__ = __add__

	def __iadd__(self, other: Sequence[int]) -> Self:
		return self._ioperator(other, operator.add)

	def __sub__(self, other: Sequence[int]) -> Self:
		return self._operator(other, operator.sub)

	def __rsub__(self, other: Sequence[int]) -> Self:
		return self._roperator(other, operator.sub)

	def __isub__(self, other: Sequence[int]) -> Self:
		return self._ioperator(other, operator.sub)

	def __mul__(self, other: Sequence[int]) -> Self:
		return self._operator(other, operator.mul)

	__rmul__ = __mul__

	def __imul__(self, other: Sequence[int]) -> Self:
		return self._ioperator(other, operator.mul)

	def __floordiv__(self, other: Sequence[int]) -> Self:
		return self._operator(other, operator.floordiv)

	def __rfloordiv__(self, other: Sequence[int]) -> Self:
		return self._roperator(other, operator.floordiv)

	def __ifloordiv__(self, other: Sequence[int]) -> Self:
		return self._ioperator(other, operator.floordiv)

	def __truediv__(self, other: Sequence[int]) -> Self:
		return self._operator(other, operator.truediv)

	def __rtruediv__(self, other: Sequence[int]) -> Self:
		return self._roperator(other, operator.truediv)

	def __itruediv__(self, other: Sequence[int]) -> Self:
		return self._ioperator(other, operator.truediv)

	def __mod__(self, other: Sequence[int]) -> Self:
		return self._operator(other, operator.mod)

	def __rmod__(self, other: Sequence[int]) -> Self:
		return self._roperator(other, operator.mod)

	def __pow__(self, other: Sequence[int]) -> Self:
		return self._operator(other, operator.pow)

	def __rpow__(self, other: Sequence[int]) -> Self:
		return self._roperator(other, operator.pow)

	def __lshift__(self, other: Sequence[int]) -> Self:
		return self._operator(other, operator.lshift)

	def __rlshift__(self, other: Sequence[int]) -> Self:
		return self._roperator(other, operator.lshift)

	def __rshift__(self, other: Sequence[int]) -> Self:
		return self._operator(other, operator.rshift)

	def __rrshift__(self, other: Sequence[int]) -> Self:
		return self._roperator(other, operator.rshift)

	def __and__(self, other: Sequence[int]) -> Self:
		return self._operator(other, operator.and_)

	__rand__ = __and__

	def __or__(self, other: Sequence[int]) -> Self:
		return self._operator(other, operator.or_)

	__ror__ = __or__

	def __xor__(self, other: Sequence[int]) -> Self:
		return self._operator(other, operator.xor)

	__rxor__ = __xor__

	def __neg__(self) -> Self:
		return type(self)(operator.neg(self.x), operator.neg(self.y), operator.neg(self.z))

	def __pos__(self) -> Self:
		return type(self)(operator.pos(self.x), operator.pos(self.y), operator.pos(self.z))

	def __abs__(self) -> Self:
		return type(self)(abs(self.x), abs(self.y), abs(self.z))

	def __invert__(self) -> Self:
		return type(self)(-self.x, -self.y, -self.z)
