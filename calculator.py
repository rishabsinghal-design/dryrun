"""
calculator.py — Scientific Calculator Module
=============================================
A stateless, pure-function scientific calculator using only Python's
standard ``math`` library.  No third-party runtime dependencies are
introduced (NFR-5).

Usage::

    import calculator

    calculator.add(3.5, 2.0)        # → 5.5
    calculator.sqrt(9.0)            # → 3.0
    calculator.log(1.0)             # → 0.0
    calculator.sin(0.0)             # → 0.0

Custom exceptions
-----------------
DivisionByZeroError
    Raised by ``divide`` when the divisor is zero.
DomainError
    Raised by ``sqrt``, ``log``, and ``tan`` when the argument is
    outside the function's mathematical domain.
TypeError (built-in)
    Raised by every function when a non-numeric argument is supplied.
"""

import math

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class DivisionByZeroError(ArithmeticError):
    """Raised when ``divide(a, b)`` is called with ``b == 0``."""


class DomainError(ValueError):
    """Raised when an argument is outside a function's mathematical domain.

    Affected operations: ``sqrt`` (negative input), ``log`` (non-positive
    input), ``tan`` (odd multiple of π/2).
    """


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _validate_numeric(*args: object) -> None:
    """Raise ``TypeError`` if any argument is not an ``int`` or ``float``.

    Args:
        *args: The values to validate.

    Raises:
        TypeError: If any value is not numeric, with a descriptive message
            that includes the offending type(s).
    """
    bad = [type(a).__name__ for a in args if not isinstance(a, (int, float))]
    if bad:
        types_str = ", ".join(bad)
        raise TypeError(
            f"Expected numeric arguments (int or float), "
            f"but received: {types_str}"
        )


# ---------------------------------------------------------------------------
# Basic arithmetic
# ---------------------------------------------------------------------------


def add(a: float, b: float) -> float:
    """Return the arithmetic sum of *a* and *b*.

    Args:
        a: First operand (int or float).
        b: Second operand (int or float).

    Returns:
        The value ``a + b`` as a float.

    Raises:
        TypeError: If *a* or *b* is not numeric.

    Examples:
        >>> add(3.5, 2.0)
        5.5
        >>> add(-1, 1)
        0
    """
    _validate_numeric(a, b)
    return a + b


def subtract(a: float, b: float) -> float:
    """Return the arithmetic difference *a* − *b*.

    Args:
        a: Minuend (int or float).
        b: Subtrahend (int or float).

    Returns:
        The value ``a - b`` as a float.

    Raises:
        TypeError: If *a* or *b* is not numeric.

    Examples:
        >>> subtract(3.5, 2.0)
        1.5
    """
    _validate_numeric(a, b)
    return a - b


def multiply(a: float, b: float) -> float:
    """Return the arithmetic product of *a* and *b*.

    Args:
        a: First factor (int or float).
        b: Second factor (int or float).

    Returns:
        The value ``a * b`` as a float.

    Raises:
        TypeError: If *a* or *b* is not numeric.

    Examples:
        >>> multiply(3.5, 2.0)
        7.0
    """
    _validate_numeric(a, b)
    return a * b


def divide(a: float, b: float) -> float:
    """Return the quotient *a* / *b*.

    Args:
        a: Dividend (int or float).
        b: Divisor (int or float).  Must not be zero.

    Returns:
        The value ``a / b`` as a float.

    Raises:
        DivisionByZeroError: If *b* is zero.
        TypeError: If *a* or *b* is not numeric.

    Examples:
        >>> divide(10.0, 4.0)
        2.5
        >>> divide(10.0, 0)
        Traceback (most recent call last):
            ...
        calculator.DivisionByZeroError: Cannot divide by zero
    """
    _validate_numeric(a, b)
    if b == 0:
        raise DivisionByZeroError("Cannot divide by zero")
    return a / b


# ---------------------------------------------------------------------------
# Scientific operations
# ---------------------------------------------------------------------------


