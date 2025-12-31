# tests/test_tools.py
import pytest
import math


def test_calculate_ph_basic_buffer():
    """pH calculation using Henderson-Hasselbalch equation."""
    from core.tools import calculate_ph

    # Acetic acid buffer: pKa=4.76, [A-]=0.05M, [HA]=0.1M
    result = calculate_ph(pka=4.76, acid_conc=0.1, base_conc=0.05)

    # pH = pKa + log([A-]/[HA]) = 4.76 + log(0.5) = 4.76 - 0.301 = 4.459
    assert abs(result - 4.459) < 0.01


def test_calculate_ph_equal_concentrations():
    """When acid and base concentrations are equal, pH equals pKa."""
    from core.tools import calculate_ph

    result = calculate_ph(pka=7.0, acid_conc=0.1, base_conc=0.1)

    assert abs(result - 7.0) < 0.001


def test_calculate_ph_raises_on_zero_concentration():
    """Zero concentration should raise ValueError."""
    from core.tools import calculate_ph

    with pytest.raises(ValueError, match="must be positive"):
        calculate_ph(pka=4.76, acid_conc=0, base_conc=0.1)
