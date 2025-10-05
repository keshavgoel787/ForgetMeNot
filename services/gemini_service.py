"""
Gemini AI service for memory analysis and intent parsing
"""
import google.generativeai as genai
import json
import os
from typing import Dict


class GeminiService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")

    def analyze_memory(self, transcript: str) -> Dict:
        """
        Analyze a memory transcript and extract structured information.

        Args:
            transcript: The transcribed text to analyze

        Returns:
            Dict with people, location, event, emotion, and summary
        """
        prompt = f"""
        Analyze the following memory transcript and extract:
        - People mentioned
        - Location or setting
        - Main event or topic
        - Emotional tone (joyful, sad, nostalgic, confused, calm, anxious)
        - A short 1–2 sentence summary

        Return strictly as valid JSON with these keys:
        people, location, event, emotion, summary.

        Transcript:
        {transcript}
        """

        response = self.model.generate_content(prompt)

        try:
            # Extract text from the response candidates
            response_text = response.candidates[0].content.parts[0].text
            # Remove markdown code blocks if present
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            data = json.loads(response_text)
        except Exception as e:
            # Fallback to raw text if parsing fails
            data = {"summary": "Failed to parse memory analysis", "error": str(e)}

        return data
