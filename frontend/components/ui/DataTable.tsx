"use client";

import React, { useState, useRef, useEffect } from "react";

export interface DataTableColumn {
  key: string;
  header: string;
  type?: "text" | "number" | "date";
  align?: "left" | "right" | "center";
}

interface DataTableProps {
  columns: DataTableColumn[];
  data: Record<string, unknown>[];
  onCellChange?: (rowIndex: number, columnKey: string, newValue: string | number) => void;
  flaggedCells?: Set<string>; // set of "rowIndex:columnKey"
  className?: string;
}

export default function DataTable({
  columns,
  data,
  onCellChange,
  flaggedCells = new Set(),
  className = "",
}: DataTableProps) {
  const [editingCell, setEditingCell] = useState<{ row: number; col: number } | null>(null);
  const [editValue, setEditValue] = useState<string>("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editingCell && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [editingCell]);

  const handleStartEdit = (row: number, col: number) => {
    const colDef = columns[col];
    if (!colDef) return;
    const rawVal = data[row]?.[colDef.key];
    setEditValue(rawVal !== undefined && rawVal !== null ? String(rawVal) : "");
    setEditingCell({ row, col });
  };

  const handleSaveEdit = () => {
    if (!editingCell) return;
    const colDef = columns[editingCell.col];
    if (!colDef) return;
    let parsed: string | number = editValue;
    if (colDef.type === "number") {
      const num = parseFloat(editValue);
      if (!Number.isNaN(num)) parsed = num;
    }
    onCellChange?.(editingCell.row, colDef.key, parsed);
    setEditingCell(null);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSaveEdit();
    } else if (e.key === "Escape") {
      setEditingCell(null);
    }
  };

  return (
    <div className={`overflow-x-auto border border-zinc-800 rounded-lg bg-zinc-950/40 ${className}`}>
      <table className="w-full text-left text-xs text-zinc-300 border-collapse">
        <thead className="bg-zinc-900/80 sticky top-0 border-b border-zinc-800 backdrop-blur-md z-10">
          <tr>
            <th className="p-2.5 text-zinc-500 font-medium w-10 text-center">#</th>
            {columns.map((col) => (
              <th
                key={col.key}
                className={`p-2.5 font-medium text-zinc-400 ${
                  col.align === "right" ? "text-right" : col.align === "center" ? "text-center" : "text-left"
                }`}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-800/60 font-mono">
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length + 1} className="p-4 text-center text-zinc-500 italic">
                No records extracted.
              </td>
            </tr>
          ) : (
            data.map((row, rIdx) => (
              <tr key={rIdx} className="hover:bg-zinc-900/40 transition-colors">
                <td className="p-2.5 text-zinc-500 text-center select-none">{rIdx + 1}</td>
                {columns.map((col, cIdx) => {
                  const cellKey = `${rIdx}:${col.key}`;
                  const isFlagged = flaggedCells.has(cellKey);
                  const isEditing = editingCell?.row === rIdx && editingCell?.col === cIdx;
                  const cellVal = row[col.key];

                  return (
                    <td
                      key={col.key}
                      onClick={() => handleStartEdit(rIdx, cIdx)}
                      className={`p-2.5 cursor-pointer relative transition-all ${
                        col.align === "right" ? "text-right" : col.align === "center" ? "text-center" : "text-left"
                      } ${
                        isFlagged
                          ? "bg-amber-500/10 text-amber-300 border-l-2 border-amber-500"
                          : "hover:bg-zinc-800/30"
                      }`}
                    >
                      {isEditing ? (
                        <input
                          ref={inputRef}
                          type={col.type === "number" ? "number" : "text"}
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          onBlur={handleSaveEdit}
                          onKeyDown={handleKeyDown}
                          className="w-full bg-zinc-900 border border-accent rounded px-1.5 py-0.5 text-zinc-100 outline-none"
                        />
                      ) : (
                        <span>
                          {cellVal !== undefined && cellVal !== null
                            ? typeof cellVal === "number"
                              ? cellVal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
                              : String(cellVal)
                            : "—"}
                        </span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
