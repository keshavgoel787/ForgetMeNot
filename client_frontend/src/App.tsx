import React, { useState, useEffect, useRef } from 'react';
import { Mic, ChevronLeft, ChevronRight } from 'lucide-react';

// Import memory data
import avery1 from './testdata/avery1.json';
import avery2 from './testdata/avery2.json';
import avery3 from './testdata/avery3.json';
import college1 from './testdata/college1.json';
import college2 from './testdata/college2.json';
import disney1 from './testdata/disney1.json';
import ski1 from './testdata/ski1.json';
import football1 from './testdata/football1.json';
import tyler1 from './testdata/tyler1.json';

interface Memory {
  id: string;
  topic: string;
  text: string;
  displayMode: '3-pic' | '4-pic' | '5-pic' | 'video' | 'vertical-video';
  media: string[];
}

const ImagePlaygroundUI = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);
  const [currentMemoryIndex, setCurrentMemoryIndex] = useState(0);
  const [displayMode, setDisplayMode] = useState<'3-pic' | '4-pic' | '5-pic' | 'video' | 'vertical-video'>('video');
  const [fadeKey, setFadeKey] = useState(0);
  const [currentMedia, setCurrentMedia] = useState<string[]>([]);
  const [isLoadingAudio, setIsLoadingAudio] = useState(false);
  const [showContent, setShowContent] = useState(false);
  const recognitionRef = useRef<any>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const memories: Memory[] = [
    avery1, avery2, avery3, college1, college2, disney1, ski1, football1, tyler1
  ] as Memory[];

  const filteredMemories = selectedTopic 
    ? memories.filter(m => m.topic === selectedTopic)
    : memories;

  const suggestions = [
    { id: 1, label: 'Avery', icon: '👧' },
    { id: 2, label: 'College', icon: '🎓' },
    { id: 3, label: 'Disney', icon: '🏰' },
    { id: 4, label: 'Ski', icon: '⛷️' },
    { id: 5, label: 'Football', icon: '🏈' },
    { id: 6, label: 'Tyler', icon: '🧑' }
  ];

  const backgroundCircles = [
    { id: 'bg1', x: 8, y: 15, size: 70, delay: 0, icon: '🎨' },
    { id: 'bg2', x: 15, y: 45, size: 65, delay: 1.5, icon: '✨' },
    { id: 'bg3', x: 5, y: 70, size: 75, delay: 0.8, icon: '🎭' },
    { id: 'bg4', x: 12, y: 85, size: 68, delay: 2, icon: '🎪' },
    { id: 'bg5', x: 18, y: 25, size: 62, delay: 1.2, icon: '🎬' },
    { id: 'bg6', x: 85, y: 20, size: 72, delay: 0.5, icon: '🎵' },
    { id: 'bg7', x: 92, y: 50, size: 66, delay: 1.8, icon: '🎸' },
    { id: 'bg8', x: 88, y: 75, size: 70, delay: 1, icon: '🎯' },
    { id: 'bg9', x: 82, y: 35, size: 64, delay: 2.2, icon: '🎲' },
    { id: 'bg10', x: 90, y: 88, size: 68, delay: 0.3, icon: '🎰' }
  ];

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;

      recognitionRef.current.onresult = (event: any) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        if (finalTranscript) {
          setTranscript(finalTranscript);
          setIsListening(false);
          playback(finalTranscript);
        }
      };

      recognitionRef.current.onend = () => {
        if (isListening && !isPlaying) {
          recognitionRef.current.start();
        }
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [isListening, isPlaying]);

  const playback = (text: string) => {
    setIsPlaying(true);
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.onend = () => {
      setIsPlaying(false);
      setTranscript('');
      setTimeout(() => {
        setIsListening(true);
        if (recognitionRef.current) {
          recognitionRef.current.start();
        }
      }, 500);
    };
    window.speechSynthesis.speak(utterance);
  };

  const fetchAndPlayAudio = async (text: string) => {
    try {
      setIsLoadingAudio(true);
      setShowContent(false);
      
      console.log('Fetching audio for text:', text);
      
      const response = await fetch('https://forgetmenot-eq7i.onrender.com/text-to-speech', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          name: 'therapist'
        })
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers.get('content-type'));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error Response:', errorText);
        alert(`Audio API Error (${response.status}): ${errorText}\n\nCheck console for details.`);
        throw new Error(`Failed to fetch audio: ${response.status}`);
      }
      
      const audioBlob = await response.blob();
      console.log('Audio blob size:', audioBlob.size, 'type:', audioBlob.type);
      const audioUrl = URL.createObjectURL(audioBlob);
      
      if (audioRef.current) {
        audioRef.current.pause();
        URL.revokeObjectURL(audioRef.current.src);
        audioRef.current = null;
      }
      
      const audio = new Audio(audioUrl);
      audio.volume = 1.0; // Ensure volume is at maximum
      audioRef.current = audio;
      
      audio.onloadeddata = () => {
        console.log('Audio loaded, duration:', audio.duration);
      };
      
      audio.onplay = () => {
        console.log('Audio started playing');
        setShowContent(true);
        setFadeKey(prev => prev + 1);
        setIsLoadingAudio(false);
      };
      
      audio.onended = () => {
        console.log('Audio ended');
        setIsPlaying(false);
      };
      
      audio.onerror = (e) => {
        console.error('Audio playback error:', e);
        setIsLoadingAudio(false);
        setShowContent(true);
        setIsPlaying(false);
      };
      
      setIsPlaying(true);
      console.log('Attempting to play audio...');
      await audio.play();
      console.log('Audio play() called successfully');
      
    } catch (error) {
      console.error('Error in fetchAndPlayAudio:', error);
      setIsLoadingAudio(false);
      setShowContent(true);
      setIsPlaying(false);
    }
  };

  const loadMemory = (index: number) => {
    if (index < 0 || index >= filteredMemories.length) return;
    
    const memory = filteredMemories[index];
    if (!memory) return;
    
    setCurrentMemoryIndex(index);
    setDisplayMode(memory.displayMode);
    setCurrentMedia(memory.media);
    fetchAndPlayAudio(memory.text);
  };

  const handlePrevious = () => {
    const newIndex = currentMemoryIndex > 0 ? currentMemoryIndex - 1 : filteredMemories.length - 1;
    loadMemory(newIndex);
  };

  const handleNext = () => {
    const newIndex = currentMemoryIndex < filteredMemories.length - 1 ? currentMemoryIndex + 1 : 0;
    loadMemory(newIndex);
  };

  const handleTopicClick = (topic: string) => {
    setSelectedTopic(topic);
    setCurrentMemoryIndex(0);
    const topicMemories = memories.filter(m => m.topic === topic);
    if (topicMemories.length > 0) {
      const memory = topicMemories[0];
      if (!memory) return;
      
      setDisplayMode(memory.displayMode);
      setCurrentMedia(memory.media);
      fetchAndPlayAudio(memory.text);
    }
  };

  useEffect(() => {
    setIsListening(true);
    if (recognitionRef.current) {
      recognitionRef.current.start();
    }
  }, []);

  return (
    <div style={{
      width: '100%',
      height: '100vh',
      background: '#000000',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      position: 'relative',
      overflow: 'hidden',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      {backgroundCircles.map((circle) => (
        <div key={circle.id} style={{ position: 'absolute', left: `${circle.x}%`, top: `${circle.y}%`, width: `${circle.size}px`, height: `${circle.size}px`, borderRadius: '50%', background: 'linear-gradient(135deg, rgba(0, 122, 255, 0.3), rgba(10, 132, 255, 0.2))', border: '2px solid rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(10px)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: `${circle.size * 0.5}px`, animation: `floatBackground 4s ease-in-out infinite`, animationDelay: `${circle.delay}s`, zIndex: 0, opacity: 0.7 }}>{circle.icon}</div>
      ))}

      <div style={{ position: 'relative', zIndex: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '40px' }}>
        {/* Left Arrow */}
        {selectedTopic && filteredMemories.length > 1 && (
          <button
            onClick={handlePrevious}
            disabled={isLoadingAudio}
            style={{
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              background: 'rgba(255, 255, 255, 0.15)',
              backdropFilter: 'blur(10px)',
              border: '2px solid rgba(255, 255, 255, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: isLoadingAudio ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s',
              opacity: isLoadingAudio ? 0.5 : 1
            }}
          >
            <ChevronLeft size={32} color="white" />
          </button>
        )}

        <div style={{ 
          width: displayMode === 'vertical-video' ? '320px' : '700px', 
          height: displayMode === 'vertical-video' ? '500px' : '400px', 
          borderRadius: '24px', 
          overflow: 'hidden',
          transition: 'all 0.5s ease',
          opacity: showContent ? 1 : 0.3
        }}>
          {showContent && displayMode === 'video' && currentMedia[0] && (
            <div key={`video-${fadeKey}`} className="fade-in" style={{ width: '100%', height: '100%' }}>
              <video autoPlay loop muted playsInline style={{ width: '100%', height: '100%', objectFit: 'cover' }}>
                <source src={currentMedia[0]} type="video/mp4" />
              </video>
            </div>
          )}
          
          {showContent && displayMode === 'vertical-video' && currentMedia[0] && (
            <div key={`vertical-video-${fadeKey}`} className="fade-in" style={{ width: '100%', height: '100%' }}>
              <video autoPlay loop muted playsInline style={{ width: '100%', height: '100%', objectFit: 'cover' }}>
                <source src={currentMedia[0]} type="video/mp4" />
              </video>
            </div>
          )}
          
          {showContent && displayMode === '3-pic' && (
            <div key={`3-pic-${fadeKey}`} className="fade-in" style={{ position: 'relative', width: '100%', height: '100%' }}>
              {currentMedia[0] && (
                <div className="photo" style={{ position: 'absolute', background: 'white', padding: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', width: '240px', height: '280px', top: '20px', left: '30px', transform: 'rotate(-7deg)', zIndex: 3, transition: 'transform 0.3s ease, z-index 0.3s' }} onMouseEnter={(e) => { e.currentTarget.style.transform = 'rotate(-7deg) scale(1.05)'; e.currentTarget.style.zIndex = '10'; }} onMouseLeave={(e) => { e.currentTarget.style.transform = 'rotate(-7deg)'; e.currentTarget.style.zIndex = '3'; }}>
                  <img src={currentMedia[0]} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                </div>
              )}
              {currentMedia[1] && (
                <div className="photo" style={{ position: 'absolute', background: 'white', padding: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', width: '280px', height: '260px', top: '10px', right: '40px', transform: 'rotate(5deg)', zIndex: 4, transition: 'transform 0.3s ease, z-index 0.3s' }} onMouseEnter={(e) => { e.currentTarget.style.transform = 'rotate(5deg) scale(1.05)'; e.currentTarget.style.zIndex = '10'; }} onMouseLeave={(e) => { e.currentTarget.style.transform = 'rotate(5deg)'; e.currentTarget.style.zIndex = '4'; }}>
                  <img src={currentMedia[1]} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                </div>
              )}
              {currentMedia[2] && (
                <div className="photo" style={{ position: 'absolute', background: 'white', padding: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', width: '240px', height: '240px', bottom: '30px', left: '220px', transform: 'rotate(6deg)', zIndex: 2, transition: 'transform 0.3s ease, z-index 0.3s' }} onMouseEnter={(e) => { e.currentTarget.style.transform = 'rotate(6deg) scale(1.05)'; e.currentTarget.style.zIndex = '10'; }} onMouseLeave={(e) => { e.currentTarget.style.transform = 'rotate(6deg)'; e.currentTarget.style.zIndex = '2'; }}>
                  <img src={currentMedia[2]} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                </div>
              )}
            </div>
          )}
          
          {showContent && displayMode === '4-pic' && (
            <div key={`4-pic-${fadeKey}`} className="fade-in" style={{ position: 'relative', width: '100%', height: '100%' }}>
              {currentMedia[0] && (
                <div className="photo" style={{ position: 'absolute', background: 'white', padding: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', width: '220px', height: '260px', top: '20px', left: '20px', transform: 'rotate(-6deg)', zIndex: 4, transition: 'transform 0.3s ease, z-index 0.3s' }} onMouseEnter={(e) => { e.currentTarget.style.transform = 'rotate(-6deg) scale(1.05)'; e.currentTarget.style.zIndex = '10'; }} onMouseLeave={(e) => { e.currentTarget.style.transform = 'rotate(-6deg)'; e.currentTarget.style.zIndex = '4'; }}>
                  <img src={currentMedia[0]} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                </div>
              )}
              {currentMedia[1] && (
                <div className="photo" style={{ position: 'absolute', background: 'white', padding: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', width: '240px', height: '240px', top: '15px', right: '30px', transform: 'rotate(4deg)', zIndex: 3, transition: 'transform 0.3s ease, z-index 0.3s' }} onMouseEnter={(e) => { e.currentTarget.style.transform = 'rotate(4deg) scale(1.05)'; e.currentTarget.style.zIndex = '10'; }} onMouseLeave={(e) => { e.currentTarget.style.transform = 'rotate(4deg)'; e.currentTarget.style.zIndex = '3'; }}>
                  <img src={currentMedia[1]} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                </div>
              )}
              {currentMedia[2] && (
                <div className="photo" style={{ position: 'absolute', background: 'white', padding: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', width: '230px', height: '230px', bottom: '30px', left: '80px', transform: 'rotate(7deg)', zIndex: 2, transition: 'transform 0.3s ease, z-index 0.3s' }} onMouseEnter={(e) => { e.currentTarget.style.transform = 'rotate(7deg) scale(1.05)'; e.currentTarget.style.zIndex = '10'; }} onMouseLeave={(e) => { e.currentTarget.style.transform = 'rotate(7deg)'; e.currentTarget.style.zIndex = '2'; }}>
                  <img src={currentMedia[2]} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                </div>
              )}
              {currentMedia[3] && (
                <div className="photo" style={{ position: 'absolute', background: 'white', padding: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', width: '250px', height: '250px', bottom: '25px', right: '50px', transform: 'rotate(-5deg)', zIndex: 1, transition: 'transform 0.3s ease, z-index 0.3s' }} onMouseEnter={(e) => { e.currentTarget.style.transform = 'rotate(-5deg) scale(1.05)'; e.currentTarget.style.zIndex = '10'; }} onMouseLeave={(e) => { e.currentTarget.style.transform = 'rotate(-5deg)'; e.currentTarget.style.zIndex = '1'; }}>
                  <img src={currentMedia[3]} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                </div>
              )}
            </div>
          )}
          
          {showContent && displayMode === '5-pic' && (
            <div key={`5-pic-${fadeKey}`} className="fade-in" style={{ position: 'relative', width: '100%', height: '100%' }}>
              {currentMedia[0] && (
                <div className="photo" style={{ position: 'absolute', background: 'white', padding: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', width: '200px', height: '250px', top: '40px', left: '40px', transform: 'rotate(-7deg)', zIndex: 3, transition: 'transform 0.3s ease, z-index 0.3s' }} onMouseEnter={(e) => { e.currentTarget.style.transform = 'rotate(-7deg) scale(1.05)'; e.currentTarget.style.zIndex = '10'; }} onMouseLeave={(e) => { e.currentTarget.style.transform = 'rotate(-7deg)'; e.currentTarget.style.zIndex = '3'; }}>
                  <img src={currentMedia[0]} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                </div>
              )}
              {currentMedia[1] && (
                <div className="photo" style={{ position: 'absolute', background: 'white', padding: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', width: '230px', height: '230px', top: '20px', right: '120px', transform: 'rotate(5deg)', zIndex: 4, transition: 'transform 0.3s ease, z-index 0.3s' }} onMouseEnter={(e) => { e.currentTarget.style.transform = 'rotate(5deg) scale(1.05)'; e.currentTarget.style.zIndex = '10'; }} onMouseLeave={(e) => { e.currentTarget.style.transform = 'rotate(5deg)'; e.currentTarget.style.zIndex = '4'; }}>
                  <img src={currentMedia[1]} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                </div>
              )}
              {currentMedia[2] && (
                <div className="photo" style={{ position: 'absolute', background: 'white', padding: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', width: '180px', height: '230px', top: '150px', left: '220px', transform: 'rotate(-4deg)', zIndex: 5, transition: 'transform 0.3s ease, z-index 0.3s' }} onMouseEnter={(e) => { e.currentTarget.style.transform = 'rotate(-4deg) scale(1.05)'; e.currentTarget.style.zIndex = '10'; }} onMouseLeave={(e) => { e.currentTarget.style.transform = 'rotate(-4deg)'; e.currentTarget.style.zIndex = '5'; }}>
                  <img src={currentMedia[2]} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                </div>
              )}
              {currentMedia[3] && (
                <div className="photo" style={{ position: 'absolute', background: 'white', padding: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', width: '200px', height: '200px', bottom: '50px', left: '30px', transform: 'rotate(6deg)', zIndex: 2, transition: 'transform 0.3s ease, z-index 0.3s' }} onMouseEnter={(e) => { e.currentTarget.style.transform = 'rotate(6deg) scale(1.05)'; e.currentTarget.style.zIndex = '10'; }} onMouseLeave={(e) => { e.currentTarget.style.transform = 'rotate(6deg)'; e.currentTarget.style.zIndex = '2'; }}>
                  <img src={currentMedia[3]} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                </div>
              )}
              {currentMedia[4] && (
                <div className="photo" style={{ position: 'absolute', background: 'white', padding: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.3)', width: '210px', height: '210px', bottom: '40px', right: '80px', transform: 'rotate(-5deg)', zIndex: 1, transition: 'transform 0.3s ease, z-index 0.3s' }} onMouseEnter={(e) => { e.currentTarget.style.transform = 'rotate(-5deg) scale(1.05)'; e.currentTarget.style.zIndex = '10'; }} onMouseLeave={(e) => { e.currentTarget.style.transform = 'rotate(-5deg)'; e.currentTarget.style.zIndex = '1'; }}>
                  <img src={currentMedia[4]} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Arrow */}
        {selectedTopic && filteredMemories.length > 1 && (
          <button
            onClick={handleNext}
            disabled={isLoadingAudio}
            style={{
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              background: 'rgba(255, 255, 255, 0.15)',
              backdropFilter: 'blur(10px)',
              border: '2px solid rgba(255, 255, 255, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: isLoadingAudio ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s',
              opacity: isLoadingAudio ? 0.5 : 1
            }}
          >
            <ChevronRight size={32} color="white" />
          </button>
        )}
      </div>

      <div style={{ position: 'absolute', top: '20px', left: '50%', transform: 'translateX(-50%)', zIndex: 50 }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
          <div style={{ display: 'flex', gap: '70px', justifyContent: 'center', flexWrap: 'wrap' }}>
            {suggestions.map((suggestion) => (
              <div 
                key={suggestion.id} 
                style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', cursor: 'pointer', transform: selectedTopic === suggestion.label ? 'scale(1.2)' : 'scale(1)', transition: 'transform 0.3s' }} 
                onClick={() => handleTopicClick(suggestion.label)}
              >
                <div style={{ 
                  width: '56px', 
                  height: '56px', 
                  borderRadius: '50%', 
                  background: selectedTopic === suggestion.label ? 'rgba(255, 255, 255, 0.3)' : 'rgba(255, 255, 255, 0.1)', 
                  backdropFilter: 'blur(10px)', 
                  border: selectedTopic === suggestion.label ? '3px solid rgba(255, 255, 255, 0.5)' : '1px solid rgba(255, 255, 255, 0.15)', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  fontSize: '28px', 
                  transition: 'all 0.3s ease',
                  boxShadow: selectedTopic === suggestion.label ? '0 0 20px rgba(255, 255, 255, 0.4)' : 'none'
                }}>
                  {suggestion.icon}
                </div>
                <span style={{ 
                  color: 'white', 
                  fontSize: selectedTopic === suggestion.label ? '14px' : '12px', 
                  fontWeight: selectedTopic === suggestion.label ? '700' : '500',
                  transition: 'all 0.3s'
                }}>
                  {suggestion.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={{ position: 'absolute', bottom: '30px', left: '50%', transform: 'translateX(-50%)', zIndex: 100 }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={() => {
              if (isListening) {
                setIsListening(false);
                if (recognitionRef.current) recognitionRef.current.stop();
              } else {
                setIsListening(true);
                if (recognitionRef.current) recognitionRef.current.start();
              }
            }}
            style={{
              width: '64px',
              height: '64px',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              transition: 'background 0.3s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'none'}
          >
            {isListening ? (
              <div style={{
                width: '24px',
                height: '24px',
                borderRadius: '4px',
                background: 'rgba(255, 255, 255, 0.5)',
                animation: 'spin 3s linear infinite'
              }} />
            ) : (
              <Mic size={24} color="rgba(255, 255, 255, 0.5)" />
            )}
          </button>

          <div style={{ height: '40px', width: '256px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '2px' }}>
            {[...Array(48)].map((_, i) => (
              <div
                key={i}
                style={{
                  width: '2px',
                  borderRadius: '9999px',
                  height: isListening ? `${20 + Math.random() * 80}%` : '4px',
                  background: isListening ? 'rgba(255, 255, 255, 0.5)' : 'rgba(255, 255, 255, 0.1)',
                  transition: 'all 0.3s',
                  animation: isListening ? 'pulse 1.5s ease-in-out infinite' : 'none',
                  animationDelay: `${i * 0.05}s`
                }}
              />
            ))}
          </div>

          <p style={{ height: '16px', fontSize: '12px', color: 'rgba(255, 255, 255, 0.7)' }}>
            {isListening ? 'Listening...' : 'Click to speak'}
          </p>
        </div>
      </div>

      <style>{`
        @keyframes floatBackground { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-20px); } }
        @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes fadeIn { 
          from { 
            opacity: 0; 
            transform: scale(0.95);
          } 
          to { 
            opacity: 1; 
            transform: scale(1);
          } 
        }
        .fade-in {
          animation: fadeIn 3s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

export default ImagePlaygroundUI;
