"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Heart,
  UserPlus,
  Video,
  Upload,
  ArrowLeft,
} from "lucide-react";
import { MoodRadarChart } from "@/components/mood-radar-chart";
import { ExperiencesList } from "@/components/experiences-list";

type Screen = "dashboard" | "patient-name" | "patient-upload" | "face-naming" | "patient-complete" | "experience-form" | "experience-complete";

interface Face {
  id: string;
  imageUrl: string;
  name: string;
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

export default function DashboardPage() {
  const [currentScreen, setCurrentScreen] = useState<Screen>("dashboard");
  const [patientName, setPatientName] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [faces, setFaces] = useState<Face[]>([]);
  const [selectedPatient, setSelectedPatient] = useState("");
  const [experienceTopic, setExperienceTopic] = useState("");
  const [bulletPoints, setBulletPoints] = useState("");
  const [patients, setPatients] = useState(["John Doe", "Jane Smith", "Robert Johnson"]);
  
  // Bubble animation state
  const [bubbles, setBubbles] = useState<Bubble[]>([]);
  const mousePos = useRef({ x: -1000, y: -1000 });
  const animationFrameId = useRef<number | null>(null);
  const canvasRef = useRef<HTMLDivElement>(null);
  
  // Multi-person face naming state
  const [currentPersonIndex, setCurrentPersonIndex] = useState(0);
  const [allPeople, setAllPeople] = useState<Array<{folder: string, images: string[]}>>([]);
  const [namedPeople, setNamedPeople] = useState<{[folder: string]: string}>({});

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const filesArray = Array.from(e.target.files);
      setUploadedFiles(filesArray);
    }
  };

  const handleUploadComplete = async () => {
    // Load all people folders - hardcoded for demo
    const peopleData = [
      {
        folder: 'person_1',
        images: [
          'face_0005.jpg', 'face_0011.jpg', 'face_0019.jpg', 'face_0031.jpg',
          'face_0044.jpg', 'face_0045.jpg', 'face_0052.jpg', 'face_0070.jpg',
          'face_0072.jpg', 'face_0076.jpg', 'face_0084.jpg', 'face_0088.jpg',
          'face_0089.jpg', 'face_0090.jpg', 'face_0094.jpg', 'face_0096.jpg'
        ]
      },
      {
        folder: 'person_2',
        images: [
          'face_0000.jpg', 'face_0007.jpg', 'face_0020.jpg', 'face_0029.jpg',
          'face_0035.jpg', 'face_0036.jpg', 'face_0038.jpg', 'face_0039.jpg',
          'face_0041.jpg', 'face_0047.jpg', 'face_0050.jpg', 'face_0061.jpg',
          'face_0063.jpg', 'face_0065.jpg', 'face_0080.jpg', 'face_0081.jpg'
        ]
      },
      {
        folder: 'person_3',
        images: [
          'face_0002.jpg', 'face_0006.jpg', 'face_0011.jpg', 'face_0013.jpg',
          'face_0020.jpg', 'face_0041.jpg', 'face_0042.jpg', 'face_0043.jpg',
          'face_0047.jpg', 'face_0048.jpg', 'face_0053.jpg', 'face_0063.jpg',
          'face_0070.jpg', 'face_0072.jpg', 'face_0074.jpg', 'face_0076.jpg'
        ]
      }
    ];
    
    setAllPeople(peopleData);
    setCurrentPersonIndex(0);
    loadPersonFaces(peopleData[0]);
    setCurrentScreen("face-naming");
  };
  
  const loadPersonFaces = (person: {folder: string, images: string[]}) => {
    const loadedFaces: Face[] = person.images.map((img, idx) => ({
      id: `${person.folder}-${idx}`,
      imageUrl: `/people/${person.folder}/${img}`,
      name: ""
    }));
    
    setFaces(loadedFaces);
    
    // Initialize bubbles for animation
    const newBubbles: Bubble[] = loadedFaces.map((face, index) => {
      const angle = (index / loadedFaces.length) * Math.PI * 2;
      const radius = 200;
      const centerX = typeof window !== 'undefined' ? window.innerWidth / 2 : 500;
      const centerY = typeof window !== 'undefined' ? window.innerHeight / 2 : 400;
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;
      
      return {
        id: face.id,
        x,
        y,
        vx: (Math.random() - 0.5) * 2,
        vy: (Math.random() - 0.5) * 2,
        size: 80 + Math.random() * 40,
        image: face.imageUrl,
        name: face.name,
        originalX: x,
        originalY: y,
        currentX: x,
        currentY: y
      };
    });
    setBubbles(newBubbles);
  };

  const handleFaceNameChange = (id: string, name: string) => {
    setFaces(faces.map(face => face.id === id ? { ...face, name } : face));
  };

  const handleFaceNamingComplete = (name: string) => {
    if (!name.trim()) return;
    
    // Save the name for current person
    const currentPerson = allPeople[currentPersonIndex];
    setNamedPeople(prev => ({
      ...prev,
      [currentPerson.folder]: name
    }));
    
    // Move to next person or complete
    if (currentPersonIndex < allPeople.length - 1) {
      const nextIndex = currentPersonIndex + 1;
      setCurrentPersonIndex(nextIndex);
      loadPersonFaces(allPeople[nextIndex]);
    } else {
      // All people named, go to completion
      // Add the new patient to the patients list if not already present
      if (patientName.trim() && !patients.includes(patientName.trim())) {
        setPatients(prev => [...prev, patientName.trim()]);
      }
      setCurrentScreen("patient-complete");
    }
  };

  // Track mouse position
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      mousePos.current = { x: e.clientX, y: e.clientY };
    };
    
    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Bubble physics animation
  useEffect(() => {
    if (bubbles.length === 0 || currentScreen !== "face-naming") return;
    
    const repelRadius = 150;
    const repelRadiusSq = repelRadius * repelRadius;
    
    const animate = () => {
      setBubbles(prev => {
        const mouse = mousePos.current;
        
        return prev.map(bubble => {
          const dx = bubble.currentX - mouse.x;
          const dy = bubble.currentY - mouse.y;
          const distanceSq = dx * dx + dy * dy;
          
          let targetX = bubble.originalX;
          let targetY = bubble.originalY;
          
          if (distanceSq < repelRadiusSq && distanceSq > 0) {
            const distance = Math.sqrt(distanceSq);
            const force = (repelRadius - distance) / repelRadius;
            const pushX = (dx / distance) * force * 80;
            const pushY = (dy / distance) * force * 80;
            targetX = bubble.originalX + pushX;
            targetY = bubble.originalY + pushY;
          }
          
          const diffX = targetX - bubble.currentX;
          const diffY = targetY - bubble.currentY;
          
          if (Math.abs(diffX) < 0.1 && Math.abs(diffY) < 0.1) {
            return bubble;
          }
          
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
  }, [bubbles.length, currentScreen]);

  const handleExperienceSubmit = () => {
    // Create JSON from form data
    const experienceData = {
      patient: selectedPatient,
      topic: experienceTopic,
      details: bulletPoints.split("\n").filter(line => line.trim() !== "")
    };
    console.log("Experience Data:", JSON.stringify(experienceData, null, 2));
    setCurrentScreen("experience-complete");
  };

  const resetToDashboard = () => {
    setCurrentScreen("dashboard");
    setPatientName("");
    setUploadedFiles([]);
    setFaces([]);
    setSelectedPatient("");
    setExperienceTopic("");
    setBulletPoints("");
  };

  return (
    <div className="flex min-h-screen w-full flex-col">
      <header className="sticky top-0 z-50 flex h-16 items-center gap-4 border-b bg-background px-4 md:px-6">
        <div className="flex items-center gap-2">
          <Heart className="h-6 w-6 text-red-500" />
          <span className="font-bold text-lg">Caregiver Dashboard</span>
        </div>
        {currentScreen !== "dashboard" && (
          <Button
            variant="ghost"
            onClick={resetToDashboard}
            className="ml-auto"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
        )}
      </header>

      <main className="flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-8">
        {currentScreen === "dashboard" && (
          <>
            <div className="grid gap-6 md:grid-cols-2 max-w-4xl mx-auto w-full">
              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <UserPlus className="h-5 w-5 text-blue-600" />
                    New Patient
                  </CardTitle>
                  <CardDescription>
                    Add a new patient and set up their profile
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    onClick={() => setCurrentScreen("patient-name")}
                    className="w-full h-14 px-8 text-lg"
                  >
                    <UserPlus className="mr-2 h-5 w-5" />
                    Add New Patient
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Video className="h-5 w-5 text-purple-600" />
                    New Experience
                  </CardTitle>
                  <CardDescription>
                    Create a new memory experience for a patient
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    onClick={() => setCurrentScreen("experience-form")}
                    className="w-full h-14 px-8 text-lg"
                    variant="outline"
                  >
                    <Video className="mr-2 h-5 w-5" />
                    Create Experience
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Mood Analytics Section */}
            <div className="max-w-4xl mx-auto w-full mt-8">
              <MoodRadarChart />
            </div>

            {/* Experiences List Section */}
            <div className="max-w-4xl mx-auto w-full mt-8">
              <ExperiencesList />
            </div>
          </>
        )}

        {currentScreen === "patient-name" && (
          <Card className="max-w-2xl mx-auto w-full">
            <CardHeader>
              <CardTitle>Enter Patient Name</CardTitle>
              <CardDescription>
                Please provide the patient's full name
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="patient-name">Patient Name</Label>
                <Input
                  id="patient-name"
                  placeholder="Enter patient's full name"
                  value={patientName}
                  onChange={(e) => setPatientName(e.target.value)}
                />
              </div>
              <Button
                onClick={() => setCurrentScreen("patient-upload")}
                disabled={!patientName.trim()}
                className="w-full"
              >
                Continue
              </Button>
            </CardContent>
          </Card>
        )}

        {currentScreen === "patient-upload" && (
          <Card className="max-w-2xl mx-auto w-full">
            <CardHeader>
              <CardTitle>Upload Media for {patientName}</CardTitle>
              <CardDescription>
                Upload photos and videos to extract faces
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
                <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <Label htmlFor="file-upload" className="cursor-pointer">
                  <span className="text-blue-600 hover:text-blue-700 font-medium">
                    Click to upload
                  </span>
                  <span className="text-gray-600"> or drag and drop</span>
                </Label>
                <Input
                  id="file-upload"
                  type="file"
                  multiple
                  accept="image/*,video/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <p className="text-sm text-gray-500 mt-2">
                  PNG, JPG, MP4, MOV up to 50MB each
                </p>
              </div>
              {uploadedFiles.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium">
                    {uploadedFiles.length} file(s) selected
                  </p>
                  <div className="max-h-40 overflow-y-auto space-y-1">
                    {uploadedFiles.map((file, index) => (
                      <div key={index} className="text-sm text-gray-600">
                        {file.name}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <Button
                onClick={handleUploadComplete}
                className="w-full"
              >
                Process Files
              </Button>
            </CardContent>
          </Card>
        )}

        {currentScreen === "face-naming" && (
          <div className="fixed inset-0 w-screen h-screen overflow-hidden bg-slate-900">
            {/* Bubbles */}
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
                    transform: 'translateZ(0)'
                  }}
                >
                  <div className="relative w-full h-full group cursor-pointer">
                    <div className="absolute inset-0 rounded-full bg-gradient-to-br from-pink-400 via-purple-500 to-indigo-600 opacity-40 blur-lg group-hover:opacity-80 group-hover:scale-110 transition-all duration-500"></div>
                    <div className="absolute inset-2 rounded-full overflow-hidden border-2 border-white/40 shadow-xl bg-white/5 group-hover:border-white/70 group-hover:scale-105 transition-all duration-300">
                      <img
                        src={bubble.image}
                        alt="Face"
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                        onError={(e) => {
                          e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23ddd" width="100" height="100"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999"%3EFace%3C/text%3E%3C/svg%3E';
                        }}
                      />
                    </div>
                    <div className="absolute inset-2 rounded-full bg-gradient-to-br from-white/30 via-transparent to-transparent pointer-events-none opacity-60 group-hover:opacity-100 transition-opacity duration-300"></div>
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
                  <div className="flex gap-3 items-center">
                    <div className="text-white text-lg font-semibold bg-white/10 backdrop-blur-sm px-6 py-2 rounded-full border border-white/20 animate-in fade-in duration-700">
                      Person {currentPersonIndex + 1} of {allPeople.length}
                    </div>
                    <div className="text-white text-lg font-semibold bg-white/10 backdrop-blur-sm px-6 py-2 rounded-full border border-white/20 animate-in fade-in duration-700">
                      {patientName}
                    </div>
                  </div>
                </div>
                <div className="text-center mb-4 animate-in fade-in slide-in-from-top duration-700 delay-200">
                  <p className="text-xl font-semibold text-white/90 drop-shadow-lg">
                    {faces.length} photo{faces.length !== 1 ? 's' : ''} of this person
                  </p>
                </div>
              </div>
            </div>

            {/* Bottom Controls */}
            <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-slate-900/80 via-slate-900/40 to-transparent z-10">
              <div className="max-w-2xl mx-auto">
                <div className="flex gap-4 items-center justify-center mb-4 animate-in slide-in-from-bottom duration-500">
                  <Input
                    value={faces[0]?.name || ''}
                    onChange={(e) => handleFaceNameChange(faces[0]?.id, e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && faces[0]?.name.trim()) {
                        handleFaceNamingComplete(faces[0].name);
                      }
                    }}
                    placeholder="Type a name..."
                    className="flex-1 h-14 text-lg bg-white/95 backdrop-blur-sm border-2 border-white/30 focus:border-purple-400 text-gray-900 placeholder:text-gray-400 shadow-lg hover:shadow-xl transition-all"
                  />
                  <Button
                    onClick={() => faces[0]?.name.trim() && handleFaceNamingComplete(faces[0].name)}
                    className="h-14 px-8 text-lg font-bold bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg hover:shadow-2xl hover:scale-105 transition-all active:scale-95"
                  >
                    Assign
                  </Button>
                </div>
              </div>
            </div>

            {/* Instructions */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none z-0">
              <p className="text-white/30 text-xl font-bold text-center">
                Move your mouse to interact with the bubbles
              </p>
            </div>
          </div>
        )}

        {currentScreen === "patient-complete" && (
          <Card className="max-w-2xl mx-auto w-full">
            <CardHeader>
              <CardTitle className="text-center text-2xl">Patient Setup Complete!</CardTitle>
              <CardDescription className="text-center">
                {patientName} has been successfully added to the system
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-center py-6">
                <div className="h-20 w-20 rounded-full bg-green-100 flex items-center justify-center">
                  <svg
                    className="h-10 w-10 text-green-600"
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path d="M5 13l4 4L19 7"></path>
                  </svg>
                </div>
              </div>
              <Button onClick={resetToDashboard} className="w-full h-14 px-10 text-lg">
                Return to Dashboard
              </Button>
            </CardContent>
          </Card>
        )}

        {currentScreen === "experience-form" && (
          <Card className="max-w-2xl mx-auto w-full">
            <CardHeader>
              <CardTitle>Create New Experience</CardTitle>
              <CardDescription>
                Set up a new memory experience for a patient
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="patient-select">Select Patient</Label>
                <Select value={selectedPatient} onValueChange={setSelectedPatient}>
                  <SelectTrigger id="patient-select">
                    <SelectValue placeholder="Choose a patient" />
                  </SelectTrigger>
                  <SelectContent>
                    {patients.map((patient) => (
                      <SelectItem key={patient} value={patient}>
                        {patient}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="topic">General Topic</Label>
                <Input
                  id="topic"
                  placeholder="e.g., Family Reunion, Birthday Party"
                  value={experienceTopic}
                  onChange={(e) => setExperienceTopic(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="details">Specific Details</Label>
                <textarea
                  id="details"
                  className="w-full min-h-[200px] px-3 py-2 text-sm rounded-md border border-input bg-background"
                  placeholder="Enter each detail on a new line:\n• Who was there\n• What happened\n• Where it took place\n• Special moments"
                  value={bulletPoints}
                  onChange={(e) => setBulletPoints(e.target.value)}
                />
              </div>

              <Button
                onClick={handleExperienceSubmit}
                disabled={!selectedPatient || !experienceTopic.trim() || !bulletPoints.trim()}
                className="w-full"
              >
                Create Experience
              </Button>
            </CardContent>
          </Card>
        )}

        {currentScreen === "experience-complete" && (
          <Card className="max-w-2xl mx-auto w-full">
            <CardHeader>
              <CardTitle className="text-center text-2xl">Experience Created!</CardTitle>
              <CardDescription className="text-center">
                The new experience has been successfully created
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-center py-6">
                <div className="h-20 w-20 rounded-full bg-purple-100 flex items-center justify-center">
                  <svg
                    className="h-10 w-10 text-purple-600"
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path d="M5 13l4 4L19 7"></path>
                  </svg>
                </div>
              </div>
              <Button onClick={resetToDashboard} className="w-full h-14 px-10 text-lg">
                Return to Dashboard
              </Button>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
