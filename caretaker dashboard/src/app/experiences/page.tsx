"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Link from "next/link";
import {
  Heart,
  Upload,
  Video,
  Users,
  MapPin,
  Calendar,
  Smile,
  Frown,
  Meh,
  Plus,
  X,
  ArrowLeft,
} from "lucide-react";

export default function ExperiencesPage() {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [experienceTitle, setExperienceTitle] = useState("");
  const [selectedResident, setSelectedResident] = useState("");
  const [topics, setTopics] = useState<{ type: string; value: string }[]>([]);
  const [newTopicType, setNewTopicType] = useState("person");
  const [newTopicValue, setNewTopicValue] = useState("");

  const mockResidents = [
    "Margaret Thompson",
    "Robert Chen",
    "Elizabeth Davis",
    "James Wilson",
  ];

  const addTopic = () => {
    if (newTopicValue.trim()) {
      setTopics([...topics, { type: newTopicType, value: newTopicValue }]);
      setNewTopicValue("");
    }
  };

  const removeTopic = (index: number) => {
    setTopics(topics.filter((_, i) => i !== index));
  };

  return (
    <div className="flex min-h-screen w-full flex-col">
      <header className="sticky top-0 z-50 flex h-16 items-center gap-4 border-b bg-background px-4 md:px-6">
        <nav className="flex items-center gap-4">
          <Link href="/" className="flex items-center gap-2">
            <ArrowLeft className="h-5 w-5" />
            <span className="font-semibold">Back to Dashboard</span>
          </Link>
        </nav>
      </header>

      <main className="flex flex-1 flex-col gap-6 p-4 md:gap-8 md:p-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Create Experience</h1>
            <p className="text-muted-foreground">
              Upload videos and create custom experiences for residents
            </p>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Video Upload Section */}
          <Card>
            <CardHeader>
              <CardTitle>Upload Video</CardTitle>
              <CardDescription>
                Upload a video experience for emotion analysis and face recognition
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="resident">Select Resident</Label>
                <select
                  id="resident"
                  value={selectedResident}
                  onChange={(e) => setSelectedResident(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="">Choose a resident...</option>
                  {mockResidents.map((resident) => (
                    <option key={resident} value={resident}>
                      {resident}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="title">Experience Title</Label>
                <Input
                  id="title"
                  placeholder="e.g., Morning Walk in the Garden"
                  value={experienceTitle}
                  onChange={(e) => setExperienceTitle(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="video">Video File</Label>
                <div className="flex items-center gap-2">
                  <Input
                    id="video"
                    type="file"
                    accept="video/*"
                    onChange={(e) => setVideoFile(e.target.files?.[0] || null)}
                    className="cursor-pointer"
                  />
                </div>
                {videoFile && (
                  <p className="text-sm text-muted-foreground">
                    Selected: {videoFile.name}
                  </p>
                )}
              </div>

              <div className="rounded-lg border-2 border-dashed border-muted-foreground/25 p-8 text-center">
                <Upload className="mx-auto h-12 w-12 text-muted-foreground/50" />
                <p className="mt-2 text-sm text-muted-foreground">
                  Drop video file here or click to browse
                </p>
                <p className="text-xs text-muted-foreground">
                  Supports MP4, MOV, AVI (max 500MB)
                </p>
              </div>

              <Button className="w-full h-11">
                <Video className="mr-2 h-4 w-4" />
                Upload & Analyze
              </Button>
            </CardContent>
          </Card>

          {/* Custom Experience Builder */}
          <Card>
            <CardHeader>
              <CardTitle>Custom Experience Builder</CardTitle>
              <CardDescription>
                Create custom experiences with specific topics and memories
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Add Topic Elements</Label>
                <div className="flex gap-2">
                  <select
                    value={newTopicType}
                    onChange={(e) => setNewTopicType(e.target.value)}
                    className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  >
                    <option value="person">Person</option>
                    <option value="memory">Memory</option>
                    <option value="location">Location</option>
                    <option value="event">Event</option>
                  </select>
                  <Input
                    placeholder="Enter topic..."
                    value={newTopicValue}
                    onChange={(e) => setNewTopicValue(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && addTopic()}
                  />
                  <Button onClick={addTopic} className="h-10 w-10 p-0">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Topics ({topics.length})</Label>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {topics.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-4">
                      No topics added yet
                    </p>
                  ) : (
                    topics.map((topic, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between rounded-lg border p-3"
                      >
                        <div className="flex items-center gap-2">
                          {topic.type === "person" && <Users className="h-4 w-4 text-blue-500" />}
                          {topic.type === "memory" && <Heart className="h-4 w-4 text-pink-500" />}
                          {topic.type === "location" && <MapPin className="h-4 w-4 text-green-500" />}
                          {topic.type === "event" && <Calendar className="h-4 w-4 text-purple-500" />}
                          <div>
                            <p className="text-sm font-medium">{topic.value}</p>
                            <p className="text-xs text-muted-foreground capitalize">
                              {topic.type}
                            </p>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          className="h-8 w-8 p-0"
                          onClick={() => removeTopic(index)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ))
                  )}
                </div>
              </div>

              <Button className="w-full h-11" variant="outline">
                <Plus className="mr-2 h-4 w-4" />
                Create Custom Experience
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Emotion Analysis Preview */}
        <Card>
          <CardHeader>
            <CardTitle>Emotion Analysis Preview</CardTitle>
            <CardDescription>
              Real-time emotion detection results will appear here after upload
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="flex items-center gap-4 rounded-lg border p-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900">
                  <Smile className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold">45%</p>
                  <p className="text-sm text-muted-foreground">Happy</p>
                </div>
              </div>

              <div className="flex items-center gap-4 rounded-lg border p-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900">
                  <Meh className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold">35%</p>
                  <p className="text-sm text-muted-foreground">Calm</p>
                </div>
              </div>

              <div className="flex items-center gap-4 rounded-lg border p-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-orange-100 dark:bg-orange-900">
                  <Frown className="h-6 w-6 text-orange-600 dark:text-orange-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold">20%</p>
                  <p className="text-sm text-muted-foreground">Neutral</p>
                </div>
              </div>
            </div>

            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <Label>Emotion Timeline</Label>
                <span className="text-xs text-muted-foreground">0:00 - 2:45</span>
              </div>
              <div className="h-24 rounded-lg border bg-muted/50 flex items-center justify-center">
                <p className="text-sm text-muted-foreground">
                  Timeline visualization will appear after video analysis
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex gap-4 justify-end">
          <Button variant="outline" className="h-11 px-8">
            Save as Draft
          </Button>
          <Link href="/face-naming">
            <Button className="h-11 px-8">
              <Users className="mr-2 h-4 w-4" />
              Continue to Face Naming
            </Button>
          </Link>
        </div>
      </main>
    </div>
  );
}
