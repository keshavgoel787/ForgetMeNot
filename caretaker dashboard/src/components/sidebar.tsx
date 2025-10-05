"use client";

import * as React from "react";
import Link from "next/link";

const navItems = [
  { href: "/", label: "Dashboard" },
  { href: "#users", label: "Users" },
  { href: "#analytics", label: "Analytics" },
];

export default function Sidebar() {
  // User-provided gradient presets
  const gradients = [
    // Gentle sky gradient — bright and airy (#4DA6FF → #AEE6FF)
    "bg-gradient-to-r from-[#4DA6FF] to-[#AEE6FF]",
    // Dreamy dusk gradient — a bit moodier and balanced (#4DA6FF → #7B68EE)
    "bg-gradient-to-r from-[#4DA6FF] to-[#7B68EE]",
    // Pastel serenity — softer, calm tones (#4DA6FF → #B3CFFF)
    "bg-gradient-to-r from-[#4DA6FF] to-[#B3CFFF]",
    // Natural garden contrast — inspired by forget-me-nots and yellow centers (#4DA6FF → #FFD54F)
    "bg-gradient-to-r from-[#4DA6FF] to-[#FFD54F]",
  ];

  return (
    <aside className="hidden md:flex md:w-64 lg:w-72 xl:w-80 shrink-0 h-screen sticky top-0 border-r border-slate-200/70 bg-slate-50 dark:bg-slate-900 dark:border-slate-800 shadow-sm">
      <div className="flex flex-col w-full h-full">
        <div className="p-4">
          <div className="text-lg font-extrabold text-slate-800 dark:text-slate-100">Caregiver</div>
          <div className="text-xs text-slate-500 dark:text-slate-400">Dashboard</div>
        </div>
        <nav className="flex-1 p-2">
          <ul className="space-y-2">
            {navItems.map((item, idx) => {
              const gradient = gradients[idx % gradients.length];
              const isDusk = idx % gradients.length === 1; // Dreamy dusk is darker on the right
              const textClass = isDusk ? "text-white" : "text-slate-900";
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={`flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-semibold ${textClass} ${gradient} shadow-sm hover:shadow-md transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-300/60`}
                  >
                    <span className="drop-shadow-[0_1px_0_rgba(255,255,255,0.5)] dark:drop-shadow-none">{item.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
        <div className="p-4 text-xs text-slate-500 dark:text-slate-400">v0.1.0</div>
      </div>
    </aside>
  );
}
