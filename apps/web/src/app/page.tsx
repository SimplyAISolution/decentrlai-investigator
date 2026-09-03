"use client";

import { useEffect, useState, useRef } from "react";
import dynamic from "next/dynamic";
import { ElementDefinition } from "cytoscape";

const GraphVisualizer = dynamic(() => import("@/components/GraphVisualizer"), { ssr: false });

interface LogEntry {
  step: string;
  message: string;
  timestamp: string;
}

export default function InvestigationDashboard() {
  const [elements, setElements] = useState<ElementDefinition[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [status, setStatus] = useState<"connecting" | "live" | "complete" | "disconnected">("connecting");
  const logEndRef = useRef<HTMLDivElement>(null);

  // Fixed investigation ID matching the demo test pipeline
  const INVESTIGATION_ID = "00000000-0000-0000-0000-000000000001";

  const fetchGraph = () => {
    fetch(`http://localhost:8000/api/v1/investigations/${INVESTIGATION_ID}/graph`)
      .then((res) => res.json())
      .then((data) => setElements(data.elements))
      .catch((err) => console.error("Error fetching graph:", err));
  };

  useEffect(() => {
    fetchGraph();

    const ws = new WebSocket(`ws://localhost:8000/api/v1/investigations/${INVESTIGATION_ID}/ws`);

    ws.onopen = () => {
      setStatus("live");
      setLogs((prev) => [...prev, {
        step: "WS_CONNECTED",
        message: "Connected to investigation event stream",
        timestamp: new Date().toLocaleTimeString()
      }]);
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        setLogs((prev) => [...prev, {
          step: payload.step,
          message: payload.message,
          timestamp: new Date().toLocaleTimeString()
        }]);

        if (payload.step === "GRAPH_UPDATED" || payload.step === "COMPLETE") {
          fetchGraph();
        }

        if (payload.step === "COMPLETE") {
          setStatus("complete");
        }
      } catch (err) {
        console.error("Malformed WebSocket frame:", err);
      }
    };

    ws.onclose = () => setStatus("disconnected");
    ws.onerror = () => setStatus("disconnected");

    return () => ws.close();
  }, []);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const nodeCount = elements.filter((e) => !e.data.source).length;
  const edgeCount = elements.filter((e) => e.data.source).length;

  return (
    <main className="min-h-screen bg-slate-900 text-slate-200 p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <header className="flex items-center justify-between border-b border-slate-800 pb-6">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">Investigation: INV-000001</h1>
            <p className="text-slate-400 mt-1 text-sm">Target: Autonomous AI Systems & Neo4j Graphs</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`w-2.5 h-2.5 rounded-full ${
              status === "live" ? "bg-emerald-500 animate-pulse" :
              status === "complete" ? "bg-blue-500" : "bg-rose-500"
            }`} />
            <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">
              {status}
            </span>
          </div>
        </header>

        {/* Graph Section */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-100">Knowledge Graph</h2>
            <div className="text-xs text-slate-400">
              Nodes: <span className="text-slate-200 font-mono font-bold">{nodeCount}</span> | 
              Edges: <span className="text-slate-200 font-mono font-bold ml-1">{edgeCount}</span>
            </div>
          </div>
          <GraphVisualizer elements={elements} />
        </section>

        {/* Real-Time Worker Log Stream */}
        <section className="space-y-3">
          <h2 className="text-lg font-semibold text-slate-100">Live Investigation Feed</h2>
          <div className="h-56 bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-xs overflow-y-auto space-y-1.5 shadow-inner">
            {logs.length === 0 ? (
              <div className="text-slate-600 italic">Waiting for events from ARQ worker...</div>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="flex items-start gap-3">
                  <span className="text-slate-500 shrink-0">{log.timestamp}</span>
                  <span className={`font-semibold shrink-0 px-1.5 py-0.5 rounded text-[10px] ${
                    log.step === "STARTED" ? "bg-blue-950 text-blue-400" :
                    log.step === "SEARCHING" ? "bg-indigo-950 text-indigo-400" :
                    log.step === "COLLECTING" ? "bg-amber-950 text-amber-400" :
                    log.step === "EVIDENCE_STORED" ? "bg-emerald-950 text-emerald-400" :
                    log.step === "EXTRACTING" ? "bg-purple-950 text-purple-400" :
                    log.step === "GRAPH_UPDATED" ? "bg-cyan-950 text-cyan-400" :
                    log.step === "COMPLETE" ? "bg-green-950 text-green-300 font-bold" :
                    "bg-slate-800 text-slate-400"
                  }`}>
                    {log.step}
                  </span>
                  <span className="text-slate-300">{log.message}</span>
                </div>
              ))
            )}
            <div ref={logEndRef} />
          </div>
        </section>
      </div>
    </main>
  );
}