def sqrt(a: float) -> float:
    """Return the principal (non-negative) square root of *a*.

    Args:
        a: Radicand (int or float).  Must be ≥ 0.

    Returns:
        ``math.sqrt(a)`` — the non-negative square root of *a*.

    Raises:
        DomainError: If *a* is negative.
        TypeError: If *a* is not numeric.

    Examples:
        >>> sqrt(9.0)
        3.0
        >>> sqrt(2.0)
        1.4142135623730951
    """
    _validate_numeric(a)
    if a < 0:
        raise DomainError(
            f"sqrt requires a non-negative argument, got {a}"
        )
    return math.sqrt(a)


def power(base: float, exponent: float) -> float:
    """Return *base* raised to the power of *exponent*.

    Uses ``math.pow``, which always returns a ``float``.

    Args:
        base: The base value (int or float).
        exponent: The exponent value (int or float).

    Returns:
        ``math.pow(base, exponent)`` as a float.

    Raises:
        TypeError: If *base* or *exponent* is not numeric.

    Examples:
        >>> power(2.0, 10.0)
        1024.0
        >>> power(2.0, -1.0)
        0.5
    """
    _validate_numeric(base, exponent)
    return math.pow(base, exponent)


def log(a: float) -> float:
    """Return the natural logarithm (base *e*) of *a*.

    Args:
        a: The argument (int or float).  Must be strictly positive (> 0).

    Returns:
        ``math.log(a)`` — the natural logarithm of *a*.

    Raises:
        DomainError: If *a* is zero or negative.
        TypeError: If *a* is not numeric.

    Examples:
        >>> log(1.0)
        0.0
        >>> import math; abs(log(math.e) - 1.0) < 1e-9
        True
    """
    _validate_numeric(a)
    if a <= 0:
        raise DomainError(
            f"log requires a strictly positive argument, got {a}"
        )
    return math.log(a)


def sin(a: float) -> float:
    """Return the sine of *a* (angle in radians).

    Args:
        a: Angle in radians (int or float).

    Returns:
        ``math.sin(a)`` — a value in the range [−1, 1].

    Raises:
        TypeError: If *a* is not numeric.

    Examples:
        >>> sin(0.0)
        0.0
    """
    _validate_numeric(a)
    return math.sin(a)


def cos(a: float) -> float:
    """Return the cosine of *a* (angle in radians).

    Args:
        a: Angle in radians (int or float).

    Returns:
        ``math.cos(a)`` — a value in the range [−1, 1].

    Raises:
        TypeError: If *a* is not numeric.

    Examples:
        >>> cos(0.0)
        1.0
    """
    _validate_numeric(a)
    return math.cos(a)


def tan(a: float) -> float:
    """Return the tangent of *a* (angle in radians).

    The tangent is mathematically undefined at odd multiples of π/2
    (i.e., …, −3π/2, −π/2, π/2, 3π/2, …).  Because π/2 is not exactly
    representable in IEEE-754 floating-point, ``math.tan(math.pi / 2)``
    returns a very large finite number (~1.63 × 10¹⁶) rather than raising.
    This function guards against that by checking whether
    ``abs(math.cos(a)) < 1e-10``; if so, ``DomainError`` is raised.

    **Threshold note:** The guard threshold ``1e-10`` is chosen because
    ``math.cos(math.pi / 2)`` evaluates to ``≈ 6.12 × 10⁻¹⁷`` in CPython
    (well below the threshold), while the smallest well-defined cosine
    value that a caller would legitimately pass is many orders of magnitude
    larger.  Angles within ~10⁻¹⁰ radians of an undefined point will also
    raise ``DomainError``; this is documented behaviour.

    Args:
        a: Angle in radians (int or float).

    Returns:
        ``math.tan(a)`` for well-defined angles.

    Raises:
        DomainError: If *a* is at (or extremely close to) an odd multiple
            of π/2, i.e., ``abs(math.cos(a)) < 1e-10``.
        TypeError: If *a* is not numeric.

    Examples:
        >>> tan(0.0)
        0.0
        >>> import math; abs(tan(math.pi / 4) - 1.0) < 1e-9
        True
    """
    _validate_numeric(a)
    if abs(math.cos(a)) < 1e-10:
        raise DomainError(
            "tan is undefined at odd multiples of π/2 "
            f"(cos({a}) ≈ {math.cos(a):.3e})"
        )
    return math.tan(a)
