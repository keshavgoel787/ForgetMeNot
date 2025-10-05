"use client"

import { useState, useEffect } from "react"
import { TrendingUp } from "lucide-react"
import { Pie, PieChart, Cell, Label } from "recharts"

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

// Data showing which experience topics are being used most
const chartData = [
  { topic: "Family Reunion", count: 8, fill: "hsl(var(--chart-1))" },
  { topic: "Birthday Celebration", count: 6, fill: "hsl(var(--chart-2))" },
  { topic: "Garden Walk", count: 5, fill: "hsl(var(--chart-3))" },
  { topic: "Home Videos", count: 4, fill: "hsl(var(--chart-4))" },
  { topic: "Music Sessions", count: 3, fill: "hsl(var(--chart-5))" },
]

const chartConfig = {
  count: {
    label: "Sessions",
  },
  "Family Reunion": {
    label: "Family Reunion",
    color: "hsl(var(--chart-1))",
  },
  "Birthday Celebration": {
    label: "Birthday Celebration",
    color: "hsl(var(--chart-2))",
  },
  "Garden Walk": {
    label: "Garden Walk",
    color: "hsl(var(--chart-3))",
  },
  "Home Videos": {
    label: "Home Videos",
    color: "hsl(var(--chart-4))",
  },
  "Music Sessions": {
    label: "Music Sessions",
    color: "hsl(var(--chart-5))",
  },
}

export function ExperienceUsagePieChart() {
  const [animatedData, setAnimatedData] = useState(
    chartData.map(item => ({ ...item, count: 0 }))
  )

  useEffect(() => {
    // Animate the pie chart by gradually increasing values
    const timer = setTimeout(() => {
      setAnimatedData(chartData)
    }, 300)

    return () => clearTimeout(timer)
  }, [])

  const totalSessions = chartData.reduce((acc, curr) => acc + curr.count, 0)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Most Used Experience Topics</CardTitle>
        <CardDescription>
          Distribution of memory sessions by topic type
        </CardDescription>
      </CardHeader>
      <CardContent className="pb-0">
        <ChartContainer
          config={chartConfig}
          className="mx-auto aspect-square max-h-[300px]"
        >
          <PieChart>
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel />}
            />
            <Pie
              data={animatedData}
              dataKey="count"
              nameKey="topic"
              innerRadius={60}
              strokeWidth={5}
              animationDuration={800}
              animationBegin={0}
            >
              {animatedData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
              <Label
                content={({ viewBox }) => {
                  if (viewBox && "cx" in viewBox && "cy" in viewBox) {
                    return (
                      <text
                        x={viewBox.cx}
                        y={viewBox.cy}
                        textAnchor="middle"
                        dominantBaseline="middle"
                      >
                        <tspan
                          x={viewBox.cx}
                          y={viewBox.cy}
                          className="fill-foreground text-3xl font-bold"
                        >
                          {totalSessions}
                        </tspan>
                        <tspan
                          x={viewBox.cx}
                          y={(viewBox.cy || 0) + 24}
                          className="fill-white"
                        >
                          Sessions
                        </tspan>
                      </text>
                    )
                  }
                }}
              />
            </Pie>
          </PieChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="flex-col gap-2 text-sm">
        <div className="flex items-center gap-2 font-medium leading-none">
          Family activities trending up by 15% this month <TrendingUp className="h-4 w-4" />
        </div>
        <div className="flex items-center gap-2 leading-none text-muted-foreground">
          Based on last 30 days of memory experiences
        </div>
      </CardFooter>
    </Card>
  )
}
