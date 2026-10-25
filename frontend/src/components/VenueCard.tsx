"use client";

import { VenueFact } from "@/lib/types";
import { Clock, Ticket, Accessibility, Globe, Phone, AlertTriangle, CheckCircle, HelpCircle } from "lucide-react";

interface VenueCardProps {
  venueFacts: VenueFact[];
  landmarkName: string;
}

export function VenueCard({ venueFacts, landmarkName }: VenueCardProps) {
  const getIconForAttr = (attr: string) => {
    switch (attr) {
      case "opening_hours":
        return Clock;
      case "admission":
        return Ticket;
      case "accessibility":
        return Accessibility;
      case "website":
        return Globe;
      case "phone":
        return Phone;
      default:
        return HelpCircle;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "verified":
        return (
          <span className="flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800">
            <CheckCircle className="w-3 h-3" />
            Verified Live
          </span>
        );
      case "unverified":
        return (
          <span className="flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-950 text-amber-400 border border-amber-800">
            <AlertTriangle className="w-3 h-3" />
            Unconfirmed
          </span>
        );
      case "missing":
        return (
          <span className="flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
            <HelpCircle className="w-3 h-3" />
            Not Published
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800">
      <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
        <h4 className="font-semibold text-sm text-slate-200 flex items-center gap-2">
          <Clock className="w-4 h-4 text-amber-400" />
          Live Scout Venue Access & Guidelines
        </h4>
        <span className="text-[11px] text-slate-400 font-mono">Freshness Tagged</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {venueFacts.length === 0 ? (
          <div className="p-6 col-span-2 text-center text-slate-500 text-xs">
            No venue access tags audited for this landmark.
          </div>
        ) : (
          venueFacts.map((vf, idx) => {
            const Icon = getIconForAttr(vf.attribute);
            return (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between gap-2"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-semibold text-slate-300 capitalize">
                    <Icon className="w-4 h-4 text-cyan-400" />
                    {vf.attribute.replace("_", " ")}
                  </div>
                  {getStatusBadge(vf.status)}
                </div>

                <p className="text-sm text-slate-100 font-medium leading-snug">
                  {vf.value}
                </p>

                {vf.note && (
                  <p className="text-[10px] text-slate-400 italic">
                    {vf.note}
                  </p>
                )}

                <div className="text-[10px] text-slate-500 font-mono pt-1 border-t border-slate-800/60">
                  Source: {vf.source}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
