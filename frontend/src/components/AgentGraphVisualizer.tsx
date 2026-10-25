"use client";

import { useEffect, useState } from "react";
import { Cpu, BookOpen, Clock, PenTool, Volume2, CheckCircle2, AlertTriangle, ArrowRight, Activity, Terminal } from "lucide-react";
import { ToolExecutionTrace } from "@/lib/types";

interface AgentGraphVisualizerProps {
  currentStatus: string;
  toolCalls: ToolExecutionTrace[];
  timeline: Array<{ event: string; agent: string; timestamp: number; detail: string }>;
  isStreaming?: boolean;
}

export function AgentGraphVisualizer({
  currentStatus,
  toolCalls,
  timeline,
  isStreaming = false
}: AgentGraphVisualizerProps) {
  const [selectedTool, setSelectedTool] = useState<ToolExecutionTrace | null>(null);

  // Derive agent active states
  const isOrchestratorActive = currentStatus === "pending" || currentStatus === "validating";
  const isHistorianActive = currentStatus === "researching";
  const isScoutActive = currentStatus === "researching";
  const isStorytellerActive = currentStatus === "writing";
  const isAudioActive = currentStatus === "generating_audio";
  const isCompleted = currentStatus === "completed" || currentStatus === "partial";

  const agents = [
    {
      id: "orchestrator",
      name: "Orchestrator Agent",
      role: "Planning & Convergence Validation",
      icon: Cpu,
      color: "from-purple-500 to-indigo-600",
      border: "border-purple-500/40",
      glow: "shadow-purple-500/20",
      isActive: isOrchestratorActive,
      isDone: isStorytellerActive || isAudioActive || isCompleted,
    },
    {
      id: "historian",
      name: "Historian Agent",
      role: "Wikipedia, Wikidata & Lore Grounding",
      icon: BookOpen,
      color: "from-emerald-500 to-teal-600",
      border: "border-emerald-500/40",
      glow: "shadow-emerald-500/20",
      isActive: isHistorianActive,
      isDone: isStorytellerActive || isAudioActive || isCompleted,
    },
    {
      id: "live_scout",
      name: "Live Scout Agent",
      role: "OSM Venue Tags & Freshness Verification",
      icon: Clock,
      color: "from-amber-500 to-orange-600",
      border: "border-amber-500/40",
      glow: "shadow-amber-500/20",
      isActive: isScoutActive,
      isDone: isStorytellerActive || isAudioActive || isCompleted,
    },
    {
      id: "storyteller",
      name: "Storyteller Agent",
      role: "Evidence Synthesis & Claim Attribution",
      icon: PenTool,
      color: "from-pink-500 to-rose-600",
      border: "border-pink-500/40",
      glow: "shadow-pink-500/20",
      isActive: isStorytellerActive,
      isDone: isAudioActive || isCompleted,
    },
    {
      id: "tts",
      name: "Speech Synthesizer",
      role: "Gemini TTS / Waveform Audio Synthesis",
      icon: Volume2,
      color: "from-cyan-500 to-blue-600",
      border: "border-cyan-500/40",
      glow: "shadow-cyan-500/20",
      isActive: isAudioActive,
      isDone: isCompleted,
    }
  ];

  return (
    <div className="space-y-6">
      {/* Visual LangGraph Pipeline Topology */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex items-center justify-between mb-6 pb-3 border-b border-slate-800">
          <div>
            <h3 className="font-bold text-base text-slate-100 flex items-center gap-2">
              <Activity className="w-5 h-5 text-cyan-400" />
              LangGraph Stateful Orchestration Topology
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Observable state transitions, parallel research branches, and evidence convergence
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono uppercase px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700">
              Status: <span className="text-cyan-400 font-semibold">{currentStatus}</span>
            </span>
            {isStreaming && (
              <span className="flex items-center gap-1.5 text-xs text-emerald-400 px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-800/40 font-mono">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                SSE Stream Live
              </span>
            )}
          </div>
        </div>

        {/* Node Cards in Flow */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 relative">
          {agents.map((agent, index) => {
            const Icon = agent.icon;
            return (
              <div
                key={agent.id}
                className={`relative flex flex-col p-4 rounded-xl border transition-all ${
                  agent.isActive
                    ? `bg-slate-900 ${agent.border} shadow-lg ${agent.glow} ring-2 ring-cyan-400/30`
                    : agent.isDone
                    ? "bg-slate-900/60 border-slate-700/80"
                    : "bg-slate-950/40 border-slate-800/60 opacity-60"
                }`}
              >
                {/* Active Ring Animation */}
                {agent.isActive && (
                  <span className="absolute -top-1.5 -right-1.5 flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
                  </span>
                )}

                <div className="flex items-center justify-between mb-3">
                  <div className={`w-9 h-9 rounded-lg bg-gradient-to-tr ${agent.color} flex items-center justify-center text-white shadow-md`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  {agent.isDone ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : agent.isActive ? (
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 animate-pulse">
                      ACTIVE
                    </span>
                  ) : (
                    <span className="text-[10px] font-mono text-slate-500">IDLE</span>
                  )}
                </div>

                <h4 className="font-semibold text-xs text-slate-100">{agent.name}</h4>
                <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                  {agent.role}
                </p>

                {/* Branch Indicators */}
                {index === 1 && (
                  <span className="mt-3 text-[9px] font-mono text-cyan-400 bg-cyan-950/80 px-1.5 py-0.5 rounded border border-cyan-800/40 w-fit">
                    Parallel Branch A
                  </span>
                )}
                {index === 2 && (
                  <span className="mt-3 text-[9px] font-mono text-amber-400 bg-amber-950/80 px-1.5 py-0.5 rounded border border-amber-800/40 w-fit">
                    Parallel Branch B
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Observability Columns: Tool Calls & Live Execution Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tool Execution Logs */}
        <div className="glass-panel rounded-2xl p-5 border border-slate-800">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
            <h4 className="font-semibold text-sm text-slate-200 flex items-center gap-2">
              <Terminal className="w-4 h-4 text-purple-400" />
              Grounded Tool Invocations ({toolCalls.length})
            </h4>
            <span className="text-[11px] text-slate-400 font-mono">Sanitized I/O Audit</span>
          </div>

          <div className="space-y-2.5 max-h-[340px] overflow-y-auto pr-1">
            {toolCalls.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">
                No tool calls executed yet. Awaiting agent activation...
              </div>
            ) : (
              toolCalls.map((tc, idx) => (
                <div
                  key={idx}
                  onClick={() => setSelectedTool(tc)}
                  className={`p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                    selectedTool === tc
                      ? "bg-slate-800/90 border-cyan-500/50"
                      : "bg-slate-900/60 border-slate-800 hover:border-slate-700"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-mono text-cyan-400 font-semibold truncate max-w-[180px]">
                      {tc.tool_name}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-[10px] text-slate-400">
                        {tc.duration_ms} ms
                      </span>
                      <span className={`px-1.5 py-0.2 rounded text-[9px] uppercase font-semibold ${
                        tc.success ? "bg-emerald-950 text-emerald-400 border border-emerald-800" : "bg-red-950 text-red-400"
                      }`}>
                        {tc.success ? "200 OK" : "ERR"}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span>Invoked by: <strong className="text-slate-300">{tc.agent_name}</strong></span>
                    <span className="text-[10px] text-slate-500">{tc.timestamp}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Live SSE Event Stream Timeline */}
        <div className="glass-panel rounded-2xl p-5 border border-slate-800">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
            <h4 className="font-semibold text-sm text-slate-200 flex items-center gap-2">
              <Clock className="w-4 h-4 text-emerald-400" />
              Execution Trace & Convergence Log
            </h4>
            <span className="text-[11px] text-slate-400 font-mono">LangGraph Checkpoints</span>
          </div>

          <div className="space-y-3 max-h-[340px] overflow-y-auto pr-1">
            {timeline.length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">
                Awaiting workflow initialization...
              </div>
            ) : (
              timeline.map((ev, idx) => (
                <div key={idx} className="flex gap-3 text-xs">
                  <div className="flex flex-col items-center">
                    <div className="w-2 h-2 rounded-full bg-cyan-400 mt-1" />
                    {idx < timeline.length - 1 && <div className="w-0.5 flex-1 bg-slate-800 my-1" />}
                  </div>
                  <div className="flex-1 pb-2">
                    <div className="flex items-center justify-between mb-0.5">
                      <span className="font-semibold text-slate-300 font-mono text-[11px]">
                        [{ev.agent}] {ev.event}
                      </span>
                      <span className="text-[10px] font-mono text-slate-500">
                        {new Date(ev.timestamp * 1000).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-slate-400 leading-relaxed text-[11px]">
                      {ev.detail}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Selected Tool I/O Modal / Drawer */}
      {selectedTool && (
        <div className="glass-panel rounded-2xl p-5 border border-cyan-500/30">
          <div className="flex items-center justify-between mb-3">
            <h5 className="font-mono text-xs text-cyan-300 font-bold flex items-center gap-2">
              <Terminal className="w-4 h-4" />
              Inspector: {selectedTool.tool_name} ({selectedTool.agent_name})
            </h5>
            <button
              onClick={() => setSelectedTool(null)}
              className="text-slate-400 hover:text-white text-xs px-2 py-0.5 rounded bg-slate-800"
            >
              Close
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <span className="text-[10px] uppercase font-mono text-slate-400 mb-1 block">Sanitized Input</span>
              <pre className="p-3 rounded-lg bg-slate-950 font-mono text-[11px] text-slate-300 overflow-x-auto border border-slate-800">
                {JSON.stringify(selectedTool.sanitized_input, null, 2)}
              </pre>
            </div>
            <div>
              <span className="text-[10px] uppercase font-mono text-slate-400 mb-1 block">Sanitized Output</span>
              <pre className="p-3 rounded-lg bg-slate-950 font-mono text-[11px] text-slate-300 overflow-x-auto border border-slate-800">
                {JSON.stringify(selectedTool.sanitized_output, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
