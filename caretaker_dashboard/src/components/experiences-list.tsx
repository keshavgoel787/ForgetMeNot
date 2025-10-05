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
    patientName: "Margaret Thompson",
    topic: "Family Reunion at the Beach",
    description: "A wonderful day spent with family members at the beach. Margaret recognized her daughter and grandchildren. She was particularly engaged when looking at old family photos and shared stories about her childhood summers.",
    date: "2024-10-03",
    location: "Santa Monica Beach",
    duration: "45 minutes",
    mood: "Happy & Nostalgic"
  },
  {
    id: "exp-002",
    patientName: "Margaret Thompson",
    topic: "Birthday Celebration",
    description: "Margaret's 80th birthday party with close friends and family. She was delighted to see everyone and actively participated in conversations. Showed strong emotional connection when her favorite music from the 1960s was played.",
    date: "2024-10-02",
    location: "Home",
    duration: "60 minutes",
    mood: "Joyful & Engaged"
  },
  {
    id: "exp-003",
    patientName: "Margaret Thompson",
    topic: "Garden Walk and Memories",
    description: "Margaret spent time in the garden, reminiscing about her years as a landscape architect. She identified various plants and shared detailed stories about projects she worked on. Very calm and focused throughout the session.",
    date: "2024-10-01",
    location: "Community Garden",
    duration: "30 minutes",
    mood: "Calm & Reflective"
  },
  {
    id: "exp-004",
    patientName: "Margaret Thompson",
    topic: "Watching Old Home Videos",
    description: "Reviewed home videos from the 1980s showing Margaret's children growing up. She became emotional but in a positive way, laughing at funny moments and sharing additional context about the events captured on film.",
    date: "2024-09-30",
    location: "Living Room",
    duration: "40 minutes",
    mood: "Nostalgic & Content"
  }
]

export function ExperiencesList() {
  return (
    <Card className="bg-slate-900 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white">Recent Memory Experiences</CardTitle>
        <CardDescription className="text-slate-300">
          Documented memory sessions and their outcomes
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {mockExperiences.map((experience) => (
            <div
              key={experience.id}
              className="border rounded-lg p-4 hover:shadow-md transition-shadow bg-slate-900"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg text-white mb-1">
                    {experience.topic}
                  </h3>
                  <div className="flex items-center gap-2 text-sm text-slate-300 mb-2">
                    <User className="h-4 w-4" />
                    <span>{experience.patientName}</span>
                  </div>
                </div>
                {experience.mood && (
                  <span className="px-3 py-1 bg-purple-600 text-white rounded-full text-xs font-medium">
                    {experience.mood}
                  </span>
                )}
              </div>
              
              <p className="text-slate-200 text-sm leading-relaxed mb-3">
                {experience.description}
              </p>
              
              <div className="flex flex-wrap gap-4 text-xs text-slate-400">
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
