# Conversation History Feature

The system now tracks conversation history to enable contextual, non-repetitive responses.

## How It Works

### 1. **Tracks Every Conversation Turn**
```
Patient: "Tell me about Disney"
Agent: "Looking at your Disney trip, I see a wonderful Mickey Mouse cinnamon roll..."

Patient: "What else did we eat?"
Agent: "Besides that delicious cinnamon roll we just talked about, I also see..."
                    ↑ References previous conversation!
```

### 2. **Prevents Repetition**
The LLM sees:
```
Previous responses you've given (DO NOT REPEAT):
- "Looking at your Disney trip, I see a wonderful Mickey Mouse cinnamon roll..."

IMPORTANT: Do not repeat the same phrases or information.
```

### 3. **Builds Context Over Time**
```
Turn 1:
Patient: "Show me Disney"
Agent: "Here's a beautiful memory from your Disney trip..."

Turn 2:
Patient: "Who was I with?"
Agent: "From what we just looked at, you were with Anna..."
         ↑ References the memory from Turn 1
```

---

## Example Conversation Flow

```bash
# Request 1
POST /patient/query-test
{
  "transcription": "Tell me about Disney",
  "topic": "disney",
  "patient_id": "patient_123"
}

Response:
{
  "text": "Looking at your Disney trip memories, I can see a delicious Mickey Mouse cinnamon roll with chocolate chips. You shared this special treat with Anna, and it looks absolutely wonderful!"
}

# Request 2 - BUILDS on previous
POST /patient/query-test
{
  "transcription": "What else did we do?",
  "topic": "disney",
  "patient_id": "patient_123"  # Same patient
}

Response:
{
  "text": "Besides enjoying that tasty cinnamon roll, I see another memory from your Disney adventure - this time you're both standing in front of the iconic castle! You both look so happy together."
}
# Notice: "Besides that cinnamon roll" - references previous turn!

# Request 3 - CONTINUES building
POST /patient/query-test
{
  "transcription": "How did I feel?",
  "topic": "disney",
  "patient_id": "patient_123"
}

Response:
{
  "text": "From these wonderful moments we've been exploring - the cinnamon roll, the castle visit - I can see so much joy in your smile. You looked genuinely happy sharing these experiences with Anna."
}
# Notice: References BOTH previous memories
```

---

## API Endpoints

### View Conversation History
```bash
GET /patient/conversation/history?patient_id=patient_123&topic=disney

Response:
{
  "patient_id": "patient_123",
  "topic": "disney",
  "total_turns": 6,
  "conversation": [
    {
      "timestamp": "2025-10-05T10:30:00",
      "role": "patient",
      "message": "Tell me about Disney"
    },
    {
      "timestamp": "2025-10-05T10:30:05",
      "role": "agent",
      "message": "Looking at your Disney trip memories..."
    },
    ...
  ]
}
```

### Get Conversation Stats
```bash
GET /patient/conversation/stats?patient_id=patient_123&topic=disney

Response:
{
  "patient_id": "patient_123",
  "topic": "disney",
  "total_turns": 6,
  "patient_turns": 3,
  "agent_turns": 3,
  "started_at": "2025-10-05T10:30:00",
  "last_updated": "2025-10-05T10:35:00",
  "duration_minutes": 5.0
}
```

### Export Full Conversation
```bash
GET /patient/conversation/export?patient_id=patient_123&topic=disney

# Downloads complete conversation JSON
```

### Reset Conversation
```bash
# Reset conversation history only (keep shown memories)
POST /patient/session/reset?patient_id=patient_123&topic=disney&reset_conversation=true

# Reset both conversation AND shown memories
POST /patient/session/reset?patient_id=patient_123&topic=disney
```

---

## Key Features

### 1. **Context Awareness**
- Agent knows what was discussed in previous turns
- Builds on earlier statements
- Can reference specific memories mentioned before

### 2. **Anti-Repetition**
- LLM sees list of previous responses
- Explicitly instructed NOT to repeat phrases
- Higher temperature (0.9) for more variety

### 3. **Natural Conversation**
- "Besides that cinnamon roll we just talked about..."
- "From what we looked at earlier..."
- "Remember when I mentioned..."

### 4. **Session Management**
- Tracks up to last 10 turns (configurable)
- Auto-expires after 24 hours
- Separate history per patient + topic

---

## Frontend Integration

```javascript
// Track conversation in your UI
const [conversationHistory, setConversationHistory] = useState([]);

async function askQuestion(question) {
  const response = await fetch('/patient/query-test', {
    method: 'POST',
    body: new URLSearchParams({
      transcription: question,
      topic: 'disney',
      patient_id: 'patient_123'
    })
  });

  const data = await response.json();

  // Add to UI
  setConversationHistory([
    ...conversationHistory,
    { role: 'patient', message: question },
    { role: 'agent', message: data.text }
  ]);

  return data;
}

// Display conversation
{conversationHistory.map((turn, i) => (
  <div key={i} className={turn.role}>
    <strong>{turn.role === 'patient' ? 'You' : 'ReMind'}:</strong>
    <p>{turn.message}</p>
  </div>
))}
```

---

## Technical Details

### Storage Structure
```python
# conversation_history.conversations
{
  "patient_123": {
    "disney": [
      ConversationTurn(
        timestamp=datetime.now(),
        role="patient",
        message="Tell me about Disney",
        topic="disney"
      ),
      ConversationTurn(
        timestamp=datetime.now(),
        role="agent",
        message="Looking at your Disney trip...",
        topic="disney"
      )
    ],
    "college": [...]
  }
}
```

### How LLM Uses History
```python
# In generate_narration()

# Gets last 6 turns
conversation_context = """
Patient: Tell me about Disney
You (Agent): Looking at your Disney trip memories...
Patient: What else did we do?
You (Agent): Besides that cinnamon roll...
"""

# Gets last 3 agent responses to avoid repetition
previous_responses = [
  "Looking at your Disney trip memories...",
  "Besides that cinnamon roll...",
  "From these wonderful moments..."
]

# Includes in prompt
prompt = f"""
Recent Conversation:
{conversation_context}

Previous responses (DO NOT REPEAT):
- "Looking at your Disney trip memories..."
- "Besides that cinnamon roll..."

Generate NEW response that builds on this conversation...
"""
```

---

## Benefits

✅ **Contextual**: Agent remembers what was discussed
✅ **Non-repetitive**: Varies language and phrasing
✅ **Natural**: Feels like talking to someone who's listening
✅ **Progressive**: Deepens conversation over time
✅ **Trackable**: Full conversation history available

---

## Example: Before vs After

### Before (No History)
```
Turn 1: "Looking at your Disney trip, I see a Mickey Mouse cinnamon roll..."
Turn 2: "Looking at your Disney trip, I see a Mickey Mouse cinnamon roll..."
Turn 3: "Looking at your Disney trip, I see a Mickey Mouse cinnamon roll..."
```
❌ Repetitive, robotic

### After (With History)
```
Turn 1: "Looking at your Disney trip, I see a Mickey Mouse cinnamon roll with chocolate chips. You shared it with Anna!"

Turn 2: "Besides that delicious cinnamon roll we just talked about, I also see you both at the castle - you look so happy together!"

Turn 3: "From these wonderful moments - the treat, the castle - I can see the joy in your smile. What was your favorite part of the trip?"
```
✅ Natural, progressive, engaging
