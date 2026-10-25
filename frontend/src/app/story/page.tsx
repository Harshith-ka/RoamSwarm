"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Headset, Cpu, ArrowLeft, RotateCcw, Share2, Sparkles, Volume2 } from "lucide-react";
import { AudioStoryPlayer } from "@/components/AudioStoryPlayer";
import { CitationDrawer } from "@/components/CitationDrawer";
import { VenueCard } from "@/components/VenueCard";
import { AudioQA } from "@/components/AudioQA";
import { getExplorationSession, getExplorationHistory } from "@/lib/api";
import { ExplorationSession } from "@/lib/types";

function StoryContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");

  const [session, setSession] = useState<ExplorationSession | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadStory() {
      setLoading(true);
      try {
        let targetId = sessionId;
        if (!targetId) {
          // Load most recent completed session if none specified
          const history = await getExplorationHistory();
          if (history.length > 0) {
            targetId = history[0].session_id;
          }
        }

        if (targetId) {
          const data = await getExplorationSession(targetId);
          setSession(data);
        }
      } catch (err) {
        console.error("Failed loading story session", err);
      } finally {
        setLoading(false);
      }
    }
    loadStory();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="p-16 text-center text-slate-400 space-y-3">
        <Volume2 className="w-10 h-10 text-cyan-400 animate-pulse mx-auto" />
        <p className="text-sm">Synthesizing audio story and verifying citations...</p>
      </div>
    );
  }

  if (!session || !session.story_script) {
    return (
      <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800 space-y-4 max-w-lg mx-auto my-12">
        <Headset className="w-12 h-12 text-slate-500 mx-auto" />
        <h3 className="text-lg font-bold text-slate-200">No Story Session Selected</h3>
        <p className="text-xs text-slate-400">
          Select a landmark on the Explore map to let the four agents research and synthesize an audio guide.
        </p>
        <Link
          href="/"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 text-white text-xs font-semibold hover:bg-cyan-500 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Go to Explore Map
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Banner Navigation */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 glass-panel p-5 rounded-2xl border border-slate-800">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="p-2 rounded-lg bg-slate-900 border border-slate-700/80 text-slate-400 hover:text-white"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2 mb-0.5">
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800">
                Verified Narration
              </span>
              <span className="text-[10px] font-mono text-slate-400">
                Session: {session.session_id}
              </span>
            </div>
            <h2 className="text-xl font-bold text-slate-100">{session.landmark_name}</h2>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href={`/workspace?session_id=${session.session_id}`}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 border border-slate-700 transition-colors"
          >
            <Cpu className="w-3.5 h-3.5 text-purple-400" />
            Inspect Agent Traces
          </Link>
        </div>
      </div>

      {/* Main Grid: Story Narration & Player (7 cols) + Citations & Venue Card (5 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Audio Player & Synced Transcript */}
        <div className="lg:col-span-7 space-y-6">
          <AudioStoryPlayer
            audioUrl={session.audio_url}
            transcript={session.story_script}
            landmarkName={session.landmark_name}
            style={session.story_style}
            durationSeconds={session.duration_seconds}
          />
          <AudioQA
            sessionId={session.session_id}
            landmarkName={session.landmark_name}
          />
        </div>

        {/* Right Column: Claim Citations & Live Venue Status */}
        <div className="lg:col-span-5 space-y-6">
          <VenueCard
            venueFacts={session.venue_facts || []}
            landmarkName={session.landmark_name}
          />
          <CitationDrawer citations={session.citations || []} />
        </div>
      </div>
    </div>
  );
}

export default function StoryPage() {
  return (
    <Suspense fallback={
      <div className="p-12 text-center text-slate-400 text-sm">
        Loading Story Experience...
      </div>
    }>
      <StoryContent />
    </Suspense>
  );
}
