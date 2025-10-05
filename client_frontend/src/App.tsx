import React, { useState, useEffect, useRef } from 'react';
import { Mic } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

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
  const backgroundMusicRef = useRef<HTMLAudioElement | null>(null);
  const [isAudioReady, setIsAudioReady] = useState(false);
  const [isLoadingMusic, setIsLoadingMusic] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [petalsExplode, setPetalsExplode] = useState(false);

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

  const topicMusicPrompts: Record<string, string> = {
    'Avery': 'Warm nostalgic acoustic music with gentle piano and strings, peaceful and heartwarming atmosphere',
    'College': 'Upbeat inspiring music with hopeful melodies, celebrating achievement and new beginnings',
    'Disney': 'Magical whimsical orchestral music with wonder and excitement, playful and enchanting',
    'Ski': 'Energetic adventurous music with dynamic rhythms, capturing thrill and mountain atmosphere',
    'Football': 'Powerful triumphant sports anthem with driving beats and heroic brass, victory celebration',
    'Tyler': 'Cheerful uplifting music with bright melodies, youthful energy and joy'
  };

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
          // Don't auto-advance - user must click mic to advance
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

  const advanceToNextMemory = () => {
    if (!selectedTopic) return;
    
    const nextIndex = (currentMemoryIndex + 1) % filteredMemories.length;
    loadMemory(nextIndex);
  };

  const generateAndPlayBackgroundMusic = async (topic: string) => {
    try {
      setIsLoadingMusic(true);
      console.log('Generating background music for topic:', topic);
      
      const musicPrompt = topicMusicPrompts[topic];
      if (!musicPrompt) {
        console.warn('No music prompt found for topic:', topic);
        return;
      }

      const response = await fetch('https://forgetmenot-eq7i.onrender.com/text-to-sound', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: musicPrompt,
          duration_seconds: 15,
          prompt_influence: 0.5
        })
      });

      console.log('Music response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Music API Error:', errorText);
        setIsLoadingMusic(false);
        return;
      }
      
      const audioBlob = await response.blob();
      console.log('Music blob size:', audioBlob.size, 'type:', audioBlob.type);
      const audioUrl = URL.createObjectURL(audioBlob);
      
      if (backgroundMusicRef.current) {
        backgroundMusicRef.current.pause();
        URL.revokeObjectURL(backgroundMusicRef.current.src);
        backgroundMusicRef.current = null;
      }
      
      const music = new Audio(audioUrl);
      music.volume = 0.15;
      music.loop = true;
      backgroundMusicRef.current = music;
      
      music.oncanplaythrough = () => {
        console.log('Background music ready to play');
        setIsLoadingMusic(false);
      };
      
      music.onerror = (e) => {
        console.error('Background music error:', e);
        setIsLoadingMusic(false);
      };
      
      await music.play();
      console.log('Background music started playing');
      
    } catch (error) {
      console.error('Error generating background music:', error);
      setIsLoadingMusic(false);
    }
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
        
        // Always trigger explosion when audio plays
        setPetalsExplode(true);
        
        // Wait for explosion to complete
        setTimeout(() => {
          setIsTransitioning(false);
          setShowContent(true);
        }, 500);
        
        setFadeKey(prev => prev + 1);
        setIsLoadingAudio(false);
        setIsAudioReady(true); // Show mic button when audio is ready
      };
      
      audio.onended = () => {
        console.log('Audio ended');
        setIsPlaying(false);
        // Keep content visible when audio ends naturally
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
    
    // Fade out current content
    setShowContent(false);
    
    // Stop current audio playback
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    
    // Reset states but keep mic visible (don't set isAudioReady to false)
    setIsListening(false);
    setIsPlaying(false);
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    
    // Wait for content to fade out (1 second), then show flower
    setTimeout(() => {
      setIsTransitioning(true);
      setPetalsExplode(false);
      
      // Load content after flower appears
      setCurrentMemoryIndex(index);
      setDisplayMode(memory.displayMode);
      setCurrentMedia(memory.media);
      fetchAndPlayAudio(memory.text);
    }, 1000);
  };

  const handleMicClick = () => {
    if (isPlaying) {
      // Interrupt audio and start listening (don't fade content)
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      setIsPlaying(false);
      setIsListening(true);
      if (recognitionRef.current) {
        recognitionRef.current.start();
      }
    } else if (isListening) {
      // Stop listening and advance to next memory (this will fade content)
      setIsListening(false);
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      advanceToNextMemory();
    } else {
      // Start listening
      setIsListening(true);
      if (recognitionRef.current) {
        recognitionRef.current.start();
      }
    }
  };

  const handleTopicClick = (topic: string) => {
    // Don't process if already processing this topic
    if (selectedTopic === topic) return;
    
    // Fade out current content if any
    if (selectedTopic) {
      setShowContent(false);
    }
    
    // Stop all audio and reset states
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    
    if (backgroundMusicRef.current) {
      backgroundMusicRef.current.pause();
      URL.revokeObjectURL(backgroundMusicRef.current.src);
      backgroundMusicRef.current = null;
    }
    
    setSelectedTopic(topic);
    setCurrentMemoryIndex(0);
    setIsAudioReady(false);
    setIsListening(false);
    setIsPlaying(false);
    
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    
    // Generate background music for this topic
    generateAndPlayBackgroundMusic(topic);
    
    const topicMemories = memories.filter(m => m.topic === topic);
    if (topicMemories.length > 0) {
      const memory = topicMemories[0];
      if (!memory) return;
      
      // Wait for start screen to fade out (1 second), then show flower
      setTimeout(() => {
        setIsTransitioning(true);
        setPetalsExplode(false);
        
        // Load content after flower appears
        setDisplayMode(memory.displayMode);
        setCurrentMedia(memory.media);
        fetchAndPlayAudio(memory.text);
      }, 1000);
    }
  };

  useEffect(() => {
    // Don't auto-start listening - wait for first memory to load
    
    return () => {
      if (backgroundMusicRef.current) {
        backgroundMusicRef.current.pause();
        backgroundMusicRef.current = null;
      }
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
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
      fontFamily: 'Georgia, serif'
    }}>
      {backgroundCircles.map((circle) => (
        <div key={circle.id} style={{ position: 'absolute', left: `${circle.x}%`, top: `${circle.y}%`, width: `${circle.size}px`, height: `${circle.size}px`, borderRadius: '50%', background: 'linear-gradient(135deg, rgba(123, 168, 193, 0.3), rgba(123, 168, 193, 0.2))', border: '2px solid rgba(123, 168, 193, 0.2)', backdropFilter: 'blur(10px)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: `${circle.size * 0.5}px`, animation: `floatBackground 4s ease-in-out infinite`, animationDelay: `${circle.delay}s`, zIndex: 0, opacity: 0.7 }}>{circle.icon}</div>
      ))}

      {/* Starting Screen */}
      <AnimatePresence>
        {!selectedTopic && (
          <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1, ease: 'easeInOut' }}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 15,
              pointerEvents: 'none'
            }}
          >
          <div style={{ textAlign: 'center', zIndex: 1, marginBottom: '80px' }}>
            <h1 style={{
              color: 'white',
              fontSize: '96px',
              fontFamily: 'Georgia, serif',
              marginBottom: '10px',
              marginTop: '0',
              letterSpacing: '2px',
              textShadow: '0 0 30px rgba(0,0,0,0.8), 0 0 60px rgba(0,0,0,0.5)'
            }}>
              Forget Me Not
            </h1>
            <p style={{
              color: 'white',
              fontSize: '32px',
              fontFamily: 'Georgia, serif',
              fontStyle: 'italic',
              margin: '0',
              letterSpacing: '1px',
              textShadow: '0 0 20px rgba(0,0,0,0.8), 0 0 40px rgba(0,0,0,0.5)'
            }}>
              Remembering is recovering
            </p>
          </div>
          
          <svg width="300" height="375" viewBox="0 0 200 250" style={{ position: 'absolute', bottom: '0', animation: 'bloomUp 2s ease-out forwards, sway 4s ease-in-out 2s infinite', transformOrigin: 'center bottom' }}>
            {/* Stem */}
            <path
              d="M 100 250 Q 95 180 100 150 Q 105 120 100 80"
              stroke="#2d5016"
              strokeWidth="4"
              fill="none"
            />
            
            {/* Branch stems */}
            <path d="M 100 150 Q 85 140 75 130" stroke="#2d5016" strokeWidth="2" fill="none" />
            <path d="M 100 120 Q 120 110 135 100" stroke="#2d5016" strokeWidth="2" fill="none" />
            
            {/* Flower 1 - Main large flower */}
            <g transform="translate(100, 80)">
              {[0, 72, 144, 216, 288].map((angle, i) => (
                <g key={`main-${i}`} transform={`rotate(${angle})`}>
                  <ellipse
                    cx="0"
                    cy="-18"
                    rx="12"
                    ry="16"
                    fill="#7ba8c1"
                    opacity="0.9"
                  />
                </g>
              ))}
              <circle cx="0" cy="0" r="7" fill="#f4d03f" />
            </g>
            
            {/* Flower 2 - Left smaller flower */}
            <g transform="translate(75, 130)">
              {[0, 72, 144, 216, 288].map((angle, i) => (
                <g key={`left-${i}`} transform={`rotate(${angle})`}>
                  <ellipse
                    cx="0"
                    cy="-14"
                    rx="9"
                    ry="12"
                    fill="#7ba8c1"
                    opacity="0.9"
                  />
                </g>
              ))}
              <circle cx="0" cy="0" r="5" fill="#f4d03f" />
            </g>
            
            {/* Flower 3 - Right smaller flower */}
            <g transform="translate(135, 100)">
              {[0, 72, 144, 216, 288].map((angle, i) => (
                <g key={`right-${i}`} transform={`rotate(${angle})`}>
                  <ellipse
                    cx="0"
                    cy="-12"
                    rx="8"
                    ry="10"
                    fill="#7ba8c1"
                    opacity="0.9"
                  />
                </g>
              ))}
              <circle cx="0" cy="0" r="4" fill="#f4d03f" />
            </g>
          </svg>
          </motion.div>
        )}
      </AnimatePresence>

      <div style={{ position: 'relative', zIndex: 10, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <AnimatePresence mode="wait">
          {showContent && (
            <motion.div
              key={`content-${currentMemoryIndex}`}
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              transition={{ duration: 1, ease: 'easeInOut' }}
              style={{ 
                width: displayMode === 'vertical-video' ? '320px' : '700px', 
                height: displayMode === 'vertical-video' ? '500px' : '400px', 
                borderRadius: '24px', 
                overflow: 'hidden'
              }}
            >
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
            </motion.div>
          )}
        </AnimatePresence>
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

      {/* Music Loading Indicator */}
      {/* Loading Flower */}
      <AnimatePresence>
        {isTransitioning && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.3 }}
            style={{
              position: 'fixed',
              top: '50%',
              left: '50%',
              zIndex: 150,
              pointerEvents: 'none',
              width: '120px',
              height: '120px',
              marginLeft: '-60px',
              marginTop: '-60px'
            }}
          >
            <svg width="120" height="120" viewBox="0 0 160 160" style={{ display: 'block' }}>
              <g className={!petalsExplode ? 'rotating' : ''} style={{ transformOrigin: '80px 80px' }}>
                {[0, 1, 2, 3, 4].map((i) => {
                  const angle = i * 72;
                  const radians = (angle - 90) * (Math.PI / 180);
                  const distance = 20;
                  const x = 80 + Math.cos(radians) * distance;
                  const y = 80 + Math.sin(radians) * distance;
                  const explodeDistance = 60;
                  const explodeX = Math.cos(radians) * explodeDistance;
                  const explodeY = Math.sin(radians) * explodeDistance;
                  
                  return (
                    <g
                      key={i}
                      transform={`translate(${x}, ${y})`}
                      style={{
                        animation: petalsExplode ? `explode-${i} 0.5s ease-out forwards` : 'none'
                      }}
                    >
                      <ellipse
                        cx="0"
                        cy="0"
                        rx="14"
                        ry="18"
                        fill="#7ba8c1"
                        opacity="0.9"
                        transform={`rotate(${angle})`}
                      />
                    </g>
                  );
                })}
                <circle
                  cx="80"
                  cy="80"
                  r="8"
                  fill="#f4d03f"
                  className={petalsExplode ? 'center-fade' : ''}
                />
              </g>
            </svg>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Only show mic button when audio is ready */}
      <AnimatePresence>
        {isAudioReady && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1, ease: 'easeInOut' }}
            style={{ 
              position: 'absolute', 
              bottom: '30px', 
              left: '50%', 
              transform: 'translateX(-50%)', 
              zIndex: 100
            }}
          >
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={handleMicClick}
            disabled={isLoadingAudio}
            style={{
              width: '64px',
              height: '64px',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: 'none',
              border: 'none',
              cursor: isLoadingAudio ? 'not-allowed' : 'pointer',
              transition: 'background 0.3s',
              opacity: isLoadingAudio ? 0.5 : 1
            }}
            onMouseEnter={(e) => !isLoadingAudio && (e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)')}
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
            {isPlaying ? 'Remembering...' : isListening ? 'Listening...' : 'Click to speak'}
          </p>
        </div>
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`
        @keyframes floatBackground { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-20px); } }
        @keyframes pulse { 
          0%, 100% { transform: scale(1); opacity: 1; } 
          50% { transform: scale(1.1); opacity: 0.8; } 
        }
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
        @keyframes bloomUp {
          from {
            transform: translateY(100%);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
        @keyframes sway {
          0% {
            transform: translateY(0) rotate(2deg);
          }
          50% {
            transform: translateY(0) rotate(-2deg);
          }
          100% {
            transform: translateY(0) rotate(2deg);
          }
        }
        .rotating {
          animation: rotate 2s linear infinite;
          transform-origin: 80px 80px;
          transform: rotate(36deg);
        }
        @keyframes rotate {
          from { transform: rotate(36deg); }
          to { transform: rotate(396deg); }
        }
        @keyframes explode-0 {
          to {
            transform: translate(137.08px, 23.51px);
            opacity: 0;
          }
        }
        @keyframes explode-1 {
          to {
            transform: translate(129.27px, 62.36px);
            opacity: 0;
          }
        }
        @keyframes explode-2 {
          to {
            transform: translate(91.42px, 91.42px);
            opacity: 0;
          }
        }
        @keyframes explode-3 {
          to {
            transform: translate(42.36px, 69.27px);
            opacity: 0;
          }
        }
        @keyframes explode-4 {
          to {
            transform: translate(22.92px, 23.51px);
            opacity: 0;
          }
        }
        .center-fade {
          animation: fade-out 0.5s ease-out forwards;
        }
        @keyframes fade-out {
          to { opacity: 0; }
        }
        .fade-in {
          animation: fadeIn 1s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

export default ImagePlaygroundUI;
