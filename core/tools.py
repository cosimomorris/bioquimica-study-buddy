# core/tools.py
"""Biochemical calculation tools for Gemini function calling."""
import math
from typing import List


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


def isoelectric_point(pka_values: List[float]) -> float:
    """
    Calculate the isoelectric point (pI) of an amino acid.

    The pI is calculated as the average of the two pKa values that bracket
    the zwitterionic form. For simple amino acids, this is the average of
    pKa1 and pKa2. For acidic amino acids (3 pKa values), use the two lowest.
    For basic amino acids (3 pKa values), use the two highest.

    Args:
        pka_values: List of pKa values for the amino acid, sorted ascending.
                   Must contain at least 2 values.

    Returns:
        The calculated isoelectric point.

    Raises:
        ValueError: If fewer than 2 pKa values are provided.

    Example:
        >>> isoelectric_point(pka_values=[2.34, 9.60])  # Glycine
        5.97
        >>> isoelectric_point(pka_values=[1.88, 3.65, 9.60])  # Aspartate
        2.77
    """
    if len(pka_values) < 2:
        raise ValueError("At least 2 pKa values are required")

    sorted_pkas = sorted(pka_values)

    if len(sorted_pkas) == 2:
        return (sorted_pkas[0] + sorted_pkas[1]) / 2
    elif len(sorted_pkas) == 3:
        # Acidic amino acids: average of two lowest
        # Basic amino acids: average of two highest
        # Heuristic: if middle pKa < 7, it's acidic; otherwise basic
        if sorted_pkas[1] < 7:
            return (sorted_pkas[0] + sorted_pkas[1]) / 2
        else:
            return (sorted_pkas[1] + sorted_pkas[2]) / 2
    else:
        raise ValueError("Expected 2 or 3 pKa values")


def create_flashcards(topic: str, cards: List[dict]) -> str:
    """
    Create flashcards for studying a biochemistry topic.

    Use this tool when Jimena asks for flashcards, tarjetas de estudio,
    or wants to memorize key concepts from the course materials.
    First ask how many flashcards she wants, then create them based on
    the indexed documents.

    Args:
        topic: The topic being studied (e.g., "Enzimas", "Glucólisis", "pH").
        cards: List of flashcard dicts, each with:
            - "pregunta": The question or prompt to test knowledge
            - "respuesta": The answer or explanation

    Returns:
        Formatted flashcards as text ready to display.

    Raises:
        ValueError: If cards list is empty.

    Example:
        >>> create_flashcards("Enzimas", [
        ...     {"pregunta": "¿Qué es la Km?", "respuesta": "Concentración de sustrato a Vmax/2"},
        ...     {"pregunta": "¿Qué es Vmax?", "respuesta": "Velocidad máxima de reacción"}
        ... ])
    """
    if not cards:
        raise ValueError("Debe haber al menos una tarjeta")

    output = f"📚 **Flashcards: {topic}**\n\n"

    for i, card in enumerate(cards, 1):
        pregunta = card.get("pregunta", "")
        respuesta = card.get("respuesta", "")
        output += f"🔹 **Tarjeta {i}**\n"
        output += f"**Pregunta:** {pregunta}\n"
        output += f"**Respuesta:** {respuesta}\n\n"

    return output.strip()


def create_exam(topic: str, questions: List[dict]) -> str:
    """
    Create a practice exam with multiple choice and true/false questions.

    Use this tool when Jimena asks for an exam, quiz, examen, test, or wants
    to practice with questions from the course materials.
    First ask how many questions she wants, then create a mix of
    multiple choice and true/false questions based on the indexed documents.

    Args:
        topic: The topic being tested (e.g., "Glucólisis", "Aminoácidos").
        questions: List of question dicts, each with:
            - "tipo": "opcion_multiple" or "verdadero_falso"
            - "pregunta": The question text
            - "opciones": List of 4 options A, B, C, D (for opcion_multiple only)
            - "respuesta_correcta": The correct answer (letter or "Verdadero"/"Falso")
            - "explicacion": Brief explanation of why it's correct

    Returns:
        Formatted exam as text ready to display.

    Raises:
        ValueError: If questions list is empty.

    Example:
        >>> create_exam("Glucólisis", [
        ...     {
        ...         "tipo": "opcion_multiple",
        ...         "pregunta": "¿Cuál es la enzima reguladora principal?",
        ...         "opciones": ["Hexoquinasa", "PFK-1", "Piruvato quinasa", "Aldolasa"],
        ...         "respuesta_correcta": "B",
        ...         "explicacion": "PFK-1 es el punto de control principal"
        ...     },
        ...     {
        ...         "tipo": "verdadero_falso",
        ...         "pregunta": "La glucólisis produce 4 ATP netos",
        ...         "opciones": None,
        ...         "respuesta_correcta": "Falso",
        ...         "explicacion": "Produce 2 ATP netos"
        ...     }
        ... ])
    """
    if not questions:
        raise ValueError("Debe haber al menos una pregunta")

    output = f"📝 **Examen: {topic}**\n\n"

    for i, q in enumerate(questions, 1):
        tipo = q.get("tipo", "opcion_multiple")
        pregunta = q.get("pregunta", "")
        respuesta = q.get("respuesta_correcta", "")
        explicacion = q.get("explicacion", "")

        if tipo == "opcion_multiple":
            opciones = q.get("opciones", [])
            output += f"**{i}. [Opción Múltiple]** {pregunta}\n"
            for j, opcion in enumerate(opciones):
                letra = chr(65 + j)  # A, B, C, D
                marca = " ✓" if letra == respuesta else ""
                output += f"   {letra}) {opcion}{marca}\n"
        else:  # verdadero_falso
            output += f"**{i}. [V/F]** {pregunta}\n"
            output += f"   **Respuesta:** {respuesta} ✓\n"

        output += f"   **Explicación:** {explicacion}\n\n"

    return output.strip()
