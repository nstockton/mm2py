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


import operator


def is_iterable(obj):
	try:
		iter(obj)
	except TypeError:
		return False
	else:
		return True


class Coordinates(object):
	__slots__ = ("x", "y", "z")

	def __init__(self, x_or_iterable=None, y=None, z=None):
		if x_or_iterable is not None:
			if y is None or z is None:
				if hasattr(x_or_iterable, "x") and hasattr(x_or_iterable, "y") and hasattr(x_or_iterable, "z"):
					self.x = int(x_or_iterable.x)
					self.y = int(x_or_iterable.y)
					self.z = int(x_or_iterable.z)
				else:
					self.x, self.y, self.z = (int(i) for i in x_or_iterable[:3])
			else:
				self.x = int(x_or_iterable)
				self.y = int(y)
				self.z = int(z)
		else:
			self.x = 0
			self.y = 0
			self.z = 0

	def __getitem__(self, i):
		return (self.x, self.y, self.z)[i]

	def __iter__(self):
		yield self.x
		yield self.y
		yield self.z

	def __len__(self):
		return 3

	def __setitem__(self, i, value):
		if i == 0:
			self.x = value
		elif i == 1:
			self.y = value
		elif i == 2:
			self.z = value
		else:
			raise IndexError()

	def __repr__(self):
		return "Coordinates({x}, {y}, {z})".format(x=self.x, y=self.y, z=self.z)

	def __eq__(self, other):
		if is_iterable(other) and len(other) == 3:
			return self.x == other[0] and self.y == other[1] and self.z == other[2]
		else:
			return False

	def __ne__(self, other):
		if is_iterable(other) and len(other) == 3:
			return self.x != other[0] or self.y != other[1] or self.z != other[2]
		else:
			return True

	def __nonzero__(self):
		return self.x != 0 or self.y != 0 or self.z != 0

	def _operate(self, other, func):
		if isinstance(other, Coordinates):
			return Coordinates(func(self.x, other.x), func(self.y, other.y), func(self.z, other.z))
		elif is_iterable(other):
			return Coordinates(func(self.x, other[0]), func(self.y, other[1]), func(self.z, other[2]))
		else:
			return Coordinates(func(self.x, other), func(self.y, other), func(self.z, other))

	def _roperate(self, other, func):
		if is_iterable(other):
			return Coordinates(func(other[0], self.x), func(other[1], self.y), func(other[2], self.z))
		else:
			return Coordinates(func(other, self.x), func(other, self.y), func(other, self.z))

	def _ioperator(self, other, func):
		if is_iterable(other):
			self.x = func(self.x, other[0])
			self.y = func(self.y, other[1])
			self.z = func(self.z, other[2])
		else:
			self.x = func(self.x, other)
			self.y = func(self.y, other)
			self.z = func(self.z, other)
		return self

	def __add__(self, other):
		return self._operator(other, operator.add)

	__radd__ = __add__

	def __iadd__(self, other):
		return self._ioperator(other, operator.add)

	def __sub__(self, other):
		return self._operator(other, operator.sub)

	def __rsub__(self, other):
		return self._roperator(other, operator.sub)

	def __isub__(self, other):
		return self._ioperator(other, operator.sub)

	def __mul__(self, other):
		return self._operator(other, operator.mul)

	__rmul__ = __mul__

	def __imul__(self, other):
		return self._ioperator(other, operator.mul)

	def __div__(self, other):
		return self._operator(other, operator.div)

	def __rdiv__(self, other):
		return self._roperator(other, operator.div)

	def __idiv__(self, other):
		return self._ioperator(other, operator.div)

	def __floordiv__(self, other):
		return self._operator(other, operator.floordiv)

	def __rfloordiv__(self, other):
		return self._roperator(other, operator.floordiv)

	def __ifloordiv__(self, other):
		return self._ioperator(other, operator.floordiv)

	def __truediv__(self, other):
		return self._operator(other, operator.truediv)

	def __rtruediv__(self, other):
		return self._roperator(other, operator.truediv)

	def __itruediv__(self, other):
		return self._ioperator(other, operator.truediv)

	def __mod__(self, other):
		return self._operator(other, operator.mod)

	def __rmod__(self, other):
		return self._roperator(other, operator.mod)

	def __divmod__(self, other):
		return self._operator(other, divmod)

	def __rdivmod__(self, other):
		return self._roperator(other, divmod)

	def __pow__(self, other):
		return self._operator(other, operator.pow)

	def __rpow__(self, other):
		return self._roperator(other, operator.pow)

	def __lshift__(self, other):
		return self._operator(other, operator.lshift)

	def __rlshift__(self, other):
		return self._roperator(other, operator.lshift)

	def __rshift__(self, other):
		return self._operator(other, operator.rshift)

	def __rrshift__(self, other):
		return self._roperator(other, operator.rshift)

	def __and__(self, other):
		return self._operator(other, operator.and_)

	__rand__ = __and__

	def __or__(self, other):
		return self._operator(other, operator.or_)

	__ror__ = __or__

	def __xor__(self, other):
		return self._operator(other, operator.xor)

	__rxor__ = __xor__

	def __neg__(self):
		return Coordinates(operator.neg(self.x), operator.neg(self.y), operator.neg(self.z))

	def __pos__(self):
		return Coordinates(operator.pos(self.x), operator.pos(self.y), operator.pos(self.z))

	def __abs__(self):
		return Coordinates(abs(self.x), abs(self.y), abs(self.z))

	def __invert__(self):
		return Coordinates(-self.x, -self.y, -self.z)
