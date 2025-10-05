"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Calendar, User, MapPin, Clock } from "lucide-react"

interface Experience {
  id: string
  patientName: string
  topic: string
  description: string
  date: string
  location?: string
  duration?: string
  mood?: string
}

const mockExperiences: Experience[] = [
  {
    id: "exp-001",
    patientName: "John Doe",
    topic: "Family Reunion at the Beach",
    description: "A wonderful day spent with family members at the beach. John recognized his daughter and grandchildren. He was particularly engaged when looking at old family photos and shared stories about his childhood summers.",
    date: "2024-10-03",
    location: "Santa Monica Beach",
    duration: "45 minutes",
    mood: "Happy & Nostalgic"
  },
  {
    id: "exp-002",
    patientName: "Jane Smith",
    topic: "Birthday Celebration",
    description: "Jane's 80th birthday party with close friends and family. She was delighted to see everyone and actively participated in conversations. Showed strong emotional connection when her favorite music from the 1960s was played.",
    date: "2024-10-02",
    location: "Home",
    duration: "60 minutes",
    mood: "Joyful & Engaged"
  },
  {
    id: "exp-003",
    patientName: "Robert Johnson",
    topic: "Garden Walk and Memories",
    description: "Robert spent time in the garden, reminiscing about his years as a landscape architect. He identified various plants and shared detailed stories about projects he worked on. Very calm and focused throughout the session.",
    date: "2024-10-01",
    location: "Community Garden",
    duration: "30 minutes",
    mood: "Calm & Reflective"
  },
  {
    id: "exp-004",
    patientName: "John Doe",
    topic: "Watching Old Home Videos",
    description: "Reviewed home videos from the 1980s showing John's children growing up. He became emotional but in a positive way, laughing at funny moments and sharing additional context about the events captured on film.",
    date: "2024-09-30",
    location: "Living Room",
    duration: "40 minutes",
    mood: "Nostalgic & Content"
  }
]

export function ExperiencesList() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Memory Experiences</CardTitle>
        <CardDescription>
          Documented memory sessions and their outcomes
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {mockExperiences.map((experience) => (
            <div
              key={experience.id}
              className="border rounded-lg p-4 hover:shadow-md transition-shadow bg-white/50"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg text-slate-800 mb-1">
                    {experience.topic}
                  </h3>
                  <div className="flex items-center gap-2 text-sm text-slate-600 mb-2">
                    <User className="h-4 w-4" />
                    <span>{experience.patientName}</span>
                  </div>
                </div>
                {experience.mood && (
                  <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                    {experience.mood}
                  </span>
                )}
              </div>
              
              <p className="text-slate-700 text-sm leading-relaxed mb-3">
                {experience.description}
              </p>
              
              <div className="flex flex-wrap gap-4 text-xs text-slate-500">
                <div className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5" />
                  <span>{new Date(experience.date).toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric', 
                    year: 'numeric' 
                  })}</span>
                </div>
                {experience.location && (
                  <div className="flex items-center gap-1">
                    <MapPin className="h-3.5 w-3.5" />
                    <span>{experience.location}</span>
                  </div>
                )}
                {experience.duration && (
                  <div className="flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" />
                    <span>{experience.duration}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
