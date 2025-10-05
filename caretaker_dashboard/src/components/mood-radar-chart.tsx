"use client"

import { TrendingUp } from "lucide-react"
import { PolarAngleAxis, PolarGrid, Radar, RadarChart } from "recharts"

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"

const chartData = [
  { emotion: "Happy", value: 85 },
  { emotion: "Calm", value: 70 },
  { emotion: "Engaged", value: 90 },
  { emotion: "Nostalgic", value: 75 },
  { emotion: "Comfortable", value: 80 },
  { emotion: "Alert", value: 65 },
]

const chartConfig = {
  value: {
    label: "Mood Level",
    color: "hsl(var(--chart-1))",
  },
}

export function MoodRadarChart() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Patient Mood During Experiences</CardTitle>
        <CardDescription>
          Emotional state analysis from recent memory sessions
        </CardDescription>
      </CardHeader>
      <CardContent className="pb-0">
        <ChartContainer
          config={chartConfig}
          className="mx-auto aspect-square max-h-[300px]"
        >
          <RadarChart data={chartData}>
            <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
            <PolarAngleAxis dataKey="emotion" />
            <PolarGrid />
            <Radar
              dataKey="value"
              fill="var(--color-value)"
              fillOpacity={0.6}
              dot={{
                r: 4,
                fillOpacity: 1,
              }}
            />
          </RadarChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="flex-col gap-2 text-sm">
        <div className="flex items-center gap-2 font-medium leading-none">
          Positive mood trending up by 12% this week <TrendingUp className="h-4 w-4" />
        </div>
        <div className="flex items-center gap-2 leading-none text-muted-foreground">
          Based on last 7 memory experiences
        </div>
      </CardFooter>
    </Card>
  )
}
