'use client';

import { Nunito } from "next/font/google";
import { usePathname } from 'next/navigation';
import "./globals.css";

const nunito = Nunito({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["400", "600", "700", "800"],
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  const isFaceNamingPage = pathname === '/face-naming';

  return (
    <html lang="en" className="dark">
      <body
        suppressHydrationWarning
        className={`${nunito.variable} antialiased font-sans`}
      >
        <div className="min-h-screen w-full">
            {isFaceNamingPage ? (
              children
            ) : (
              <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-6">
                {children}
              </div>
            )}
        </div>
      </body>
    </html>
  );
}
