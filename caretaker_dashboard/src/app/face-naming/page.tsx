"use client";

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { extractFaces, saveNamedFaces, parseExtractedFacesZip } from '@/lib/api-client';
import { Upload, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

interface Folder {
  name: string;
  path: string;
  previewImage: string | null;
  imageCount: number;
  images: string[];
  imageUrls: string[];
}

type ProcessingStage = 'upload' | 'extracting' | 'naming' | 'generating' | 'complete' | 'error';

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
  
  // Enlarged bubble modal state
  const [enlargedBubble, setEnlargedBubble] = useState<Bubble | null>(null);
  
  // API Integration State
  const [processingStage, setProcessingStage] = useState<ProcessingStage>('upload');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [extractedZipBlob, setExtractedZipBlob] = useState<Blob | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [processingProgress, setProcessingProgress] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Handle file upload
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.name.endsWith('.zip')) {
      setUploadedFile(file);
      setErrorMessage('');
    } else {
      setErrorMessage('Please upload a ZIP file containing your memories folder');
    }
  };

  // Step 1: Extract faces from uploaded ZIP
  const handleExtractFaces = async (useMock: boolean = false) => {
    if (!uploadedFile && !useMock) {
      setErrorMessage('Please upload a ZIP file first');
      return;
    }

    setProcessingStage('extracting');
    setProcessingProgress(useMock ? '🎭 Demo Mode: Extracting faces from mock data...' : 'Extracting faces from your uploaded file...');
    setErrorMessage('');

    try {
      // Call extract-faces API (will use mock data if useMock is true)
      const zipBlob = await extractFaces(uploadedFile!, useMock);
      setExtractedZipBlob(zipBlob);
      
      setProcessingProgress('Parsing extracted faces...');
      
      // Parse the ZIP to get folder structure
      const { folders: extractedFolders } = await parseExtractedFacesZip(zipBlob);
      
      // Convert to Folder format
      const formattedFolders: Folder[] = extractedFolders.map(folder => ({
        name: folder.name,
        path: folder.name,
        previewImage: folder.imageUrls[0] || null,
        imageCount: folder.images.length,
        images: folder.images,
        imageUrls: folder.imageUrls,
      }));
      
      setFolders(formattedFolders);
      setProcessingStage('naming');
      setProcessingProgress('');
      setCurrentFolderIndex(0);
    } catch (error: any) {
      console.error('Error extracting faces:', error);
      setErrorMessage(error.message || 'Failed to extract faces. Please try again.');
      setProcessingStage('error');
    }
  };

  // Initialize bubbles when folder changes
  useEffect(() => {
    if (folders.length > 0 && currentFolderIndex < folders.length && processingStage === 'naming') {
      const currentFolder = folders[currentFolderIndex];
      // Add cache-busting to force browser to reload new images
      const cacheBuster = Date.now();
      const newBubbles: Bubble[] = currentFolder.imageUrls.map((imageUrl, index) => {
        const angle = (index / currentFolder.imageUrls.length) * Math.PI * 2;
        const radius = 200;
        const centerX = window.innerWidth / 2;
        const centerY = window.innerHeight / 2;
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        
        // Add cache buster to image URL
        const imageWithCacheBuster = imageUrl.includes('?') 
          ? `${imageUrl}&v=${cacheBuster}` 
          : `${imageUrl}?v=${cacheBuster}`;
        
        return {
          id: `${currentFolder.name}-${index}`,
          x,
          y,
          vx: (Math.random() - 0.5) * 2,
          vy: (Math.random() - 0.5) * 2,
          size: 80 + Math.random() * 40,
          image: imageWithCacheBuster,
          name: '',
          originalX: x,
          originalY: y,
          currentX: x,
          currentY: y
        };
      });
      setBubbles(newBubbles);
    }
  }, [folders, currentFolderIndex, processingStage]);

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
    if (bubbles.length === 0 || processingStage !== 'naming') return;
    
    const repelRadius = 100; // Reduced from 150
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
            const pushX = (dx / distance) * force * 40; // Reduced from 80
            const pushY = (dy / distance) * force * 40; // Reduced from 80
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

  const handleSaveFinal = async (useMock: boolean = false) => {
    setProcessingStage('generating');
    setProcessingProgress('Saving named faces to backend...');
    setShowSummary(false);
    setErrorMessage('');

    try {
      // Save named faces to backend API
      await saveNamedFaces(allAssignments, useMock);
      
      setProcessingStage('complete');
      setProcessingProgress('');
      
      // Show success message
      setTimeout(() => {
        alert(useMock ? '✅ Named faces saved successfully!\n\n🎭 Demo Mode: Names saved locally (not sent to server)' : '✅ Named faces saved successfully to the server!');
      }, 500);
    } catch (error: any) {
      console.error('Error saving named faces:', error);
      setErrorMessage(error.message || 'Failed to save named faces. Please try again.');
      setProcessingStage('error');
      setShowSummary(true); // Go back to summary
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

  // Upload Screen
  if (processingStage === 'upload' || processingStage === 'error') {
    return (
      <div className="min-h-screen w-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-6">
        <div className="max-w-2xl w-full bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20 shadow-2xl">
          <div className="text-center mb-8">
            <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-purple-300 to-pink-300 mb-4">
              Face Naming Wizard
            </h1>
            <p className="text-white/80 text-lg">
              Upload your memories ZIP file to extract and name faces
            </p>
          </div>

          {errorMessage && (
            <div className="mb-6 p-4 bg-red-500/20 border border-red-500/50 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-300 flex-shrink-0 mt-0.5" />
              <p className="text-red-200 text-sm">{errorMessage}</p>
            </div>
          )}

          <div className="space-y-6">
            <div className="border-2 border-dashed border-white/30 rounded-2xl p-12 text-center hover:border-purple-400 transition-all cursor-pointer bg-white/5"
                 onClick={() => fileInputRef.current?.click()}>
              <Upload className="w-16 h-16 mx-auto mb-4 text-purple-300" />
              <p className="text-white text-lg font-semibold mb-2">
                {uploadedFile ? uploadedFile.name : 'Click to upload ZIP file'}
              </p>
              <p className="text-white/60 text-sm">
                ZIP should contain a 'memories' folder with photos/videos
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept=".zip"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>

            <div className="flex gap-4">
              <Button
                onClick={() => handleExtractFaces(false)}
                disabled={!uploadedFile}
                className="flex-1 h-16 text-xl font-bold bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Process Files
              </Button>
              <Button
                onClick={() => handleExtractFaces(true)}
                variant="outline"
                className="h-16 px-8 text-xl font-bold bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white border-0"
              >
                🎭 Mock Demo
              </Button>
            </div>
          </div>

          <div className="mt-8 p-4 bg-white/5 rounded-lg border border-white/10">
            <p className="text-white/70 text-sm">
              <strong className="text-white">How it works:</strong><br />
              1. Upload your memories ZIP file<br />
              2. AI extracts and clusters faces<br />
              3. Name each person<br />
              4. Save names to backend
            </p>
          </div>

          <div className="mt-4 p-4 bg-blue-500/20 border border-blue-500/50 rounded-lg">
            <p className="text-blue-200 text-sm">
              <strong className="text-blue-100">💡 Two Options:</strong><br />
              • <strong>Process Files:</strong> Upload a real ZIP file to extract faces using the API<br />
              • <strong>Mock Demo:</strong> Skip upload and use hardcoded demo data to test the interface
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Extracting/Processing Screen
  if (processingStage === 'extracting' || processingStage === 'generating') {
    return (
      <div className="min-h-screen w-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-6">
        <div className="max-w-2xl w-full bg-white/10 backdrop-blur-lg rounded-3xl p-12 border border-white/20 shadow-2xl text-center">
          <Loader2 className="w-20 h-20 mx-auto mb-6 text-purple-300 animate-spin" />
          <h2 className="text-4xl font-bold text-white mb-4">
            {processingStage === 'extracting' ? 'Extracting Faces...' : 'Saving Names...'}
          </h2>
          <p className="text-white/70 text-lg mb-8">{processingProgress}</p>
          <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
            <div className="h-full bg-gradient-to-r from-purple-500 to-pink-500 animate-pulse" style={{ width: '100%' }}></div>
          </div>
          <p className="text-white/50 text-sm mt-6">This may take a moment...</p>
        </div>
      </div>
    );
  }

  // Complete Screen
  if (processingStage === 'complete') {
    return (
      <div className="min-h-screen w-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-6">
        <div className="max-w-2xl w-full bg-white/10 backdrop-blur-lg rounded-3xl p-12 border border-white/20 shadow-2xl text-center">
          <CheckCircle className="w-24 h-24 mx-auto mb-6 text-green-400" />
          <h2 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-300 to-emerald-300 mb-4">
            All Done! 🎉
          </h2>
          <p className="text-white/80 text-lg mb-8">
            Your named faces have been saved successfully.
          </p>
          <Button
            onClick={() => {
              setProcessingStage('upload');
              setUploadedFile(null);
              setFolders([]);
              setAllAssignments({});
              setCurrentFolderIndex(0);
              setShowSummary(false);
            }}
            className="h-14 px-10 text-lg font-bold bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
          >
            Process Another File
          </Button>
        </div>
      </div>
    );
  }

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
          image: folder.imageUrls[folder.images.indexOf(image)] || `/${folder.path}/${image}`
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
                onClick={() => handleSaveFinal(false)}
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
            onClick={() => setEnlargedBubble(bubble)}
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
          Move your mouse to interact with the bubbles • Click to enlarge
        </p>
      </div>

      {/* Enlarged Bubble Modal */}
      {enlargedBubble && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm animate-in fade-in duration-300"
          onClick={() => setEnlargedBubble(null)}
        >
          <div 
            className="relative animate-in zoom-in-95 duration-500 ease-out"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Animated glow effect */}
            <div className="absolute -inset-8 rounded-full bg-gradient-to-br from-pink-500 via-purple-500 to-indigo-600 opacity-60 blur-3xl animate-pulse"></div>
            
            {/* Main enlarged bubble */}
            <div className="relative w-[400px] h-[400px] animate-in spin-in-180 duration-700 ease-out">
              <div className="absolute inset-0 rounded-full bg-gradient-to-br from-pink-400 via-purple-500 to-indigo-600 opacity-50 blur-2xl animate-pulse"></div>
              <div className="absolute inset-4 rounded-full overflow-hidden border-4 border-white/60 shadow-2xl bg-white/10 backdrop-blur-sm">
                <img
                  src={enlargedBubble.image}
                  alt="Enlarged face"
                  className="w-full h-full object-cover"
                />
              </div>
              {/* Shine effect */}
              <div className="absolute inset-4 rounded-full bg-gradient-to-br from-white/40 via-transparent to-transparent pointer-events-none"></div>
              {/* Sparkle effects */}
              <div className="absolute top-8 right-8 w-3 h-3 bg-white rounded-full animate-ping"></div>
              <div className="absolute bottom-12 left-12 w-2 h-2 bg-white rounded-full animate-pulse delay-150"></div>
              <div className="absolute top-16 left-16 w-2.5 h-2.5 bg-white rounded-full animate-ping delay-300"></div>
            </div>
            
            {/* Close button */}
            <button
              onClick={() => setEnlargedBubble(null)}
              className="absolute -top-4 -right-4 w-12 h-12 rounded-full bg-white/90 hover:bg-white shadow-lg hover:shadow-2xl flex items-center justify-center transition-all duration-300 hover:scale-110 active:scale-95 animate-in zoom-in duration-500 delay-200"
            >
              <svg className="w-6 h-6 text-gray-800" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
            
            {/* Click to close hint */}
            <div className="absolute -bottom-16 left-1/2 transform -translate-x-1/2 text-white/60 text-sm font-medium animate-in fade-in slide-in-from-bottom-4 duration-700 delay-500">
              Click anywhere to close
            </div>
          </div>
        </div>
      )}

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