"use client";

import * as React from "react";

export type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "default" | "outline" | "ghost";
};

export function Button({ className = "", variant = "primary", ...props }: ButtonProps) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-full text-sm font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-slate-300/60 dark:focus:ring-slate-700/60 disabled:opacity-50 disabled:pointer-events-none h-10 px-5 py-2 shadow-md";
  const variants: Record<string, string> = {
    primary:
      "text-white bg-orange-500 hover:bg-orange-600 dark:bg-orange-500 dark:hover:bg-orange-600",
    default:
      "bg-slate-100 text-slate-800 border border-slate-200 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-100 dark:border-slate-700 dark:hover:bg-slate-700",
    outline:
      "border border-slate-300 text-slate-800 bg-transparent hover:bg-slate-100 dark:border-slate-600 dark:text-slate-100 dark:hover:bg-slate-800",
    ghost: "text-slate-800 hover:bg-slate-100 dark:text-slate-100 dark:hover:bg-slate-800",
  };
  return <button className={`${base} ${variants[variant]} ${className}`} {...props} />;
}
