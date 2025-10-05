"use client";

import * as React from "react";

type Segment = { label: string; value: number; color: string };

export function EmotionBar({ data }: { data: Segment[] }) {
  return (
    <div className="space-y-2">
      <div className="flex h-2 w-full overflow-hidden rounded-full border border-slate-200/70 bg-slate-200 dark:border-slate-700 dark:bg-slate-700">
        {data.map((seg) => (
          <div
            key={seg.label}
            title={`${seg.label} ${seg.value}%`}
            className="h-full"
            style={{ width: `${seg.value}%`, backgroundColor: seg.color }}
          />
        ))}
      </div>
      <div className="flex flex-wrap gap-3">
        {data.map((seg) => (
          <div key={seg.label} className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-300">
            <span
              aria-hidden
              className="inline-block h-2 w-2 rounded"
              style={{ backgroundColor: seg.color }}
            />
            <span>
              {seg.label} {seg.value}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
