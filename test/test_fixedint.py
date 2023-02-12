#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_fixedint.py

Unit tester program for the FixedInt class factory.
"""

import unittest
from typing import Any, Callable, Type

from fixedint import FixedInt, FixedIntType

__author__ = "Vincent Lin"

Int8 = FixedInt(8, signed=True)
UInt8 = FixedInt(8, signed=False)

Int12 = FixedInt(12, signed=True)
UInt12 = FixedInt(12, signed=False)


class TestFixedInt(unittest.TestCase):
    def test_signed_max(self) -> None:
        self.assertEqual(Int8.MAX_VALUE, 127)

    def test_signed_min(self) -> None:
        self.assertEqual(Int8.MIN_VALUE, -128)

    def test_unsigned_max(self) -> None:
        self.assertEqual(UInt8.MAX_VALUE, 255)

    def test_unsigned_min(self) -> None:
        self.assertEqual(UInt8.MIN_VALUE, 0)

    def test_as_binary(self) -> None:
        num = UInt8(188)
        binary = num.as_binary()
        self.assertEqual(binary, "10111100")

    def test_as_decimal(self) -> None:
        num = Int8(-88)
        decimal = num.as_decimal()
        self.assertEqual(decimal, -88)

    def test_invalid_sizes(self) -> None:
        with self.assertRaises(ValueError):
            FixedInt(0)
        with self.assertRaises(ValueError):
            FixedInt(-57)
        with self.assertRaises(ValueError):
            FixedInt(4.3)  # type: ignore

    def _assert_equals_combos(self, num: int, cls: Type[FixedIntType]
                              ) -> None:
        fixed = cls(num)
        self.assertEqual(fixed, cls(num))
        self.assertEqual(fixed, num)
        self.assertEqual(num, fixed)

    def test_equals_combos(self) -> None:
        self._assert_equals_combos(12, Int8)

    def _assert_not_equals_combos(self, num: int, cls: Type[FixedIntType]
                                  ) -> None:
        fixed = cls(num + 1)
        self.assertNotEqual(fixed, Int8(num))
        self.assertNotEqual(fixed, num)
        self.assertNotEqual(num, fixed)

    def test_not_equals_combos(self) -> None:
        self._assert_not_equals_combos(12, Int8)

    def _assert_all_cmps(self, num1: int, num2: int) -> None:
        self.assertLess(num1, num2)
        self.assertGreater(num2, num1)
        self.assertLessEqual(num1, num2)
        self.assertLessEqual(num2, num2)
        self.assertGreaterEqual(num2, num1)
        self.assertGreaterEqual(num2, num2)

    def test_fixed_cmp_fixed(self) -> None:
        num1 = Int8(-52)
        num2 = Int8(17)
        self._assert_all_cmps(num1, num2)

    def test_fixed_cmp_int(self) -> None:
        num1 = Int8(-52)
        num2 = 17
        self._assert_all_cmps(num1, num2)

    def test_int_cmp_fixed(self) -> None:
        num1 = -52
        num2 = Int8(17)
        self._assert_all_cmps(num1, num2)

    def test_init_overflow(self) -> None:
        num = Int8(200)
        self.assertEqual(num, -56)

    def test_init_underflow(self) -> None:
        num = Int8(-300)
        self.assertEqual(num, -44)

    def _assert_operation_combos(self,
                                 num1: int,
                                 num2: int,
                                 operation: Callable[[Any, Any], Any],
                                 cls: Type[FixedIntType]
                                 ) -> None:
        fixed1 = cls(num1)
        fixed2 = cls(num2)
        answer = operation(num1, num2)

        fixed_fixed = operation(fixed1, fixed2)
        self.assertEqual(fixed_fixed, answer)
        self.assertIs(type(fixed_fixed), cls)

        fixed_int = operation(fixed1, num2)
        self.assertEqual(fixed_int, answer)
        self.assertIs(type(fixed_int), cls)

        int_fixed = operation(num1, fixed2)
        self.assertEqual(int_fixed, answer)
        self.assertIs(type(int_fixed), int)

    def test_add_combos(self) -> None:
        self._assert_operation_combos(25, 36, lambda x, y: x + y, Int8)

    def test_sub_combos(self) -> None:
        self._assert_operation_combos(25, 36, lambda x, y: x - y, Int8)

    def test_mul_combos(self) -> None:
        # NOTE: Don't use big numbers here or they're overflow, and
        # we're not testing for that here.  The answer computed in the
        # helper will not match with the overflowed value, even if it
        # overflowed correctly.
        self._assert_operation_combos(13, 6, lambda x, y: x * y, Int8)

    def test_truediv_combos(self) -> None:
        self._assert_operation_combos(100, 20, lambda x, y: x / y, Int8)

    def test_floordiv_combos(self) -> None:
        self._assert_operation_combos(88, 20, lambda x, y: x // y, Int8)

    def test_mod_combos(self) -> None:
        self._assert_operation_combos(56, 3, lambda x, y: x % y, Int8)

    def test_add_overflow(self) -> None:
        num1 = Int8(100)
        num2 = Int8(150)
        self.assertEqual(num1 + num2, -6)

    def test_add_underflow(self) -> None:
        num1 = Int8(-100)
        num2 = Int8(-150)
        self.assertEqual(num1 + num2, 6)

    def test_nested_init(self) -> None:
        self.assertEqual(Int8(Int8(-267)), -11)

    def _assert_cross_fixed_combos(self,
                                   fixed1: FixedIntType,
                                   fixed2: FixedIntType,
                                   operation: Callable[[Any, Any], Any]
                                   ) -> None:
        cls1 = type(fixed1)
        cls2 = type(fixed2)

        decimal1 = fixed1.as_decimal()
        decimal2 = fixed2.as_decimal()

        fixed12 = operation(fixed1, fixed2)
        answer12 = cls1(operation(decimal1, decimal2))
        self.assertEqual(fixed12, answer12)
        self.assertIs(type(fixed12), type(fixed1))

        fixed21 = operation(fixed2, fixed1)
        answer21 = cls2(operation(decimal2, decimal1))
        self.assertEqual(fixed21, answer21)
        self.assertIs(type(fixed21), type(fixed2))

    def test_add_cross_fixed(self) -> None:
        fixed1 = UInt8(100)
        fixed2 = UInt12(3875)
        self._assert_cross_fixed_combos(fixed1, fixed2, lambda x, y: x + y)

    def test_sub_cross_fixed(self) -> None:
        fixed1 = UInt8(100)
        fixed2 = UInt12(3875)
        self._assert_cross_fixed_combos(fixed1, fixed2, lambda x, y: x - y)

    def test_mul_cross_fixed(self) -> None:
        fixed1 = UInt8(100)
        fixed2 = UInt12(3875)
        self._assert_cross_fixed_combos(fixed1, fixed2, lambda x, y: x * y)

    def test_truediv_cross_fixed(self) -> None:
        fixed1 = UInt8(3875)
        fixed2 = UInt12(100)
        self._assert_cross_fixed_combos(fixed1, fixed2, lambda x, y: x / y)

    def test_floordiv_cross_fixed(self) -> None:
        fixed1 = UInt8(3875)
        fixed2 = UInt12(100)
        self._assert_cross_fixed_combos(fixed1, fixed2, lambda x, y: x // y)

    def test_inheritance(self) -> None:
        fixed = UInt12(1000)
        self.assertIsInstance(fixed, FixedIntType)
        self.assertIsInstance(fixed, int)

    def test_type_internment(self) -> None:
        fixed1 = FixedInt(36, signed=False)(450)
        fixed2 = FixedInt(36, signed=False)(2744)
        self.assertIs(type(fixed1), type(fixed2))


if __name__ == "__main__":
    unittest.main()
