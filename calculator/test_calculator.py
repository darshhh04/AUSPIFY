import unittest

from calculator import calculate, format_number


class TestCalculate(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(calculate(2, "+", 3), 5)

    def test_subtraction(self):
        self.assertEqual(calculate(10, "-", 4), 6)

    def test_multiplication(self):
        self.assertEqual(calculate(6, "×", 7), 42)

    def test_division(self):
        self.assertEqual(calculate(9, "÷", 3), 3)

    def test_decimal_division(self):
        self.assertEqual(calculate(1, "÷", 4), 0.25)

    def test_negative_numbers(self):
        self.assertEqual(calculate(-5, "+", 2), -3)

    def test_divide_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            calculate(5, "÷", 0)

    def test_unknown_operator(self):
        with self.assertRaises(ValueError):
            calculate(1, "^", 2)


class TestFormatNumber(unittest.TestCase):
    def test_whole_number_has_no_decimal(self):
        self.assertEqual(format_number(5.0), "5")

    def test_float_rounding_error_is_hidden(self):
        self.assertEqual(format_number(0.1 + 0.2), "0.3")

    def test_negative_decimal(self):
        self.assertEqual(format_number(-2.5), "-2.5")

    def test_very_large_number(self):
        self.assertEqual(format_number(1e20), "1e+20")

    def test_infinity_is_rejected(self):
        with self.assertRaises(OverflowError):
            format_number(float("inf"))


if __name__ == "__main__":
    unittest.main()