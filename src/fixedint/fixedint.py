"""fixedint.py

Implement the FixedInt class factory.
"""

from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Dict, Optional, Tuple, Type, TypeVar


class FixedIntType(int, metaclass=ABCMeta):
    """
    Proxy base class for the internal `FixedIntInstance` class defined
    and returned from `FixedInt()`.  This class is made available for
    use as a type hint and for inheritance type checking like::

        fixed_num = FixedInt(12)(65)
        if isinstance(fixed_num, FixedIntType):
            print("fixed_num is a fixed size integer.")

    This class is also a singleton class manager for all
    `FixedIntInstance` classes created during runtime.  This ensures
    that the classes of numbers with the same (size, signed) properties
    are one and the same::

        num1 = FixedInt(36, signed=False)(450)
        num2 = FixedInt(36, signed=False)(2744)
        print(type(num1) is type(num2))  # True
    """
    # Define interface of a FixedIntInstance so clients using the
    # FixedIntType type hint do not get errors.

    SIZE: int = NotImplemented
    SIGNED: bool = NotImplemented
    MAX_VALUE: int = NotImplemented
    MIN_VALUE: int = NotImplemented

    @abstractmethod
    def __init__(self, value: int) -> None:
        pass

    @abstractmethod
    def as_binary(self) -> str:
        pass

    @abstractmethod
    def as_decimal(self) -> int:
        pass

    # Singleton management here.

    _classes: Dict[Tuple[int, bool], Type["FixedIntType"]] = {}

    @classmethod
    def get_class(cls, size: int, signed: bool
                  ) -> Optional[Type["FixedIntType"]]:
        return cls._classes.get((size, signed))

    @classmethod
    def add_class(cls, new_cls: Type["FixedIntType"]) -> None:
        key = (new_cls.SIZE, new_cls.SIGNED)
        cls._classes[key] = new_cls


def FixedInt(size: int, signed: bool) -> Type[FixedIntType]:
    """Class factory for int subclasses with fixed number of bits."""

    if not (isinstance(size, int) and size > 0):
        raise ValueError("Number of bits must be a positive integer.")

    # Class already interned
    cls =  FixedIntType.get_class(size, signed)
    if cls is not None:
        return cls

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

    class FixedIntInstance(FixedIntType):
        SIZE: int = size
        SIGNED: bool = signed
        MAX_VALUE: int = calculate_max_value()
        MIN_VALUE: int = calculate_min_value()

        def __new__(cls, value: int) -> "FixedIntInstance":
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

        def __add__(self, other: Any) -> "FixedIntInstance":
            return operation_wrapper(self, other,
                                     lambda x, y: x + y,
                                     self.__class__)

        def __radd__(self, other: T) -> T:
            return operation_wrapper(self, other,
                                     lambda x, y: y + x,
                                     other.__class__)

        def __sub__(self, other: Any) -> "FixedIntInstance":
            return operation_wrapper(self, other,
                                     lambda x, y: x - y,
                                     self.__class__)

        def __rsub__(self, other: T) -> T:
            return operation_wrapper(self, other,
                                     lambda x, y: y - x,
                                     other.__class__)

        def __mul__(self, other: Any) -> "FixedIntInstance":
            return operation_wrapper(self, other,
                                     lambda x, y: x * y,
                                     self.__class__)

        def __rmul__(self, other: T) -> T:
            return operation_wrapper(self, other,
                                     lambda x, y: y * x,
                                     other.__class__)

        def __truediv__(self, other: Any) -> "FixedIntInstance":
            return operation_wrapper(self, other,
                                     lambda x, y: x / y,
                                     self.__class__)

        def __rtruediv__(self, other: T) -> T:
            return operation_wrapper(self, other,
                                     lambda x, y: y / x,
                                     other.__class__)

        def __floordiv__(self, other: Any) -> "FixedIntInstance":
            return operation_wrapper(self, other,
                                     lambda x, y: x // y,
                                     self.__class__)

        def __rfloordiv__(self, other: T) -> T:
            return operation_wrapper(self, other,
                                     lambda x, y: y // x,
                                     other.__class__)

        def __mod__(self, other: Any) -> "FixedIntInstance":
            return operation_wrapper(self, other,
                                     lambda x, y: x % y,
                                     self.__class__)

        def __rmod__(self, other: T) -> T:
            return operation_wrapper(self, other,
                                     lambda x, y: y % x,
                                     other.__class__)

        def __neg__(self) -> "FixedIntInstance":
            twos_complement = ~self.real + 1
            return self.__class__(twos_complement)

        def __abs__(self) -> "FixedIntInstance":
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

    # Intern the class we just defined
    FixedIntType.add_class(FixedIntInstance)

    return FixedIntInstance


def FixedSignedInt(size: int) -> Type[FixedIntType]:
    return FixedInt(size, signed=True)


def FixedUnsignedInt(size: int) -> Type[FixedIntType]:
    return FixedInt(size, signed=False)
