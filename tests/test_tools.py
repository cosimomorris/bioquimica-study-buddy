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


def test_enzyme_kinetics_half_vmax():
    """When [S] = Km, velocity should be Vmax/2."""
    from core.tools import enzyme_kinetics

    result = enzyme_kinetics(v_max=100, km=10, substrate_conc=10)

    assert abs(result - 50.0) < 0.01


def test_enzyme_kinetics_high_substrate():
    """At very high [S], velocity approaches Vmax."""
    from core.tools import enzyme_kinetics

    result = enzyme_kinetics(v_max=100, km=10, substrate_conc=1000)

    assert result > 99.0  # Should be close to Vmax


def test_enzyme_kinetics_raises_on_invalid_params():
    """Negative or zero parameters should raise ValueError."""
    from core.tools import enzyme_kinetics

    with pytest.raises(ValueError):
        enzyme_kinetics(v_max=-100, km=10, substrate_conc=5)


def test_isoelectric_point_glycine():
    """Glycine pI is average of pKa1 (2.34) and pKa2 (9.60)."""
    from core.tools import isoelectric_point

    result = isoelectric_point(pka_values=[2.34, 9.60])

    assert abs(result - 5.97) < 0.01


def test_isoelectric_point_aspartate():
    """Acidic amino acid uses two lowest pKa values."""
    from core.tools import isoelectric_point

    # Aspartate: pKa1=1.88, pKa2=3.65, pKa3=9.60
    # pI = (1.88 + 3.65) / 2 = 2.77
    result = isoelectric_point(pka_values=[1.88, 3.65, 9.60])

    assert abs(result - 2.77) < 0.01


def test_isoelectric_point_lysine():
    """Basic amino acid uses two highest pKa values."""
    from core.tools import isoelectric_point

    # Lysine: pKa1=2.18, pKa2=8.95, pKa3=10.53
    # pI = (8.95 + 10.53) / 2 = 9.74
    result = isoelectric_point(pka_values=[2.18, 8.95, 10.53])

    assert abs(result - 9.74) < 0.01


def test_isoelectric_point_raises_on_insufficient_pkas():
    """Need at least 2 pKa values."""
    from core.tools import isoelectric_point

    with pytest.raises(ValueError, match="[Aa]t least 2"):
        isoelectric_point(pka_values=[4.5])


# Tests for create_flashcards
def test_create_flashcards_basic():
    """Create flashcards with valid input."""
    from core.tools import create_flashcards

    cards = [
        {"pregunta": "¿Qué es la Km?", "respuesta": "Concentración de sustrato a Vmax/2"},
        {"pregunta": "¿Qué es Vmax?", "respuesta": "Velocidad máxima de reacción"}
    ]
    result = create_flashcards(topic="Enzimas", cards=cards)

    assert "Flashcards: Enzimas" in result
    assert "Tarjeta 1" in result
    assert "Tarjeta 2" in result
    assert "¿Qué es la Km?" in result
    assert "Concentración de sustrato" in result


def test_create_flashcards_empty_raises():
    """Empty cards list should raise ValueError."""
    from core.tools import create_flashcards

    with pytest.raises(ValueError, match="al menos una tarjeta"):
        create_flashcards(topic="Enzimas", cards=[])


# Tests for create_exam
def test_create_exam_multiple_choice():
    """Create exam with multiple choice questions."""
    from core.tools import create_exam

    questions = [
        {
            "tipo": "opcion_multiple",
            "pregunta": "¿Cuál es la enzima reguladora?",
            "opciones": ["Hexoquinasa", "PFK-1", "Piruvato quinasa", "Aldolasa"],
            "respuesta_correcta": "B",
            "explicacion": "PFK-1 es el punto de control"
        }
    ]
    result = create_exam(topic="Glucólisis", questions=questions)

    assert "Examen: Glucólisis" in result
    assert "[Opción Múltiple]" in result
    assert "A) Hexoquinasa" in result
    assert "B) PFK-1" in result
    assert "✓" in result


def test_create_exam_true_false():
    """Create exam with true/false questions."""
    from core.tools import create_exam

    questions = [
        {
            "tipo": "verdadero_falso",
            "pregunta": "La glucólisis produce 4 ATP netos",
            "opciones": None,
            "respuesta_correcta": "Falso",
            "explicacion": "Produce 2 ATP netos"
        }
    ]
    result = create_exam(topic="Glucólisis", questions=questions)

    assert "[V/F]" in result
    assert "Falso" in result
    assert "2 ATP netos" in result


def test_create_exam_mixed():
    """Create exam with mixed question types."""
    from core.tools import create_exam

    questions = [
        {
            "tipo": "opcion_multiple",
            "pregunta": "¿Cuál es la enzima reguladora?",
            "opciones": ["A", "B", "C", "D"],
            "respuesta_correcta": "B",
            "explicacion": "Explicación 1"
        },
        {
            "tipo": "verdadero_falso",
            "pregunta": "Afirmación de prueba",
            "opciones": None,
            "respuesta_correcta": "Verdadero",
            "explicacion": "Explicación 2"
        }
    ]
    result = create_exam(topic="Test", questions=questions)

    assert "[Opción Múltiple]" in result
    assert "[V/F]" in result


def test_create_exam_empty_raises():
    """Empty questions list should raise ValueError."""
    from core.tools import create_exam

    with pytest.raises(ValueError, match="al menos una pregunta"):
        create_exam(topic="Test", questions=[])
