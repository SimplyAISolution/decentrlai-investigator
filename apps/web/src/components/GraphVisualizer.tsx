"use client";

import React from "react";
import cytoscape from "cytoscape";
import CytoscapeComponent from "react-cytoscapejs";

const layout = { name: "cose", idealEdgeLength: 100, nodeOverlap: 20 };

const stylesheet: cytoscape.Stylesheet[] = [
  {
    selector: "node",
    style: {
      "background-color": "#3b82f6",
      "label": "data(label)",
      "color": "#e2e8f0",
      "text-valign": "bottom",
      "text-halign": "center",
      "text-margin-y": 8,
      "font-size": "12px",
      "width": "40px",
      "height": "40px",
    }
  },
  {
    selector: "edge",
    style: {
      "width": 2,
      "line-color": "#475569",
      "target-arrow-color": "#475569",
      "target-arrow-shape": "triangle",
      "curve-style": "bezier",
      "label": "data(label)",
      "font-size": "10px",
      "color": "#94a3b8",
      "text-background-opacity": 1,
      "text-background-color": "#0f172a",
      "text-background-padding": "2px",
    }
  }
];

export default function GraphVisualizer({ elements }: { elements: cytoscape.ElementDefinition[] }) {
  return (
    <div className="w-full h-[600px] border border-slate-800 rounded-xl overflow-hidden bg-slate-950 shadow-inner">
      <CytoscapeComponent 
        elements={elements} 
        style={{ width: "100%", height: "100%" }} 
        stylesheet={stylesheet}
        layout={layout}
        minZoom={0.5}
        maxZoom={3}
      />
    </div>
  );
}
