"""
tests/test_calculator.py
========================
Unit tests for the ``calculator`` module.

Run with::

    pytest tests/test_calculator.py -v

Run with coverage::

    pytest tests/test_calculator.py --cov=calculator --cov-report=term-missing

Run with per-test timing (NFR-1 / AC-10)::

    pytest tests/test_calculator.py --durations=0
"""

import math
import pytest

import calculator
from calculator import (
    DivisionByZeroError,
    DomainError,
    add,
    subtract,
    multiply,
    divide,
    sqrt,
    power,
    log,
    sin,
    cos,
    tan,
)

# ---------------------------------------------------------------------------
# Tolerance used for all floating-point assertions (NFR-4: 6 sig. figs.)
# ---------------------------------------------------------------------------
TOLERANCE = 1e-6


# ===========================================================================
# add
# ===========================================================================

class TestAdd:
    """Tests for calculator.add (FR-1, AC-1)."""

    @pytest.mark.parametrize("a, b, expected", [
        (3.5,  2.0,   5.5),    # AC-1 canonical
        (0.0,  0.0,   0.0),    # zero + zero
        (-1.0, 1.0,   0.0),    # negative + positive
        (-3.0, -4.0, -7.0),    # both negative
        (1,    2,     3),      # int inputs
        (1e10, 1e10,  2e10),   # large values
    ])
    def test_add_happy_path(self, a, b, expected):
        assert add(a, b) == pytest.approx(expected, rel=TOLERANCE)

    @pytest.mark.parametrize("a, b", [
        ("abc", 2),
        (2, "abc"),
        ("abc", "def"),
        (None, 1),
        (1, None),
        ([1], 2),
    ])
    def test_add_type_error(self, a, b):
        """AC-8: non-numeric argument raises TypeError with a message."""
        with pytest.raises(TypeError) as exc_info:
            add(a, b)
        assert str(exc_info.value)  # message must be non-empty


# ===========================================================================
# subtract
# ===========================================================================

class TestSubtract:
    """Tests for calculator.subtract (FR-2, AC-1)."""

    @pytest.mark.parametrize("a, b, expected", [
        (3.5,  2.0,   1.5),    # AC-1 canonical
        (0.0,  0.0,   0.0),
        (5.0,  5.0,   0.0),
        (-1.0, -1.0,  0.0),
        (0.0,  3.0,  -3.0),
        (1,    2,    -1),      # int inputs
    ])
    def test_subtract_happy_path(self, a, b, expected):
        assert subtract(a, b) == pytest.approx(expected, rel=TOLERANCE)

    @pytest.mark.parametrize("a, b", [
        ("abc", 2),
        (2, "abc"),
        (None, 1),
    ])
    def test_subtract_type_error(self, a, b):
        with pytest.raises(TypeError) as exc_info:
            subtract(a, b)
        assert str(exc_info.value)


# ===========================================================================
# multiply
# ===========================================================================

class TestMultiply:
    """Tests for calculator.multiply (FR-3, AC-1)."""

    @pytest.mark.parametrize("a, b, expected", [
        (3.5,  2.0,   7.0),    # AC-1 canonical
        (0.0,  999.0, 0.0),    # multiply by zero
        (-2.0, 3.0,  -6.0),
        (-2.0, -3.0,  6.0),
        (1,    1,     1),      # int inputs
        (1e5,  1e5,   1e10),   # large values
    ])
    def test_multiply_happy_path(self, a, b, expected):
        assert multiply(a, b) == pytest.approx(expected, rel=TOLERANCE)

    @pytest.mark.parametrize("a, b", [
        ("abc", 2),
        (2, "abc"),
        (None, 1),
    ])
    def test_multiply_type_error(self, a, b):
        with pytest.raises(TypeError) as exc_info:
            multiply(a, b)
        assert str(exc_info.value)


# ===========================================================================
# divide
# ===========================================================================

