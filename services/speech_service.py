"""
Speech transcription service using Google Cloud Speech-to-Text
"""
from google.cloud import speech
import os


class SpeechService:
    def __init__(self):
        self.client = speech.SpeechClient()

    def transcribe_audio(self, audio_content: bytes) -> str:
        """
        Transcribe audio content to text.

        Args:
            audio_content: Raw audio file bytes

        Returns:
            Transcribed text
        """
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            language_code="en-US",
            enable_automatic_punctuation=True,
            use_enhanced=True,
            model="latest_short",
        )

        response = self.client.recognize(config=config, audio=audio)
        transcript = " ".join([
            result.alternatives[0].transcript
            for result in response.results
        ])

        return transcript
