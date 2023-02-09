"""fixedint.py

Implement the FixedInt class factory.
"""

from typing import Any, Callable, Type, TypeVar


def FixedInt(size: int, signed: bool = True):
    """Class factory for int subclasses with fixed number of bits."""

    if not (isinstance(size, int) and size > 0):
        raise ValueError("Number of bits must be a positive integer.")

    def calculate_max_value() -> int:
        umax = (1 << size) - 1
        if signed:
            msb_mask = (1 << (size - 1))
            tmax = msb_mask - 1
            return tmax
        return umax

    def calculate_min_value() -> int:
        if signed:
            return -(1 << (size - 1))
        return 0

    T = TypeVar("T")

    class FixedIntType(int):
        SIZE: int = size
        SIGNED: bool = signed
        MAX_VALUE: int = calculate_max_value()
        MIN_VALUE: int = calculate_min_value()

        def __new__(cls, value: int) -> "FixedIntType":
            lower_size_ones = (1 << size) - 1
            lower_bits = int(value) & lower_size_ones
            return super().__new__(cls, lower_bits)

        def __repr__(self) -> str:
            param_list = f"size={self.SIZE}, signed={self.SIGNED}"
            decimal = self.as_decimal()
            return f"FixedInt({param_list})({decimal:_})"

        def __str__(self) -> str:
            return str(self.as_decimal())

        def __eq__(self, other: Any) -> bool:
            return self.as_decimal() == other

        def __lt__(self, other: Any) -> bool:
            return self.as_decimal() < other

        def __gt__(self, other: Any) -> bool:
            return self.as_decimal() > other

        def __le__(self, other: Any) -> bool:
            return self.as_decimal() <= other

        def __ge__(self, other: Any) -> bool:
            return self.as_decimal() >= other

        def __add__(self, other: Any) -> "FixedIntType":
            return operation_wrapper(self, other,
                                     lambda x, y: x + y,
                                     self.__class__)

        def __radd__(self, other: T) -> T:
            return operation_wrapper(self, other,
                                     lambda x, y: y + x,
                                     other.__class__)

        def __sub__(self, other: Any) -> "FixedIntType":
            return operation_wrapper(self, other,
                                     lambda x, y: x - y,
                                     self.__class__)

        def __rsub__(self, other: T) -> T:
            return operation_wrapper(self, other,
                                     lambda x, y: y - x,
                                     other.__class__)

        def __mul__(self, other: Any) -> "FixedIntType":
            return operation_wrapper(self, other,
                                     lambda x, y: x * y,
                                     self.__class__)

        def __rmul__(self, other: T) -> T:
            return operation_wrapper(self, other,
                                     lambda x, y: y * x,
                                     other.__class__)

        def __truediv__(self, other: Any) -> "FixedIntType":
            return operation_wrapper(self, other,
                                     lambda x, y: x / y,
                                     self.__class__)

        def __rtruediv__(self, other: T) -> T:
            return operation_wrapper(self, other,
                                     lambda x, y: y / x,
                                     other.__class__)

        def __floordiv__(self, other: Any) -> "FixedIntType":
            return operation_wrapper(self, other,
                                     lambda x, y: x // y,
                                     self.__class__)

        def __rfloordiv__(self, other: T) -> T:
            return operation_wrapper(self, other,
                                     lambda x, y: y // x,
                                     other.__class__)

        def __mod__(self, other: Any) -> "FixedIntType":
            return operation_wrapper(self, other,
                                     lambda x, y: x % y,
                                     self.__class__)

        def __rmod__(self, other: T) -> T:
            return operation_wrapper(self, other,
                                     lambda x, y: y % x,
                                     other.__class__)

        def __neg__(self) -> "FixedIntType":
            twos_complement = ~self.real + 1
            return self.__class__(twos_complement)

        def __abs__(self) -> "FixedIntType":
            return self.__class__(abs(self.real))

        # NOTE: More operations may need to be overridden, and the above
        # operations may not be fully tested.

        def as_decimal(self) -> int:
            if not signed:
                return self.real
            msb_mask = (1 << (size - 1))
            msb = self.real & msb_mask
            if msb:
                all_ones = (1 << size) - 1
                magnitude = -self.real & all_ones
                return -magnitude
            return self.real

        def as_binary(self) -> str:
            # NOTE: str.removeprefix was not added until 3.9
            return bin(self)[2:].zfill(self.SIZE)

    def operation_wrapper(left: Any,
                          right: Any,
                          binary_operation: Callable[[Any, Any], Any],
                          cls: Type[T]
                          ) -> T:
        """Perform a binary operation between two int-like instances."""
        try:
            return cls(binary_operation(left.real, right.real))
        except AttributeError:
            return NotImplemented

    return FixedIntType
