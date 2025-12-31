# core/tools.py
"""Biochemical calculation tools for Gemini function calling."""
import math


def calculate_ph(pka: float, acid_conc: float, base_conc: float) -> float:
    """
    Calculate pH using the Henderson-Hasselbalch equation.

    This tool calculates the pH of a buffer solution given the pKa of the
    weak acid and the concentrations of the acid and its conjugate base.

    Formula: pH = pKa + log10([conjugate base] / [weak acid])

    Args:
        pka: The pKa value of the weak acid (e.g., 4.76 for acetic acid).
        acid_conc: Concentration of the weak acid in mol/L (must be positive).
        base_conc: Concentration of the conjugate base in mol/L (must be positive).

    Returns:
        The calculated pH value of the buffer solution.

    Raises:
        ValueError: If either concentration is zero or negative.

    Example:
        >>> calculate_ph(pka=4.76, acid_conc=0.1, base_conc=0.05)
        4.459  # Acetic acid buffer
    """
    if acid_conc <= 0 or base_conc <= 0:
        raise ValueError("Concentrations must be positive values")

    return pka + math.log10(base_conc / acid_conc)
