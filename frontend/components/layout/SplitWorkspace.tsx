"use client";

import React, { ReactNode } from "react";

export interface SplitWorkspaceProps {
  left: ReactNode;
  right: ReactNode;
}

export const SplitWorkspace: React.FC<SplitWorkspaceProps> = ({ left, right }) => {
  return (
    <div className="flex flex-col lg:flex-row w-full h-full overflow-hidden">
      {/* Left Pane (Document Preview / Ingestion) */}
      <section
        aria-label="Document Viewer Pane"
        className="w-full lg:w-1/2 h-1/2 lg:h-full overflow-hidden relative bg-app"
      >
        {left}
      </section>

      {/* Right Pane (Structured Extraction & Review) */}
      <section
        aria-label="Extracted Data Pane"
        className="w-full lg:w-1/2 h-1/2 lg:h-full overflow-hidden relative"
      >
        {right}
      </section>
    </div>
  );
};

export default SplitWorkspace;
