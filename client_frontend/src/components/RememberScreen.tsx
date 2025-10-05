import React, { useState } from 'react';
import type { Memory } from '../types';
import '../styles/RememberScreen.css';
// import starIcon from '../assets/fav_icon_clicked.png';

const RememberScreen: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [memories, setMemories] = useState<Memory[]>([]);

  const suggestions = [
    'Birthday Party',
    'Road Trip',
    'First Day',
    'Graduation',
    'Wedding',
    'Concert',
    'Vacation'
  ];

  const gradientColors = [
    'linear-gradient(45deg, #ff6b6b, #feca57)',
    'linear-gradient(45deg, #48cae4, #023e8a)',
    'linear-gradient(45deg, #f72585, #b5179e)',
    'linear-gradient(45deg, #2d6a4f, #52b788)',
    'linear-gradient(45deg, #e76f51, #f4a261)',
    'linear-gradient(45deg, #8ecae6, #219ebc)',
    'linear-gradient(45deg, #fb8500, #ffb703)'
  ];

  const handleSubmit = () => {
    if (inputText.trim()) {
      const newMemory: Memory = {
        text: inputText,
        gradient: gradientColors[memories.length % gradientColors.length]
      };
      setMemories([...memories, newMemory]);
      setInputText('');
    }
  };

  const addSuggestion = (suggestion: string) => {
    const newMemory: Memory = {
      text: suggestion,
      gradient: gradientColors[memories.length % gradientColors.length]
    };
    setMemories([...memories, newMemory]);
  };

  return (
    <div className="screen active">
      <div className="header-bar">Remember</div>
      <div className="content">
        <div className="input-group">
          <label htmlFor="memoryInput">What do you want to remember?</label>
          <input
            id="memoryInput"
            type="text"
            className="memory-input"
            placeholder="Enter a memory title..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') handleSubmit();
            }}
          />
        </div>
        <button className="submit-button" onClick={handleSubmit}>
          Add Memory
        </button>

        {memories.length > 0 && (
          <div className="memories-section">
            <div className="memories-title">Your Memories</div>
            <div className="memories-grid">
              {memories.map((memory, index) => (
                <div key={index} className="memory-item">
                  <div
                    className="memory-circle"
                    style={{ background: memory.gradient }}
                  >
                    {/* <img src={starIcon} alt={memory.text} /> */}
                    <span style={{ color: 'white', fontSize: '32px' }}>★</span>
                  </div>
                  <div className="memory-label">{memory.text}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="suggestions-section">
          <div className="suggestions-title">Suggestions</div>
          <div className="suggestions-grid">
            {suggestions.map((suggestion, index) => (
              <div
                key={suggestion}
                className="suggestion-item"
                onClick={() => addSuggestion(suggestion)}
              >
                <div
                  className="suggestion-circle"
                  style={{ background: gradientColors[index % gradientColors.length] }}
                >
                  {/* <img src={starIcon} alt={suggestion} /> */}
                  <span style={{ color: 'white', fontSize: '32px' }}>★</span>
                </div>
                <div className="suggestion-label">{suggestion}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RememberScreen;
