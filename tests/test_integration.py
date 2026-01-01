# tests/test_integration.py
"""Integration tests - require GOOGLE_API_KEY environment variable."""
import pytest
import os


@pytest.mark.skipif(
    not os.environ.get("GOOGLE_API_KEY"),
    reason="GOOGLE_API_KEY not set"
)
class TestIntegration:
    """Integration tests that hit the real Gemini API."""

    def test_tool_invocation_ph_calculation(self):
        """Verify Gemini calls our pH tool correctly."""
        from core.client import get_client
        from core.tools import calculate_ph
        from google.genai import types

        client = get_client()

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Calculate the pH of a buffer with pKa=4.76, 0.1M acetic acid, and 0.05M acetate.",
            config=types.GenerateContentConfig(
                tools=[calculate_ph]
            )
        )

        # Response should contain the calculated pH value ~4.46
        assert "4.4" in response.text or "4.5" in response.text

    def test_system_prompt_enforces_tool_use(self):
        """Verify system prompt makes Gemini use tools for calculations."""
        from core.client import get_client
        from core.tools import calculate_ph, enzyme_kinetics
        from google.genai import types

        client = get_client()

        system_instruction = """When asked for calculations, you MUST use the provided
        calculation tools rather than doing math yourself."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="What is the reaction velocity when Vmax=100, Km=10, and [S]=10?",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[calculate_ph, enzyme_kinetics]
            )
        )

        # Response should contain 50 (Vmax/2 when [S]=Km)
        assert "50" in response.text