class TestDivide:
    """Tests for calculator.divide (FR-4, AC-2)."""

    @pytest.mark.parametrize("a, b, expected", [
        (10.0,  4.0,   2.5),   # AC-2 canonical
        (0.0,   5.0,   0.0),   # zero dividend
        (-10.0, 2.0,  -5.0),   # negative dividend
        (7.0,  -2.0,  -3.5),   # negative divisor
        (1,     3,     1/3),   # int inputs → float result
        (1e10,  1e5,   1e5),   # large values
    ])
    def test_divide_happy_path(self, a, b, expected):
        assert divide(a, b) == pytest.approx(expected, rel=TOLERANCE)

    def test_divide_by_zero_raises(self):
        """AC-2: divide(a, 0) raises DivisionByZeroError."""
        with pytest.raises(DivisionByZeroError):
            divide(10.0, 0)

    def test_divide_by_zero_float_raises(self):
        with pytest.raises(DivisionByZeroError):
            divide(10.0, 0.0)

    def test_divide_by_zero_is_arithmetic_error(self):
        """DivisionByZeroError must be a subclass of ArithmeticError."""
        with pytest.raises(ArithmeticError):
            divide(1.0, 0)

    @pytest.mark.parametrize("a, b", [
        ("abc", 2),
        (2, "abc"),
        (None, 1),
    ])
    def test_divide_type_error(self, a, b):
        with pytest.raises(TypeError) as exc_info:
            divide(a, b)
        assert str(exc_info.value)


# ===========================================================================
# sqrt
# ===========================================================================

class TestSqrt:
    """Tests for calculator.sqrt (FR-5, AC-3)."""

    @pytest.mark.parametrize("a, expected", [
        (9.0,   3.0),          # AC-3 canonical
        (0.0,   0.0),          # sqrt of zero
        (1.0,   1.0),
        (2.0,   math.sqrt(2)), # irrational
        (4,     2.0),          # int input
        (1e10,  1e5),          # large value
        (0.25,  0.5),          # fractional
    ])
    def test_sqrt_happy_path(self, a, expected):
        assert sqrt(a) == pytest.approx(expected, rel=TOLERANCE)

    def test_sqrt_negative_raises(self):
        """AC-3: sqrt(-1.0) raises DomainError."""
        with pytest.raises(DomainError):
            sqrt(-1.0)

    def test_sqrt_negative_is_value_error(self):
        """DomainError must be a subclass of ValueError."""
        with pytest.raises(ValueError):
            sqrt(-1.0)

    @pytest.mark.parametrize("a", ["abc", None, []])
    def test_sqrt_type_error(self, a):
        with pytest.raises(TypeError) as exc_info:
            sqrt(a)
        assert str(exc_info.value)


# ===========================================================================
# power
# ===========================================================================

class TestPower:
    """Tests for calculator.power (FR-6, AC-4)."""

    @pytest.mark.parametrize("base, exponent, expected", [
        (2.0,   10.0,   1024.0),   # AC-4 canonical
        (2.0,  -1.0,    0.5),      # AC-4 negative exponent
        (0.0,   5.0,    0.0),      # zero base
        (1.0,   999.0,  1.0),      # base 1
        (5.0,   0.0,    1.0),      # exponent 0
        (-2.0,  3.0,   -8.0),      # negative base, odd exponent
        (4.0,   0.5,    2.0),      # fractional exponent (sqrt)
        (10,    3,      1000.0),   # int inputs
    ])
    def test_power_happy_path(self, base, exponent, expected):
        assert power(base, exponent) == pytest.approx(expected, rel=TOLERANCE)

    @pytest.mark.parametrize("base, exponent", [
        ("abc", 2),
        (2, "abc"),
        (None, 1),
    ])
    def test_power_type_error(self, base, exponent):
        with pytest.raises(TypeError) as exc_info:
            power(base, exponent)
        assert str(exc_info.value)


# ===========================================================================
# log (natural logarithm)
# ===========================================================================

class TestLog:
    """Tests for calculator.log (FR-7, AC-5)."""

    @pytest.mark.parametrize("a, expected", [
        (1.0,       0.0),           # AC-5 canonical: log(1) = 0
        (math.e,    1.0),           # log(e) = 1
        (math.e**2, 2.0),           # log(e²) = 2
        (10.0,      math.log(10)),  # log(10)
        (0.5,       math.log(0.5)), # fractional argument
        (1e10,      math.log(1e10)),# large value
    ])
    def test_log_happy_path(self, a, expected):
        assert log(a) == pytest.approx(expected, rel=TOLERANCE)

    def test_log_zero_raises(self):
        """AC-5: log(0) raises DomainError."""
        with pytest.raises(DomainError):
            log(0)

    def test_log_negative_raises(self):
        """AC-5: log(-5.0) raises DomainError."""
        with pytest.raises(DomainError):
            log(-5.0)

    def test_log_domain_error_is_value_error(self):
        with pytest.raises(ValueError):
            log(-1.0)

    @pytest.mark.parametrize("a", ["abc", None, []])
    def test_log_type_error(self, a):
        with pytest.raises(TypeError) as exc_info:
            log(a)
        assert str(exc_info.value)


