"use client";

import { CitationItem } from "@/lib/types";
import { ExternalLink, ShieldCheck, HelpCircle, AlertCircle, FileText } from "lucide-react";

interface CitationDrawerProps {
  citations: CitationItem[];
}

export function CitationDrawer({ citations }: CitationDrawerProps) {
  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800">
      <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
        <div>
          <h4 className="font-semibold text-sm text-slate-200 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            Claim-to-Source Traceability Matrix ({citations.length})
          </h4>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Every factual assertion linked to verifiable external archives
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {citations.length === 0 ? (
          <div className="p-6 text-center text-slate-500 text-xs">
            No citation records attached to this session.
          </div>
        ) : (
          citations.map((c, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 transition-all text-xs space-y-2"
            >
              <div className="flex items-start justify-between gap-2">
                <span className="font-mono text-[10px] text-cyan-400 font-semibold px-1.5 py-0.5 rounded bg-cyan-950/80 border border-cyan-800/60">
                  {c.claim_id || `CLAIM-${idx+1}`}
                </span>
                <div className="flex items-center gap-1.5">
                  <span className={`text-[9px] uppercase font-mono px-1.5 py-0.5 rounded font-semibold ${
                    c.verification_status === "verified"
                      ? "bg-emerald-950 text-emerald-400 border border-emerald-800/60"
                      : "bg-amber-950 text-amber-400 border border-amber-800/60"
                  }`}>
                    {c.verification_status}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">
                    {Math.round(c.confidence * 100)}% conf
                  </span>
                </div>
              </div>

              <p className="text-slate-200 italic leading-relaxed">
                "{c.claim_text}"
              </p>

              <div className="flex items-center justify-between pt-1 border-t border-slate-800/80 text-[11px] text-slate-400">
                <span className="flex items-center gap-1 text-slate-300">
                  <FileText className="w-3.5 h-3.5 text-slate-400" />
                  {c.publisher || "Archival Source"}
                </span>

                {c.source_url ? (
                  <a
                    href={c.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-cyan-400 hover:underline hover:text-cyan-300 font-mono text-[10px]"
                  >
                    View Source
                    <ExternalLink className="w-3 h-3" />
                  </a>
                ) : (
                  <span className="text-[10px] text-slate-500 font-mono">Unpublished Document</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
