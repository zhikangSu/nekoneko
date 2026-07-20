"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import type { AgentTrace } from "@/types/trace";

export type TraceSource = "main" | "ambient";

export interface LatestTraceEntry {
  trace: AgentTrace;
  source: TraceSource;
}

interface TraceStateContextValue {
  latestTraceEntry: LatestTraceEntry | undefined;
  traceVersion: number;
  publishTrace: (trace: AgentTrace, source: TraceSource) => void;
}

const TraceStateContext = createContext<TraceStateContextValue | null>(null);

export function useTraceState(): TraceStateContextValue {
  const value = useContext(TraceStateContext);
  if (!value) {
    throw new Error("useTraceState must be used within a TraceStateProvider");
  }
  return value;
}

export function TraceStateProvider({ children }: { children: ReactNode }) {
  const [latestTraceEntry, setLatestTraceEntry] = useState<
    LatestTraceEntry | undefined
  >();
  const [traceVersion, setTraceVersion] = useState(0);

  const publishTrace = useCallback(
    (trace: AgentTrace, source: TraceSource) => {
      setLatestTraceEntry({ trace, source });
      setTraceVersion((version) => version + 1);
    },
    [],
  );

  const value = useMemo(
    () => ({ latestTraceEntry, traceVersion, publishTrace }),
    [latestTraceEntry, publishTrace, traceVersion],
  );

  return (
    <TraceStateContext.Provider value={value}>
      {children}
    </TraceStateContext.Provider>
  );
}