# ===========================================================================
# sin
# ===========================================================================

class TestSin:
    """Tests for calculator.sin (FR-8, AC-6, AC-7)."""

    @pytest.mark.parametrize("a, expected", [
        (0.0,           0.0),                   # AC-6
        (math.pi / 2,   1.0),                   # sin(π/2) = 1
        (math.pi,       0.0),                   # sin(π) ≈ 0
        (math.pi / 4,   math.sqrt(2) / 2),      # AC-7: sin(π/4) = √2/2
        (-math.pi / 2, -1.0),                   # negative angle
        (2 * math.pi,   0.0),                   # full rotation
        (1,             math.sin(1)),            # int input
    ])
    def test_sin_happy_path(self, a, expected):
        assert sin(a) == pytest.approx(expected, abs=TOLERANCE)

    @pytest.mark.parametrize("a", ["abc", None, []])
    def test_sin_type_error(self, a):
        with pytest.raises(TypeError) as exc_info:
            sin(a)
        assert str(exc_info.value)


# ===========================================================================
# cos
# ===========================================================================

class TestCos:
    """Tests for calculator.cos (FR-8, AC-6, AC-7)."""

    @pytest.mark.parametrize("a, expected", [
        (0.0,           1.0),                   # AC-6
        (math.pi / 2,   0.0),                   # cos(π/2) ≈ 0
        (math.pi,      -1.0),                   # cos(π) = -1
        (math.pi / 4,   math.sqrt(2) / 2),      # AC-7: cos(π/4) = √2/2
        (-math.pi,     -1.0),                   # negative angle
        (2 * math.pi,   1.0),                   # full rotation
        (1,             math.cos(1)),            # int input
    ])
    def test_cos_happy_path(self, a, expected):
        assert cos(a) == pytest.approx(expected, abs=TOLERANCE)

    @pytest.mark.parametrize("a", ["abc", None, []])
    def test_cos_type_error(self, a):
        with pytest.raises(TypeError) as exc_info:
            cos(a)
        assert str(exc_info.value)


# ===========================================================================
# tan
# ===========================================================================

class TestTan:
    """Tests for calculator.tan (FR-8, FR-9, AC-6, AC-7)."""

    @pytest.mark.parametrize("a, expected", [
        (0.0,           0.0),           # AC-6
        (math.pi / 4,   1.0),           # AC-7: tan(π/4) = 1
        (-math.pi / 4, -1.0),           # negative angle
        (math.pi,       0.0),           # tan(π) ≈ 0
        (1,             math.tan(1)),   # int input
    ])
    def test_tan_happy_path(self, a, expected):
        assert tan(a) == pytest.approx(expected, abs=TOLERANCE)

    def test_tan_at_pi_over_2_raises(self):
        """FR-9: tan(π/2) raises DomainError (cos ≈ 6.12e-17 < 1e-10)."""
        with pytest.raises(DomainError):
            tan(math.pi / 2)

    def test_tan_at_neg_pi_over_2_raises(self):
        """FR-9: tan(-π/2) raises DomainError."""
        with pytest.raises(DomainError):
            tan(-math.pi / 2)

    def test_tan_at_3pi_over_2_raises(self):
        """FR-9: tan(3π/2) raises DomainError."""
        with pytest.raises(DomainError):
            tan(3 * math.pi / 2)

    def test_tan_domain_error_is_value_error(self):
        with pytest.raises(ValueError):
            tan(math.pi / 2)

    @pytest.mark.parametrize("a", ["abc", None, []])
    def test_tan_type_error(self, a):
        with pytest.raises(TypeError) as exc_info:
            tan(a)
        assert str(exc_info.value)


