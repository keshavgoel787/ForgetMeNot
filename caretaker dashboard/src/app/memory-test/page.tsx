"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  Users,
  MapPin,
  Calendar,
  Brain,
  Play,
  RotateCcw,
} from "lucide-react";

interface TestQuestion {
  id: number;
  event: string;
  image: string;
  correctLocation: string;
  correctPeople: string[];
  options: {
    locations: string[];
    people: string[];
  };
}

export default function MemoryTestPage() {
  const [selectedResident, setSelectedResident] = useState("");
  const [testStarted, setTestStarted] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedLocation, setSelectedLocation] = useState("");
  const [selectedPeople, setSelectedPeople] = useState<string[]>([]);
  const [results, setResults] = useState<{ correct: boolean; question: number }[]>([]);

  const mockResidents = [
    "Margaret Thompson",
    "Robert Chen",
    "Elizabeth Davis",
    "James Wilson",
  ];

  const mockQuestions: TestQuestion[] = [
    {
      id: 1,
      event: "Birthday Party",
      image: "/placeholder-event.jpg",
      correctLocation: "Community Room",
      correctPeople: ["Sarah", "John", "Emily"],
      options: {
        locations: ["Community Room", "Garden", "Dining Hall", "Library"],
        people: ["Sarah", "John", "Emily", "Michael", "Lisa", "David"],
      },
    },
    {
      id: 2,
      event: "Garden Walk",
      image: "/placeholder-event.jpg",
      correctLocation: "Garden",
      correctPeople: ["Nurse Mary", "Dr. Smith"],
      options: {
        locations: ["Garden", "Park", "Courtyard", "Greenhouse"],
        people: ["Nurse Mary", "Dr. Smith", "Therapist Jane", "Volunteer Tom"],
      },
    },
  ];

  const handleSubmitAnswer = () => {
    const question = mockQuestions[currentQuestion];
    const locationCorrect = selectedLocation === question.correctLocation;
    const peopleCorrect =
      selectedPeople.length === question.correctPeople.length &&
      selectedPeople.every((p) => question.correctPeople.includes(p));

    const isCorrect = locationCorrect && peopleCorrect;
    setResults([...results, { correct: isCorrect, question: currentQuestion }]);

    if (currentQuestion < mockQuestions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedLocation("");
      setSelectedPeople([]);
    }
  };

  const togglePerson = (person: string) => {
    if (selectedPeople.includes(person)) {
      setSelectedPeople(selectedPeople.filter((p) => p !== person));
    } else {
      setSelectedPeople([...selectedPeople, person]);
    }
  };

  const resetTest = () => {
    setTestStarted(false);
    setCurrentQuestion(0);
    setSelectedLocation("");
    setSelectedPeople([]);
    setResults([]);
  };

  const showResults = results.length === mockQuestions.length;
  const score = results.filter((r) => r.correct).length;

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
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              <Brain className="h-8 w-8 text-purple-500" />
              Memory Assessment Test
            </h1>
            <p className="text-muted-foreground">
              Test resident memory recall for events, locations, and people
            </p>
          </div>
        </div>

        {!testStarted ? (
          <div className="max-w-2xl mx-auto w-full">
            <Card>
              <CardHeader>
                <CardTitle>Start Memory Test</CardTitle>
                <CardDescription>
                  Select a resident and begin the memory assessment
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Select Resident</label>
                  <select
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

                <div className="rounded-lg border bg-muted/50 p-6 space-y-4">
                  <h3 className="font-semibold">Test Instructions</h3>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 mt-0.5 text-green-500" />
                      <span>Resident will be shown images from past events</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 mt-0.5 text-green-500" />
                      <span>They must recall the location and people present</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 mt-0.5 text-green-500" />
                      <span>Results will help track memory retention over time</span>
                    </li>
                  </ul>
                </div>

                <Button
                  className="w-full h-11"
                  disabled={!selectedResident}
                  onClick={() => setTestStarted(true)}
                >
                  <Play className="mr-2 h-4 w-4" />
                  Start Test
                </Button>
              </CardContent>
            </Card>
          </div>
        ) : showResults ? (
          <div className="max-w-2xl mx-auto w-full">
            <Card>
              <CardHeader>
                <CardTitle>Test Results</CardTitle>
                <CardDescription>
                  Memory assessment completed for {selectedResident}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="text-center py-8">
                  <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-primary/10 mb-4">
                    <span className="text-4xl font-bold text-primary">
                      {score}/{mockQuestions.length}
                    </span>
                  </div>
                  <h3 className="text-2xl font-bold mb-2">
                    {score === mockQuestions.length
                      ? "Perfect Score!"
                      : score >= mockQuestions.length / 2
                      ? "Good Performance"
                      : "Needs Support"}
                  </h3>
                  <p className="text-muted-foreground">
                    {Math.round((score / mockQuestions.length) * 100)}% accuracy
                  </p>
                </div>

                <div className="space-y-3">
                  {results.map((result, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between rounded-lg border p-4"
                    >
                      <div className="flex items-center gap-3">
                        {result.correct ? (
                          <CheckCircle2 className="h-5 w-5 text-green-500" />
                        ) : (
                          <XCircle className="h-5 w-5 text-red-500" />
                        )}
                        <div>
                          <p className="font-medium">
                            Question {index + 1}: {mockQuestions[index].event}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {result.correct ? "Correct" : "Incorrect"}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="flex gap-3">
                  <Button variant="outline" className="flex-1" onClick={resetTest}>
                    <RotateCcw className="mr-2 h-4 w-4" />
                    New Test
                  </Button>
                  <Link href="/" className="flex-1">
                    <Button className="w-full">Return to Dashboard</Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto w-full">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>
                      Question {currentQuestion + 1} of {mockQuestions.length}
                    </CardTitle>
                    <CardDescription>
                      {mockQuestions[currentQuestion].event}
                    </CardDescription>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {selectedResident}
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Event Image */}
                <div className="aspect-video rounded-lg border bg-muted flex items-center justify-center">
                  <Calendar className="h-16 w-16 text-muted-foreground/50" />
                </div>

                {/* Location Selection */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <MapPin className="h-5 w-5 text-green-500" />
                    <label className="text-sm font-medium">
                      Where did this event take place?
                    </label>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    {mockQuestions[currentQuestion].options.locations.map((location) => (
                      <Button
                        key={location}
                        variant={selectedLocation === location ? "default" : "outline"}
                        className="justify-start"
                        onClick={() => setSelectedLocation(location)}
                      >
                        {location}
                      </Button>
                    ))}
                  </div>
                </div>

                {/* People Selection */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Users className="h-5 w-5 text-blue-500" />
                    <label className="text-sm font-medium">
                      Who was there? (Select all that apply)
                    </label>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    {mockQuestions[currentQuestion].options.people.map((person) => (
                      <Button
                        key={person}
                        variant={selectedPeople.includes(person) ? "default" : "outline"}
                        className="justify-start"
                        onClick={() => togglePerson(person)}
                      >
                        {person}
                      </Button>
                    ))}
                  </div>
                </div>

                <Button
                  className="w-full h-11"
                  disabled={!selectedLocation || selectedPeople.length === 0}
                  onClick={handleSubmitAnswer}
                >
                  Submit Answer
                </Button>
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}
