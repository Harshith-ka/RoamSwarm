"use client";

import { useState } from "react";
import { MessageSquare, Send, Sparkles, ShieldCheck, Loader2, ExternalLink } from "lucide-react";
import { askLandmarkQuestion } from "@/lib/api";

interface AudioQAProps {
  sessionId: string;
  landmarkName: string;
}

export function AudioQA({ sessionId, landmarkName }: AudioQAProps) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Array<{ role: "user" | "agent"; text: string; sources?: string[] }>>([
    {
      role: "agent",
      text: `Hello! I'm your audio guide agent for ${landmarkName}. Ask me anything about its architecture, history, or current visitor guidelines.`
    }
  ]);

  const suggestedQuestions = [
    "What are the visiting hours?",
    "When was this landmark built?",
    "Is there an admission fee?",
    "Tell me about the architecture"
  ];

  const handleSend = async (qToSend?: string) => {
    const q = (qToSend || question).trim();
    if (!q || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setQuestion("");
    setLoading(true);

    try {
      const res = await askLandmarkQuestion(sessionId, q);
      setMessages((prev) => [
        ...prev,
        {
          role: "agent",
          text: res.answer || "I don't have verified records on that in our archives.",
          sources: res.cited_sources || []
        }
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "agent",
          text: "Sorry, I could not query the grounded archives right now. Please try again."
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div>
          <h4 className="font-semibold text-sm text-slate-200 flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-cyan-400" />
            Ask AI Guide (Conversational Q&A)
          </h4>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Real-time inquiries during playback, strictly grounded in verified facts
          </p>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 flex items-center gap-1">
          <ShieldCheck className="w-3 h-3" /> Zero Hallucination
        </span>
      </div>

      {/* Suggested Quick Prompts */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
        {suggestedQuestions.map((sq, i) => (
          <button
            key={i}
            onClick={() => handleSend(sq)}
            disabled={loading}
            className="text-[11px] px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-cyan-300 hover:border-cyan-800/80 whitespace-nowrap transition-colors"
          >
            {sq}
          </button>
        ))}
      </div>

      {/* Chat Messages */}
      <div className="space-y-3 max-h-[260px] overflow-y-auto pr-1">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex flex-col text-xs ${
              m.role === "user" ? "items-end" : "items-start"
            }`}
          >
            <div
              className={`p-3 rounded-xl max-w-[85%] leading-relaxed ${
                m.role === "user"
                  ? "bg-cyan-600 text-white rounded-tr-none"
                  : "bg-slate-900/90 border border-slate-800 text-slate-200 rounded-tl-none"
              }`}
            >
              {m.text}

              {/* Attached Citation Links */}
              {m.sources && m.sources.length > 0 && (
                <div className="mt-2 pt-1.5 border-t border-slate-800/80 flex items-center gap-2 flex-wrap">
                  <span className="text-[10px] text-slate-400 font-mono">Sources:</span>
                  {m.sources.map((s, si) => (
                    <a
                      key={si}
                      href={s}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[10px] text-cyan-400 hover:underline flex items-center gap-1 font-mono"
                    >
                      [{si + 1}]
                      <ExternalLink className="w-2.5 h-2.5" />
                    </a>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-xs text-slate-400 italic p-2">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
            Historian & Live Scout verifying evidence...
          </div>
        )}
      </div>

      {/* Input box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="relative flex items-center"
      >
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={`Ask about ${landmarkName}...`}
          className="w-full pl-3.5 pr-10 py-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
        />
        <button
          type="submit"
          disabled={!question.trim() || loading}
          className="absolute right-1.5 p-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white disabled:opacity-40 transition-colors"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
}
