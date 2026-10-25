"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Cpu, Headset, ArrowRight, RotateCw, CheckCircle2, AlertCircle, PlayCircle, Layers } from "lucide-react";
import { AgentGraphVisualizer } from "@/components/AgentGraphVisualizer";
import { subscribeToExplorationEvents, getExplorationSession, startExploration } from "@/lib/api";
import { ToolExecutionTrace } from "@/lib/types";

function WorkspaceContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = searchParams.get("session_id");

  const [status, setStatus] = useState<string>("pending");
  const [landmarkName, setLandmarkName] = useState<string>("Urban Exploration Session");
  const [toolCalls, setToolCalls] = useState<ToolExecutionTrace[]>([]);
  const [timeline, setTimeline] = useState<Array<{ event: string; agent: string; timestamp: number; detail: string }>>([]);
  const [isStreaming, setIsStreaming] = useState<boolean>(true);
  const [isCompleted, setIsCompleted] = useState<boolean>(false);

  // If a session ID is provided, subscribe to live SSE stream
  useEffect(() => {
    if (!sessionId) return;

    // Fetch initial state first
    getExplorationSession(sessionId)
      .then((data) => {
        setStatus(data.status);
        setLandmarkName(data.landmark_name);
        setToolCalls(data.tool_calls || []);
        setTimeline(data.execution_timeline || []);
        if (data.status === "completed" || data.status === "partial") {
          setIsCompleted(true);
          setIsStreaming(false);
        }
      })
      .catch(console.error);

    // Subscribe to real-time events
    const unsubscribe = subscribeToExplorationEvents(
      sessionId,
      (eventData) => {
        if (eventData.status) setStatus(eventData.status);
        if (eventData.tool_calls) setToolCalls(eventData.tool_calls);
        if (eventData.timeline_latest) {
          setTimeline((prev) => {
            const exists = prev.some((e) => e.timestamp === eventData.timeline_latest.timestamp);
            return exists ? prev : [...prev, eventData.timeline_latest];
          });
        }
        if (eventData.event === "stream.ended" || eventData.status === "completed" || eventData.status === "partial") {
          setIsCompleted(true);
          setIsStreaming(false);
        }
      },
      (err) => {
        console.warn("SSE stream closed or completed", err);
        setIsStreaming(false);
      }
    );

    return () => {
      unsubscribe();
    };
  }, [sessionId]);

  // Demo shortcut to trigger a live session if none selected
  const handleLaunchSample = async () => {
    try {
      const res = await startExploration({
        landmark_id: "osm-node-kapaleeshwarar",
        landmark_name: "Kapaleeshwarar Temple",
        latitude: 13.0334,
        longitude: 80.2699,
        category: "worship_hindu",
        language: "en",
        story_style: "documentary",
        duration_seconds: 90,
        generate_audio: true
      });
      router.push(`/workspace?session_id=${res.session_id}`);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 glass-panel p-5 rounded-2xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-purple-950 text-purple-300 border border-purple-800">
              LangGraph Multi-Agent Engine
            </span>
            <span className="text-[10px] font-mono text-slate-400">
              Session: {sessionId || "No Active Session"}
            </span>
          </div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-cyan-400" />
            {landmarkName}
          </h2>
        </div>

        <div className="flex items-center gap-3">
          {sessionId ? (
            isCompleted ? (
              <Link
                href={`/story?session_id=${sessionId}`}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-600 text-white text-xs font-semibold shadow-lg shadow-cyan-500/20 hover:opacity-90 transition-opacity"
              >
                <Headset className="w-4 h-4" />
                Listen to Audio Story
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            ) : (
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-xs font-mono text-cyan-300">
                <RotateCw className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                Agents Orchestrating...
              </div>
            )
          ) : (
            <button
              onClick={handleLaunchSample}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold transition-colors"
            >
              <PlayCircle className="w-4 h-4" />
              Run Demo Workflow (Kapaleeshwarar Temple)
            </button>
          )}
        </div>
      </div>

      {/* Visualizer Component */}
      <AgentGraphVisualizer
        currentStatus={status}
        toolCalls={toolCalls}
        timeline={timeline}
        isStreaming={isStreaming}
      />
    </div>
  );
}

export default function WorkspacePage() {
  return (
    <Suspense fallback={
      <div className="p-12 text-center text-slate-400 text-sm">
        Loading Agent Workspace...
      </div>
    }>
      <WorkspaceContent />
    </Suspense>
  );
}
