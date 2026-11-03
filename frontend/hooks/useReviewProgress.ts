import { useDocumentStore, selectFlaggedCount, selectUnresolvedCount } from "@/store/useDocumentStore";

export interface ReviewProgress {
  total: number;
  resolved: number;
  remaining: number;
  percent: number;
}

export function useReviewProgress(): ReviewProgress {
  const extractedData = useDocumentStore((state) => state.extractedData);
  const resolvedFields = useDocumentStore((state) => state.resolvedFields);

  if (!extractedData) {
    return { total: 0, resolved: 0, remaining: 0, percent: 100 };
  }

  const flaggedMetrics = extractedData.validation_metrics.filter((m) => m.needs_review);
  const total = flaggedMetrics.length;

  if (total === 0) {
    return { total: 0, resolved: 0, remaining: 0, percent: 100 };
  }

  let resolved = 0;
  for (const m of flaggedMetrics) {
    if (m.field_name === "line_items") {
      const anyLineResolved = Object.keys(resolvedFields).some((k) =>
        k.startsWith("line_items")
      );
      if (anyLineResolved) resolved += 1;
    } else {
      if (resolvedFields[m.field_name]) {
        resolved += 1;
      }
    }
  }

  const remaining = Math.max(0, total - resolved);
  const percent = Math.min(100, Math.round((resolved / total) * 100));

  return { total, resolved, remaining, percent };
}
