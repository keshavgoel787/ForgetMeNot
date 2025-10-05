"""
Session Management for ReMind
Tracks which memories have been shown to prevent repetition
"""

from typing import Set, Dict, List, Optional
from datetime import datetime, timedelta
import json


class SessionManager:
    """
    Manages patient sessions and tracks shown memories
    Prevents showing the same clips repeatedly
    """

    def __init__(self):
        # In-memory storage: {patient_id: {topic: set(memory_ids)}}
        self.shown_memories: Dict[str, Dict[str, Set[str]]] = {}
        self.session_timestamps: Dict[str, datetime] = {}

    def get_session_key(self, patient_id: str, topic: str) -> str:
        """Generate session key"""
        return f"{patient_id}:{topic}"

    def get_shown_memories(self, patient_id: str, topic: str) -> Set[str]:
        """Get list of memory IDs already shown in this session"""
        session_key = self.get_session_key(patient_id, topic)

        # Clean old sessions (older than 24 hours)
        self._clean_old_sessions()

        if patient_id not in self.shown_memories:
            self.shown_memories[patient_id] = {}

        if topic not in self.shown_memories[patient_id]:
            self.shown_memories[patient_id][topic] = set()

        return self.shown_memories[patient_id][topic]

    def mark_as_shown(self, patient_id: str, topic: str, memory_ids: List[str]):
        """Mark memories as shown"""
        session_key = self.get_session_key(patient_id, topic)

        if patient_id not in self.shown_memories:
            self.shown_memories[patient_id] = {}

        if topic not in self.shown_memories[patient_id]:
            self.shown_memories[patient_id][topic] = set()

        # Add to shown set
        self.shown_memories[patient_id][topic].update(memory_ids)

        # Update timestamp
        self.session_timestamps[session_key] = datetime.now()

        print(f"📝 Session {session_key}: {len(self.shown_memories[patient_id][topic])} memories shown")

    def reset_session(self, patient_id: str, topic: Optional[str] = None):
        """Reset session - clear shown memories"""
        if topic:
            # Reset specific topic
            if patient_id in self.shown_memories and topic in self.shown_memories[patient_id]:
                self.shown_memories[patient_id][topic] = set()
                session_key = self.get_session_key(patient_id, topic)
                if session_key in self.session_timestamps:
                    del self.session_timestamps[session_key]
                print(f"♻️  Reset session: {patient_id}:{topic}")
        else:
            # Reset all topics for patient
            if patient_id in self.shown_memories:
                del self.shown_memories[patient_id]
            # Clear timestamps
            keys_to_delete = [k for k in self.session_timestamps.keys() if k.startswith(f"{patient_id}:")]
            for key in keys_to_delete:
                del self.session_timestamps[key]
            print(f"♻️  Reset all sessions for: {patient_id}")

    def get_session_stats(self, patient_id: str, topic: str) -> Dict:
        """Get statistics about current session"""
        shown = self.get_shown_memories(patient_id, topic)
        session_key = self.get_session_key(patient_id, topic)

        return {
            "patient_id": patient_id,
            "topic": topic,
            "memories_shown": len(shown),
            "last_updated": self.session_timestamps.get(session_key),
            "shown_ids": list(shown)
        }

    def _clean_old_sessions(self, max_age_hours: int = 24):
        """Remove sessions older than max_age_hours"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        expired_keys = [
            key for key, timestamp in self.session_timestamps.items()
            if timestamp < cutoff
        ]

        for key in expired_keys:
            patient_id, topic = key.split(":", 1)
            if patient_id in self.shown_memories and topic in self.shown_memories[patient_id]:
                del self.shown_memories[patient_id][topic]
            del self.session_timestamps[key]

        if expired_keys:
            print(f"🧹 Cleaned {len(expired_keys)} expired sessions")


# Global session manager instance
session_manager = SessionManager()
