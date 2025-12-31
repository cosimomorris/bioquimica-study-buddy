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


def enzyme_kinetics(v_max: float, km: float, substrate_conc: float) -> float:
    """
    Calculate reaction velocity using the Michaelis-Menten equation.

    This tool computes the initial velocity of an enzyme-catalyzed reaction
    given the kinetic parameters and substrate concentration.

    Formula: v = (Vmax * [S]) / (Km + [S])

    Args:
        v_max: Maximum reaction velocity (Vmax) in appropriate units (e.g., umol/min).
        km: Michaelis constant (Km) in mol/L or mM.
        substrate_conc: Substrate concentration [S] in same units as Km.

    Returns:
        The calculated reaction velocity in same units as Vmax.

    Raises:
        ValueError: If any parameter is zero or negative.

    Example:
        >>> enzyme_kinetics(v_max=100, km=10, substrate_conc=10)
        50.0  # At [S] = Km, velocity is Vmax/2
    """
    if v_max <= 0 or km <= 0 or substrate_conc <= 0:
        raise ValueError("All parameters must be positive values")

    return (v_max * substrate_conc) / (km + substrate_conc)
