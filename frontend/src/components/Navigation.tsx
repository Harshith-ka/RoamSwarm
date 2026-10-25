"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { MapPin, Cpu, Headset, BarChart3, Radio } from "lucide-react";

export function Navigation() {
  const pathname = usePathname();

  const navItems = [
    { label: "Explore", href: "/", icon: MapPin },
    { label: "Agent Workspace", href: "/workspace", icon: Cpu },
    { label: "Story Experience", href: "/story", icon: Headset },
    { label: "AI Analytics", href: "/analytics", icon: BarChart3 },
  ];

  return (
    <header className="sticky top-0 z-50 w-full glass-panel border-b border-slate-800/80 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
            <Radio className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                RoamSwarm
              </span>
              <span className="px-2 py-0.5 text-[10px] uppercase font-semibold tracking-wider rounded-full bg-cyan-950/80 border border-cyan-500/40 text-cyan-300">
                LangGraph 4-Agent
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">
              Autonomous Urban Intelligence & Storytelling Engine
            </p>
          </div>
        </Link>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 sm:gap-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 px-3 sm:px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-sm shadow-cyan-500/10"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-cyan-400" : "text-slate-400"}`} />
                <span className="hidden md:inline">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Live System Indicator */}
        <div className="hidden lg:flex items-center gap-3 pl-4 border-l border-slate-800">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-slate-700/60 text-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span className="text-slate-300 font-mono text-[11px]">Engine Active</span>
          </div>
        </div>
      </div>
    </header>
  );
}
