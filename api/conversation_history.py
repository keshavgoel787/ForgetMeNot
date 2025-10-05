"""
Conversation History Management
Tracks multi-turn conversations to enable context-aware responses
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel


class ConversationTurn(BaseModel):
    """Single turn in a conversation"""
    timestamp: datetime
    role: str  # "patient" or "agent"
    message: str
    topic: str


class ConversationHistory:
    """
    Manages conversation history per patient session
    Enables LLM to build on previous context and avoid repetition
    """

    def __init__(self):
        # Storage: {patient_id: {topic: [turns]}}
        self.conversations: Dict[str, Dict[str, List[ConversationTurn]]] = {}
        self.session_timestamps: Dict[str, datetime] = {}

    def add_turn(self, patient_id: str, topic: str, role: str, message: str):
        """Add a conversation turn"""

        if patient_id not in self.conversations:
            self.conversations[patient_id] = {}

        if topic not in self.conversations[patient_id]:
            self.conversations[patient_id][topic] = []

        turn = ConversationTurn(
            timestamp=datetime.now(),
            role=role,
            message=message,
            topic=topic
        )

        self.conversations[patient_id][topic].append(turn)

        # Update session timestamp
        session_key = f"{patient_id}:{topic}"
        self.session_timestamps[session_key] = datetime.now()

        print(f"💬 Conversation turn added: {patient_id}:{topic} ({role})")

    def get_history(
        self,
        patient_id: str,
        topic: str,
        max_turns: Optional[int] = 10
    ) -> List[ConversationTurn]:
        """Get recent conversation history"""

        # Clean old sessions first
        self._clean_old_sessions()

        if patient_id not in self.conversations:
            return []

        if topic not in self.conversations[patient_id]:
            return []

        history = self.conversations[patient_id][topic]

        # Return most recent turns
        if max_turns:
            return history[-max_turns:]

        return history

    def get_formatted_history(
        self,
        patient_id: str,
        topic: str,
        max_turns: Optional[int] = 10
    ) -> str:
        """Get conversation history formatted for LLM prompt"""

        history = self.get_history(patient_id, topic, max_turns)

        if not history:
            return "No previous conversation."

        formatted = []
        for turn in history:
            role_name = "Patient" if turn.role == "patient" else "You (Agent)"
            formatted.append(f"{role_name}: {turn.message}")

        return "\n".join(formatted)

    def get_agent_previous_responses(
        self,
        patient_id: str,
        topic: str,
        max_turns: int = 5
    ) -> List[str]:
        """Get agent's previous responses to avoid repetition"""

        history = self.get_history(patient_id, topic, max_turns * 2)

        # Filter only agent responses
        agent_responses = [
            turn.message for turn in history
            if turn.role == "agent"
        ]

        return agent_responses[-max_turns:] if agent_responses else []

    def get_conversation_stats(self, patient_id: str, topic: str) -> Dict:
        """Get statistics about the conversation"""

        history = self.get_history(patient_id, topic, max_turns=None)

        if not history:
            return {
                "patient_id": patient_id,
                "topic": topic,
                "total_turns": 0,
                "patient_turns": 0,
                "agent_turns": 0,
                "started_at": None,
                "last_updated": None,
                "duration_minutes": 0
            }

        patient_turns = sum(1 for t in history if t.role == "patient")
        agent_turns = sum(1 for t in history if t.role == "agent")

        started_at = history[0].timestamp
        last_updated = history[-1].timestamp
        duration = (last_updated - started_at).total_seconds() / 60

        return {
            "patient_id": patient_id,
            "topic": topic,
            "total_turns": len(history),
            "patient_turns": patient_turns,
            "agent_turns": agent_turns,
            "started_at": started_at,
            "last_updated": last_updated,
            "duration_minutes": round(duration, 1)
        }

    def reset_conversation(self, patient_id: str, topic: Optional[str] = None):
        """Clear conversation history"""

        if topic:
            # Reset specific topic
            if patient_id in self.conversations and topic in self.conversations[patient_id]:
                del self.conversations[patient_id][topic]
                session_key = f"{patient_id}:{topic}"
                if session_key in self.session_timestamps:
                    del self.session_timestamps[session_key]
                print(f"🔄 Conversation history reset: {patient_id}:{topic}")
        else:
            # Reset all topics for patient
            if patient_id in self.conversations:
                del self.conversations[patient_id]

            # Clear timestamps
            keys_to_delete = [
                k for k in self.session_timestamps.keys()
                if k.startswith(f"{patient_id}:")
            ]
            for key in keys_to_delete:
                del self.session_timestamps[key]

            print(f"🔄 All conversations reset for: {patient_id}")

    def export_conversation(
        self,
        patient_id: str,
        topic: str
    ) -> List[Dict]:
        """Export conversation history as JSON-serializable format"""

        history = self.get_history(patient_id, topic, max_turns=None)

        return [
            {
                "timestamp": turn.timestamp.isoformat(),
                "role": turn.role,
                "message": turn.message,
                "topic": turn.topic
            }
            for turn in history
        ]

    def _clean_old_sessions(self, max_age_hours: int = 24):
        """Remove conversations older than max_age_hours"""

        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        expired_keys = [
            key for key, timestamp in self.session_timestamps.items()
            if timestamp < cutoff
        ]

        for key in expired_keys:
            patient_id, topic = key.split(":", 1)
            if patient_id in self.conversations and topic in self.conversations[patient_id]:
                del self.conversations[patient_id][topic]
            del self.session_timestamps[key]

        if expired_keys:
            print(f"🧹 Cleaned {len(expired_keys)} expired conversations")


# Global conversation history manager
conversation_history = ConversationHistory()