# ===========================================================================
# Exception hierarchy sanity checks
# ===========================================================================

class TestExceptionHierarchy:
    """Verify custom exceptions inherit from the correct base classes."""

    def test_division_by_zero_error_is_arithmetic_error(self):
        assert issubclass(DivisionByZeroError, ArithmeticError)

    def test_domain_error_is_value_error(self):
        assert issubclass(DomainError, ValueError)

    def test_division_by_zero_error_message(self):
        with pytest.raises(DivisionByZeroError, match="zero"):
            divide(1.0, 0)

    def test_domain_error_sqrt_message(self):
        with pytest.raises(DomainError, match="non-negative"):
            sqrt(-1.0)

    def test_domain_error_log_message(self):
        with pytest.raises(DomainError, match="positive"):
            log(0)

    def test_domain_error_tan_message(self):
        with pytest.raises(DomainError, match=r"π/2"):
            tan(math.pi / 2)

    def test_type_error_message_non_empty(self):
        with pytest.raises(TypeError) as exc_info:
            add("x", 1)
        assert len(str(exc_info.value)) > 0


# ===========================================================================
# Acceptance-criteria smoke tests (explicit AC mapping)
# ===========================================================================

class TestAcceptanceCriteria:
    """Direct mapping to BRD acceptance criteria AC-1 through AC-8."""

    def test_ac1_add(self):
        assert add(3.5, 2.0) == pytest.approx(5.5, rel=TOLERANCE)

    def test_ac1_subtract(self):
        assert subtract(3.5, 2.0) == pytest.approx(1.5, rel=TOLERANCE)

    def test_ac1_multiply(self):
        assert multiply(3.5, 2.0) == pytest.approx(7.0, rel=TOLERANCE)

    def test_ac2_divide_happy(self):
        assert divide(10.0, 4.0) == pytest.approx(2.5, rel=TOLERANCE)

    def test_ac2_divide_by_zero(self):
        with pytest.raises(DivisionByZeroError):
            divide(10.0, 0)

    def test_ac3_sqrt_happy(self):
        assert sqrt(9.0) == pytest.approx(3.0, rel=TOLERANCE)

    def test_ac3_sqrt_negative(self):
        with pytest.raises(DomainError):
            sqrt(-1.0)

    def test_ac4_power_positive_exponent(self):
        assert power(2.0, 10.0) == pytest.approx(1024.0, rel=TOLERANCE)

    def test_ac4_power_negative_exponent(self):
        assert power(2.0, -1.0) == pytest.approx(0.5, rel=TOLERANCE)

    def test_ac5_log_one(self):
        assert log(1.0) == pytest.approx(0.0, abs=TOLERANCE)

    def test_ac5_log_zero(self):
        with pytest.raises(DomainError):
            log(0)

    def test_ac5_log_negative(self):
        with pytest.raises(DomainError):
            log(-5.0)

    def test_ac6_sin_zero(self):
        assert sin(0.0) == pytest.approx(0.0, abs=TOLERANCE)

    def test_ac6_cos_zero(self):
        assert cos(0.0) == pytest.approx(1.0, rel=TOLERANCE)

    def test_ac6_tan_zero(self):
        assert tan(0.0) == pytest.approx(0.0, abs=TOLERANCE)

    def test_ac7_sin_pi_over_4(self):
        assert sin(math.pi / 4) == pytest.approx(math.sqrt(2) / 2, rel=TOLERANCE)

    def test_ac7_cos_pi_over_4(self):
        assert cos(math.pi / 4) == pytest.approx(math.sqrt(2) / 2, rel=TOLERANCE)

    def test_ac7_tan_pi_over_4(self):
        assert tan(math.pi / 4) == pytest.approx(1.0, rel=TOLERANCE)

    @pytest.mark.parametrize("fn", [add, subtract, multiply, divide,
                                     sqrt, power, log, sin, cos, tan])
    def test_ac8_type_error_for_string_arg(self, fn):
        """AC-8: every operation raises TypeError for a string argument."""
        import inspect
        sig = inspect.signature(fn)
        n_params = len(sig.parameters)
        args = ("abc",) + (1.0,) * (n_params - 1)
        with pytest.raises(TypeError) as exc_info:
            fn(*args)
        assert str(exc_info.value)  # message must be non-empty
