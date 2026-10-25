"use client";

import { useState, useRef, useEffect } from "react";
import { Play, Pause, RotateCcw, Volume2, FastForward, Download, Sparkles, CheckCircle2 } from "lucide-react";

interface AudioStoryPlayerProps {
  audioUrl?: string;
  transcript: string;
  landmarkName: string;
  style: string;
  durationSeconds: number;
}

export function AudioStoryPlayer({
  audioUrl,
  transcript,
  landmarkName,
  style,
  durationSeconds
}: AudioStoryPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(durationSeconds || 60);
  const [playbackRate, setPlaybackRate] = useState(1.0);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Normalize full audio URL
  const resolvedAudioUrl = audioUrl
    ? audioUrl.startsWith("http")
      ? audioUrl
      : `http://127.0.0.1:8000${audioUrl}`
    : null;

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().then(() => setIsPlaying(true)).catch(console.error);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
      if (audioRef.current.duration && !isNaN(audioRef.current.duration)) {
        setDuration(audioRef.current.duration);
      }
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = parseFloat(e.target.value);
    setCurrentTime(newTime);
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
    }
  };

  const changeSpeed = () => {
    const nextRate = playbackRate === 1.0 ? 1.25 : playbackRate === 1.25 ? 1.5 : 1.0;
    setPlaybackRate(nextRate);
    if (audioRef.current) {
      audioRef.current.playbackRate = nextRate;
    }
  };

  const rewind10 = () => {
    if (audioRef.current) {
      audioRef.current.currentTime = Math.max(0, audioRef.current.currentTime - 10);
    }
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  // Split transcript into readable sentences
  const paragraphs = transcript.split("\n\n").filter(Boolean);

  return (
    <div className="space-y-6">
      {/* Audio Controller Card */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-2xl relative overflow-hidden">
        {/* Ambient background glow */}
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-6">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800">
                  {style} narration
                </span>
                <span className="text-[10px] font-mono text-slate-400">
                  Target: {durationSeconds}s
                </span>
              </div>
              <h3 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                <Volume2 className="w-5 h-5 text-cyan-400" />
                {landmarkName} Audio Story
              </h3>
            </div>

            {resolvedAudioUrl && (
              <a
                href={resolvedAudioUrl}
                download={`roamswarm_${landmarkName.toLowerCase().replace(/\s+/g, "_")}.wav`}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 transition-colors border border-slate-700"
              >
                <Download className="w-3.5 h-3.5" />
                Export WAV
              </a>
            )}
          </div>

          {/* HTML5 Audio Element */}
          {resolvedAudioUrl && (
            <audio
              ref={audioRef}
              src={resolvedAudioUrl}
              onTimeUpdate={handleTimeUpdate}
              onEnded={() => setIsPlaying(false)}
            />
          )}

          {/* Simulated Waveform Bars */}
          <div className="flex items-center justify-between gap-1 h-12 my-4 px-2">
            {Array.from({ length: 48 }).map((_, i) => {
              const progress = currentTime / Math.max(1, duration);
              const barProgress = i / 48;
              const isPast = barProgress <= progress;
              const height = isPlaying
                ? 15 + Math.sin((i * 0.4) + (currentTime * 4)) * 30 + (i % 5) * 8
                : 20 + ((i * 7) % 35);

              return (
                <div
                  key={i}
                  style={{ height: `${Math.max(8, Math.min(48, height))}px` }}
                  className={`flex-1 rounded-full transition-all duration-150 ${
                    isPast
                      ? "bg-gradient-to-t from-cyan-500 to-purple-500"
                      : "bg-slate-800"
                  }`}
                />
              );
            })}
          </div>

          {/* Seek Bar */}
          <div className="space-y-1 mb-4">
            <input
              type="range"
              min={0}
              max={duration || 100}
              step={0.1}
              value={currentTime}
              onChange={handleSeek}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
            />
            <div className="flex justify-between text-[11px] font-mono text-slate-400">
              <span>{formatTime(currentTime)}</span>
              <span>{formatTime(duration)}</span>
            </div>
          </div>

          {/* Control Buttons */}
          <div className="flex items-center justify-between pt-2">
            <button
              onClick={rewind10}
              className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 p-2 rounded-lg hover:bg-slate-800/60"
            >
              <RotateCcw className="w-4 h-4" />
              <span>-10s</span>
            </button>

            <button
              onClick={togglePlay}
              disabled={!resolvedAudioUrl}
              className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-xl shadow-cyan-500/25 hover:scale-105 active:scale-95 transition-all disabled:opacity-50"
            >
              {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6 ml-0.5" />}
            </button>

            <button
              onClick={changeSpeed}
              className="text-xs font-mono font-semibold px-2.5 py-1.5 rounded-lg bg-slate-800 text-cyan-300 hover:bg-slate-700 transition-colors border border-slate-700"
            >
              {playbackRate}x
            </button>
          </div>
        </div>
      </div>

      {/* Synchronized Transcript View */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
          <h4 className="font-semibold text-sm text-slate-200 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-400" />
            Verified Narration Transcript
          </h4>
          <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            100% Grounded
          </span>
        </div>

        <div className="space-y-4 text-slate-300 text-sm leading-relaxed">
          {paragraphs.map((p, idx) => (
            <p key={idx} className="p-3 rounded-xl bg-slate-900/50 border border-slate-800/80 hover:border-slate-700 transition-colors">
              {p}
            </p>
          ))}
        </div>
      </div>
    </div>
  );
}
