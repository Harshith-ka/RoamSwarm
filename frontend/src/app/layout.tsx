import type { Metadata } from "next";
import "./globals.css";
import { Navigation } from "@/components/Navigation";

export const metadata: Metadata = {
  title: "RoamSwarm — Autonomous Urban Intelligence Engine",
  description: "Location-aware, 4-agent AI storytelling engine powered by LangGraph, OpenStreetMap, and Wikipedia.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#09172c] text-slate-100 flex flex-col antialiased">
        <Navigation />
        <main className="flex-1 w-full max-w-7xl mx-auto p-4 lg:p-6">
          {children}
        </main>
      </body>
    </html>
  );
}
