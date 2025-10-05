"use client";

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface Folder {
  name: string;
  path: string;
  previewImage: string | null;
  imageCount: number;
  images: string[];
}

interface Bubble {
  id: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  image: string;
  name: string;
  originalX: number;
  originalY: number;
  currentX: number;
  currentY: number;
}

export default function FaceNamingPage() {
  const [folders, setFolders] = useState<Folder[]>([]);
  const [currentFolderIndex, setCurrentFolderIndex] = useState(0);
  const [bubbles, setBubbles] = useState<Bubble[]>([]);
  const mousePos = useRef({ x: -1000, y: -1000 });
  const animationFrameId = useRef<number | null>(null);
  const [assignedName, setAssignedName] = useState('');
  const [savedNames, setSavedNames] = useState<{ [key: string]: string }>({});
  const [showSummary, setShowSummary] = useState(false);
  const [allAssignments, setAllAssignments] = useState<{ [folderName: string]: string }>({});
  const [expandedNames, setExpandedNames] = useState<Set<string>>(new Set());
  const canvasRef = useRef<HTMLDivElement>(null);
  const summaryContainerRef = useRef<HTMLDivElement>(null);
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });

  // Load existing named faces
  useEffect(() => {
    async function loadNamedFaces() {
      try {
        const res = await fetch('/data/named-faces.json');
        const data = await res.json();
        setSavedNames(data);
      } catch (error) {
        console.error('Error loading named faces:', error);
      }
    }
    loadNamedFaces();
  }, []);

  // Fetch folders
  useEffect(() => {
    async function fetchFolders() {
      try {
        const res = await fetch('/api/people');
        const data = await res.json();
        if (data.folders) {
          setFolders(data.folders);
        }
      } catch (error) {
        console.log('API not available, using mock data for testing');
        // Mock data for testing when API is unavailable
        setFolders([]);
      }
    }
    fetchFolders();
  }, []);

  // Initialize bubbles when folder changes
  useEffect(() => {
    if (folders.length > 0 && currentFolderIndex < folders.length) {
      const currentFolder = folders[currentFolderIndex];
      const newBubbles: Bubble[] = currentFolder.images.map((image, index) => {
        const angle = (index / currentFolder.images.length) * Math.PI * 2;
        const radius = 200;
        const centerX = window.innerWidth / 2;
        const centerY = window.innerHeight / 2;
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        
        return {
          id: `${currentFolder.name}-${index}`,
          x,
          y,
          vx: (Math.random() - 0.5) * 2,
          vy: (Math.random() - 0.5) * 2,
          size: 80 + Math.random() * 40,
          image: `/${currentFolder.path}/${image}`,
          name: '',
          originalX: x,
          originalY: y,
          currentX: x,
          currentY: y
        };
      });
      setBubbles(newBubbles);
    }
  }, [folders, currentFolderIndex]);

  // Track mouse position with useRef (no re-renders)
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      mousePos.current = { x: e.clientX, y: e.clientY };
    };
    
    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Optimized physics with requestAnimationFrame
  useEffect(() => {
    if (bubbles.length === 0) return;
    
    const repelRadius = 150;
    const repelRadiusSq = repelRadius * repelRadius; // Avoid sqrt when possible
    
    const animate = () => {
      setBubbles(prev => {
        const mouse = mousePos.current;
        
        return prev.map(bubble => {
          const dx = bubble.currentX - mouse.x;
          const dy = bubble.currentY - mouse.y;
          const distanceSq = dx * dx + dy * dy;
          
          let targetX = bubble.originalX;
          let targetY = bubble.originalY;
          
          // Only calculate if within repel radius (squared comparison is faster)
          if (distanceSq < repelRadiusSq && distanceSq > 0) {
            const distance = Math.sqrt(distanceSq);
            const force = (repelRadius - distance) / repelRadius;
            const pushX = (dx / distance) * force * 80;
            const pushY = (dy / distance) * force * 80;
            targetX = bubble.originalX + pushX;
            targetY = bubble.originalY + pushY;
          }
          
          // Check if already at target (avoid unnecessary updates)
          const diffX = targetX - bubble.currentX;
          const diffY = targetY - bubble.currentY;
          
          if (Math.abs(diffX) < 0.1 && Math.abs(diffY) < 0.1) {
            return bubble;
          }
          
          // Smoothly move towards target
          return {
            ...bubble,
            currentX: bubble.currentX + diffX * 0.15,
            currentY: bubble.currentY + diffY * 0.15
          };
        });
      });
      
      animationFrameId.current = requestAnimationFrame(animate);
    };
    
    animationFrameId.current = requestAnimationFrame(animate);
    
    return () => {
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, [bubbles.length]);

  const handleNameAll = () => {
    if (!assignedName.trim()) {
      alert('Please enter a name!');
      return;
    }

    const currentFolder = folders[currentFolderIndex];
    
    // Store the assignment
    setAllAssignments(prev => ({
      ...prev,
      [currentFolder.name]: assignedName
    }));
    
    setAssignedName('');
    
    // Move to next folder or show summary
    if (currentFolderIndex < folders.length - 1) {
      setCurrentFolderIndex(prev => prev + 1);
    } else {
      // All folders named, show summary
      setShowSummary(true);
    }
  };

  const handleSaveFinal = async () => {
    // Convert assignments to the format expected by the API
    const output: { [key: string]: string } = {};
    
    Object.entries(allAssignments).forEach(([folderName, personName]) => {
      if (personName && personName.trim()) {
        if (!output[personName]) {
          output[personName] = '';
        }
        output[personName] += (output[personName] ? ',' : '') + folderName;
      }
    });

    try {
      const response = await fetch('/api/save-faces', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(output),
      });

      if (response.ok) {
        alert('All names saved successfully! 🎉');
        // Reset to start
        setShowSummary(false);
        setAllAssignments({});
        setCurrentFolderIndex(0);
      } else {
        alert('Error saving names.');
      }
    } catch (error) {
      console.error('API not available:', error);
      // Allow testing without API - just show success
      console.log('Would have saved:', output);
      alert('✅ Testing mode: Names logged to console (API disabled)');
      setShowSummary(false);
      setAllAssignments({});
      setCurrentFolderIndex(0);
    }
  };

  const handleSkip = () => {
    if (currentFolderIndex < folders.length - 1) {
      setCurrentFolderIndex(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentFolderIndex > 0) {
      setCurrentFolderIndex(prev => prev - 1);
    }
  };

  const currentFolder = folders[currentFolderIndex];

  // Pan handlers - using wheel/trackpad
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    setPanOffset(prev => ({
      x: prev.x - e.deltaX,
      y: prev.y - e.deltaY
    }));
  };

  const toggleNameExpansion = (name: string) => {
    const newExpanded = new Set(expandedNames);
    if (newExpanded.has(name)) {
      newExpanded.delete(name);
    } else {
      newExpanded.add(name);
    }
    setExpandedNames(newExpanded);
  };

  // Summary view after all folders are named
  if (showSummary) {
    // Group by assigned name
    const nameGroups: { [name: string]: Array<{ folder: Folder; image: string }> } = {};
    
    folders.forEach((folder) => {
      const assignedName = allAssignments[folder.name] || 'Unnamed';
      if (!nameGroups[assignedName]) {
        nameGroups[assignedName] = [];
      }
      folder.images.forEach((image) => {
        nameGroups[assignedName].push({
          folder,
          image: `/${folder.path}/${image}`
        });
      });
    });

    const uniqueNames = Object.keys(nameGroups);
    
    // Calculate grid layout for name labels with generous spacing
    const gridCols = Math.ceil(Math.sqrt(uniqueNames.length));
    const gridRows = Math.ceil(uniqueNames.length / gridCols);
    const cellWidth = 500;
    const cellHeight = 500;
    const totalWidth = gridCols * cellWidth;
    const totalHeight = gridRows * cellHeight;

    return (
      <div 
        ref={summaryContainerRef}
        className="relative w-screen h-screen overflow-hidden bg-slate-900"
        onWheel={handleWheel}
        style={{ cursor: 'default' }}
      >
        {/* Pannable content container */}
        <div
          className="absolute"
          style={{
            left: `calc(50% + ${panOffset.x}px)`,
            top: `calc(50% + ${panOffset.y}px)`,
            transform: 'translate(-50%, -50%)',
            width: totalWidth,
            height: totalHeight,
            transition: isPanning ? 'none' : 'all 0.3s ease-out'
          }}
        >
          {/* Name groups */}
          {uniqueNames.map((name, index) => {
            const col = index % gridCols;
            const row = Math.floor(index / gridCols);
            const x = col * cellWidth + cellWidth / 2;
            const y = row * cellHeight + cellHeight / 2;
            const isExpanded = expandedNames.has(name);
            const bubbles = nameGroups[name];
            const count = bubbles.length;

            return (
              <div
                key={index}
                className="absolute"
                style={{
                  left: x,
                  top: y,
                  transform: 'translate(-50%, -50%)'
                }}
              >
                {/* Face bubbles - only shown when expanded */}
                {isExpanded && (
                  <div className="absolute top-0 left-0">
                    {bubbles.map((bubble, bubbleIndex) => {
                      const bubbleSize = 70;
                      const minSpacing = bubbleSize + 12;
                      const minRadius = count > 1 
                        ? Math.max(100, (count * minSpacing) / (2 * Math.PI))
                        : 80;
                      const radiusMultiplier = count > 15 ? 1.15 : count > 8 ? 1.1 : 1.05;
                      const radius = minRadius * radiusMultiplier;
                      
                      const angle = (bubbleIndex / count) * Math.PI * 2;
                      const bubbleX = Math.cos(angle) * radius;
                      const bubbleY = Math.sin(angle) * radius;

                      return (
                        <div
                          key={bubbleIndex}
                          className="absolute animate-in fade-in zoom-in duration-500"
                          style={{
                            left: bubbleX,
                            top: bubbleY,
                            width: bubbleSize,
                            height: bubbleSize,
                            transform: 'translate(-50%, -50%)',
                            animationDelay: `${bubbleIndex * 40}ms`
                          }}
                        >
                          <div className="relative w-full h-full group/bubble">
                            <div className="absolute inset-0 rounded-full bg-gradient-to-br from-cyan-400 via-blue-500 to-purple-600 opacity-50 blur-md group-hover/bubble:opacity-90 group-hover/bubble:scale-110 transition-all duration-500"></div>
                            <div className="absolute inset-1 rounded-full overflow-hidden border-2 border-white/40 shadow-xl bg-white/10 group-hover/bubble:border-white/70 group-hover/bubble:scale-105 transition-all duration-300">
                              <img
                                src={bubble.image}
                                alt={bubble.folder.name}
                                className="w-full h-full object-cover group-hover/bubble:scale-110 transition-transform duration-700"
                              />
                            </div>
                            <div className="absolute inset-1 rounded-full bg-gradient-to-br from-white/40 via-transparent to-transparent pointer-events-none opacity-60 group-hover/bubble:opacity-100 transition-opacity duration-300"></div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Name label - clickable - positioned on top of faces */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleNameExpansion(name);
                  }}
                  className="relative bg-gradient-to-br from-white via-white to-gray-50 rounded-2xl px-8 py-4 shadow-2xl border border-white/80 hover:border-purple-300 hover:shadow-purple-500/20 transition-all hover:scale-110 cursor-pointer z-10 group"
                  style={{ pointerEvents: 'auto' }}
                >
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-purple-500/0 to-pink-500/0 group-hover:from-purple-500/10 group-hover:to-pink-500/10 transition-all"></div>
                  <p className="text-2xl font-bold text-gray-900 whitespace-nowrap relative">{name}</p>
                  <p className="text-sm text-gray-600 text-center relative flex items-center justify-center gap-2">
                    <span>{count} photo{count !== 1 ? 's' : ''}</span>
                    <span className="transition-transform group-hover:scale-125">
                      {isExpanded ? '▼' : '▶'}
                    </span>
                  </p>
                </button>
              </div>
            );
          })}
        </div>

        {/* Instructions overlay */}
        <div className="absolute top-4 left-4 z-50 pointer-events-none animate-in fade-in duration-1000">
          <div className="bg-black/20 backdrop-blur-sm rounded-lg px-4 py-2 text-white border border-white/10">
            <p className="text-sm text-white/80">
              💡 Click names • Scroll to explore
            </p>
          </div>
        </div>

        {/* Bottom Controls */}
        <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-slate-900/80 via-slate-900/40 to-transparent z-50 pointer-events-none">
          <div className="max-w-2xl mx-auto pointer-events-auto">
            <div className="flex gap-4 justify-center animate-in slide-in-from-bottom duration-500">
              <Button
                onClick={() => {
                  setShowSummary(false);
                  setCurrentFolderIndex(0);
                  setPanOffset({ x: 0, y: 0 });
                  setExpandedNames(new Set());
                }}
                variant="outline"
                className="h-14 px-8 text-lg bg-white/10 backdrop-blur-sm border-white/20 text-white hover:bg-white/20 hover:scale-105 transition-all"
              >
                ← Edit Names
              </Button>
              <Button
                onClick={handleSaveFinal}
                className="h-14 px-10 text-lg font-bold bg-gradient-to-r from-green-500 via-emerald-500 to-teal-500 hover:from-green-600 hover:via-emerald-600 hover:to-teal-600 text-white shadow-xl hover:shadow-2xl hover:scale-105 transition-all active:scale-95"
              >
                <span className="mr-2">💾</span> Save Everything
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 w-screen h-screen overflow-hidden bg-slate-900">

      {/* Bubbles - Optimized Display */}
      <div ref={canvasRef} className="absolute inset-0">
        {bubbles.map((bubble) => (
          <div
            key={bubble.id}
            className="absolute will-change-transform"
            style={{
              left: bubble.currentX - bubble.size / 2,
              top: bubble.currentY - bubble.size / 2,
              width: bubble.size,
              height: bubble.size,
              transform: 'translateZ(0)' // Force GPU acceleration
            }}
          >
            <div className="relative w-full h-full group cursor-pointer">
              {/* Glow effect */}
              <div className="absolute inset-0 rounded-full bg-gradient-to-br from-pink-400 via-purple-500 to-indigo-600 opacity-40 blur-lg group-hover:opacity-80 group-hover:scale-110 transition-all duration-500"></div>
              
              {/* Bubble */}
              <div className="absolute inset-2 rounded-full overflow-hidden border-2 border-white/40 shadow-xl bg-white/5 group-hover:border-white/70 group-hover:scale-105 transition-all duration-300">
                <img
                  src={bubble.image}
                  alt="Face"
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                />
              </div>
              
              {/* Shine effect */}
              <div className="absolute inset-2 rounded-full bg-gradient-to-br from-white/30 via-transparent to-transparent pointer-events-none opacity-60 group-hover:opacity-100 transition-opacity duration-300"></div>
              
              {/* Sparkle on hover */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <div className="absolute top-2 right-2 w-2 h-2 bg-white rounded-full animate-ping"></div>
                <div className="absolute bottom-3 left-3 w-1.5 h-1.5 bg-white rounded-full animate-pulse"></div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* UI Controls */}
      <div className="absolute top-0 left-0 right-0 p-6 bg-gradient-to-b from-slate-900/80 via-slate-900/40 to-transparent z-10">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-4 animate-in slide-in-from-top duration-500">
            <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-purple-300 to-pink-300">
              Who is this?
            </h1>
            <div className="text-white text-lg font-semibold bg-white/10 backdrop-blur-sm px-6 py-2 rounded-full border border-white/20 animate-in fade-in duration-700">
              {currentFolderIndex + 1} / {folders.length}
            </div>
          </div>
          
          {currentFolder && (
            <div className="text-center mb-4 animate-in fade-in slide-in-from-top duration-700 delay-200">
              <p className="text-xl font-semibold text-white/90 drop-shadow-lg">
                {currentFolder.imageCount} photo{currentFolder.imageCount !== 1 ? 's' : ''} found
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Controls */}
      <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-slate-900/80 via-slate-900/40 to-transparent z-10">
        <div className="max-w-2xl mx-auto">
          <div className="flex gap-4 items-center justify-center mb-4 animate-in slide-in-from-bottom duration-500">
            <Input
              value={assignedName}
              onChange={(e) => setAssignedName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleNameAll()}
              placeholder="Type a name..."
              className="flex-1 h-14 text-lg bg-white/95 backdrop-blur-sm border-2 border-white/30 focus:border-purple-400 text-gray-900 placeholder:text-gray-400 shadow-lg hover:shadow-xl transition-all"
            />
            <Button
              onClick={handleNameAll}
              className="h-14 px-8 text-lg font-bold bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg hover:shadow-2xl hover:scale-105 transition-all active:scale-95"
            >
              Assign
            </Button>
          </div>
          
          <div className="flex gap-4 justify-center animate-in fade-in duration-700 delay-200">
            <Button
              onClick={handlePrevious}
              disabled={currentFolderIndex === 0}
              variant="outline"
              className="bg-white/10 backdrop-blur-sm border-white/20 text-white hover:bg-white/20 hover:scale-105 disabled:opacity-30 disabled:hover:scale-100 transition-all"
            >
              ← Back
            </Button>
            <Button
              onClick={handleSkip}
              disabled={currentFolderIndex >= folders.length - 1}
              variant="outline"
              className="bg-white/10 backdrop-blur-sm border-white/20 text-white hover:bg-white/20 hover:scale-105 disabled:opacity-30 disabled:hover:scale-100 transition-all"
            >
              Skip →
            </Button>
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none z-0">
        <p className="text-white/30 text-xl font-bold text-center">
        </p>
      </div>

      <style jsx>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          25% { transform: translate(20px, -50px) scale(1.1); }
          50% { transform: translate(-20px, 20px) scale(0.9); }
          75% { transform: translate(50px, 50px) scale(1.05); }
        }
        
        .animate-blob {
          animation: blob 7s infinite;
        }
        
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
}