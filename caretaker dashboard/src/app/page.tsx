"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { EmotionBar } from "@/components/emotion-bar";
import Link from "next/link";
import {
  Activity,
  Users,
  Video,
  TrendingUp,
  Calendar,
  Heart,
  Brain,
  Smile,
} from "lucide-react";

const emotionData = [
  { label: "Happy", value: 45, color: "#FFD700" },
  { label: "Calm", value: 30, color: "#87CEEB" },
  { label: "Excited", value: 15, color: "#FF6347" },
  { label: "Neutral", value: 10, color: "#D3D3D3" },
];

export default function DashboardPage() {

  return (
    <>
      <div className="flex min-h-screen w-full flex-col">
        <header className="sticky top-0 z-50 flex h-16 items-center gap-4 border-b bg-background px-4 md:px-6">
          <nav className="hidden flex-col gap-6 text-lg font-medium md:flex md:flex-row md:items-center md:gap-5 md:text-sm lg:gap-6">
            <Link
              href="/"
              className="flex items-center gap-2 text-lg font-semibold md:text-base"
            >
              <Heart className="h-6 w-6 text-red-500" />
              <span className="font-bold">Caregiver Dashboard</span>
            </Link>
            <Link
              href="/"
              className="text-foreground transition-colors hover:text-foreground"
            >
              Dashboard
            </Link>
            <Link
              href="/experiences"
              className="text-muted-foreground transition-colors hover:text-foreground"
            >
              Experiences
            </Link>
            <Link
              href="/memory-test"
              className="text-muted-foreground transition-colors hover:text-foreground"
            >
              Memory Tests
            </Link>
            <Link
              href="/face-naming"
              className="text-muted-foreground transition-colors hover:text-foreground"
            >
              Face Naming
            </Link>
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <Link href="/experiences">
              <Button variant="outline">
                <Video className="mr-2 h-4 w-4" />
                New Experience
              </Button>
            </Link>
            <Link href="/memory-test">
              <Button>
                <Brain className="mr-2 h-4 w-4" />
                Memory Test
              </Button>
            </Link>
          </div>
        </header>

        <main className="flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-8">
          <div className="grid gap-4 md:grid-cols-2 md:gap-8 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Total Patients
                </CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">24</div>
                <p className="text-xs text-muted-foreground">
                  <span className="text-green-600">+2</span> from last month
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Active Sessions
                </CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">12</div>
                <p className="text-xs text-muted-foreground">
                  <span className="text-green-600">+18%</span> from last week
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Engagement Rate
                </CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">87%</div>
                <p className="text-xs text-muted-foreground">
                  <span className="text-green-600">+5%</span> improvement
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Weekly Activities
                </CardTitle>
                <Calendar className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">156</div>
                <p className="text-xs text-muted-foreground">
                  <span className="text-green-600">+12%</span> this week
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:gap-8 lg:grid-cols-2 xl:grid-cols-3">
            <Card className="xl:col-span-2">
              <CardHeader className="flex flex-row items-center">
                <div className="grid gap-2">
                  <CardTitle>Emotional Well-being Overview</CardTitle>
                  <CardDescription>
                    Aggregated emotional states across all residents this week
                  </CardDescription>
                </div>
              </CardHeader>
              <CardContent>
                <EmotionBar data={emotionData} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Activities</CardTitle>
                <CardDescription>
                  Latest recorded experiences and sessions
                </CardDescription>
              </CardHeader>
              <CardContent className="grid gap-4">
                <div className="flex items-center gap-4">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900">
                    <Smile className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div className="grid gap-1">
                    <p className="text-sm font-medium leading-none">
                      Morning Walk Session
                    </p>
                    <p className="text-sm text-muted-foreground">
                      2 hours ago
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-purple-100 dark:bg-purple-900">
                    <Brain className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div className="grid gap-1">
                    <p className="text-sm font-medium leading-none">
                      Memory Care Activity
                    </p>
                    <p className="text-sm text-muted-foreground">
                      5 hours ago
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-green-100 dark:bg-green-900">
                    <Heart className="h-5 w-5 text-green-600 dark:text-green-400" />
                  </div>
                  <div className="grid gap-1">
                    <p className="text-sm font-medium leading-none">
                      Family Video Call
                    </p>
                    <p className="text-sm text-muted-foreground">
                      1 day ago
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:gap-8 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>
                  Common tasks and workflows
                </CardDescription>
              </CardHeader>
              <CardContent className="grid gap-2">
                <Link href="/experiences">
                  <Button
                    variant="outline"
                    className="justify-start w-full"
                  >
                    <Video className="mr-2 h-4 w-4" />
                    Create New Experience
                  </Button>
                </Link>
                <Link href="/memory-test">
                  <Button
                    variant="outline"
                    className="justify-start w-full"
                  >
                    <Brain className="mr-2 h-4 w-4" />
                    Start Memory Assessment
                  </Button>
                </Link>
                <Link href="/face-naming">
                  <Button
                    variant="outline"
                    className="justify-start w-full"
                  >
                    <Users className="mr-2 h-4 w-4" />
                    Manage Face Recognition
                  </Button>
                </Link>
                <Button
                  variant="outline"
                  className="justify-start"
                >
                  <Activity className="mr-2 h-4 w-4" />
                  View Analytics Dashboard
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>System Status</CardTitle>
                <CardDescription>
                  Current system health and notifications
                </CardDescription>
              </CardHeader>
              <CardContent className="grid gap-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-green-500" />
                    <span className="text-sm">Face Recognition</span>
                  </div>
                  <span className="text-sm text-muted-foreground">Active</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-green-500" />
                    <span className="text-sm">Emotion Analysis</span>
                  </div>
                  <span className="text-sm text-muted-foreground">Active</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-yellow-500" />
                    <span className="text-sm">Storage</span>
                  </div>
                  <span className="text-sm text-muted-foreground">75% used</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </>
  );
}
