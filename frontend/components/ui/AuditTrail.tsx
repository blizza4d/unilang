"use client";

import React from "react";
import { History, ShieldCheck, Edit3 } from "lucide-react";
import type { StoredDocumentDetail } from "@/lib/historyApi";

interface AuditTrailProps {
  document: StoredDocumentDetail | null;
}

export function AuditTrail({ document }: AuditTrailProps): React.JSX.Element {
  if (!document) {
    return (
      <div className="p-4 text-center text-xs font-mono text-zinc-500">
        No audit record selected
      </div>
    );
  }

  const edits = document.edits || [];
  const approvals = document.approvals || [];
  const hasEntries = edits.length > 0 || approvals.length > 0;

  return (
    <div className="w-full space-y-4">
      <div className="flex items-center justify-between pb-2 border-b border-[#232730]">
        <div className="flex items-center gap-2 text-xs font-mono font-medium text-zinc-300">
          <History className="w-4 h-4 text-cyan-400" />
          <span>Audit & Ledger Trail</span>
        </div>
        <span className="text-[11px] font-mono text-zinc-500">
          {edits.length} edits &bull; {approvals.length} approvals
        </span>
      </div>

      {!hasEntries ? (
        <div className="p-4 rounded-lg bg-zinc-900/40 border border-zinc-800 text-center text-xs text-zinc-500 font-mono">
          Document is untouched since initial AI extraction
        </div>
      ) : (
        <div className="space-y-3 max-h-[300px] overflow-y-auto scrollbar-thin pr-1">
          {/* Approvals */}
          {approvals.map((app) => (
            <div
              key={app.id}
              className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-500/30 flex items-start gap-2.5"
            >
              <ShieldCheck className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-emerald-300">
                    Approved by {app.user_id}
                  </span>
                  <span className="text-[10px] font-mono text-zinc-500">
                    {new Date(app.created_at).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
                {app.notes && (
                  <p className="text-xs text-zinc-400 mt-1 italic">
                    &ldquo;{app.notes}&rdquo;
                  </p>
                )}
              </div>
            </div>
          ))}

          {/* Edits */}
          {edits.map((edit) => (
            <div
              key={edit.id}
              className="p-3 rounded-lg bg-zinc-900/70 border border-zinc-800 flex items-start gap-2.5"
            >
              <Edit3 className="w-4 h-4 text-cyan-400 mt-0.5 shrink-0" />
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-medium text-cyan-300">
                    {edit.field_name}
                  </span>
                  <span className="text-[10px] font-mono text-zinc-500">
                    {new Date(edit.created_at).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>

                <div className="mt-1.5 flex items-center gap-2 text-xs font-mono">
                  <span className="text-rose-400/80 line-through truncate max-w-[120px]">
                    {String(edit.old_value ?? "—")}
                  </span>
                  <span className="text-zinc-600">&rarr;</span>
                  <span className="text-emerald-400 font-semibold truncate max-w-[140px]">
                    {String(edit.new_value ?? "—")}
                  </span>
                </div>

                <div className="mt-1 flex items-center justify-between text-[10px] text-zinc-500">
                  <span>User: {edit.user_id}</span>
                  {edit.reason && <span>Reason: {edit.reason}</span>}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
