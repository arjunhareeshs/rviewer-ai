import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import MermaidMindmap from "../../components/roadmap/MermaidMindmap";
import RoadmapSidePanel from "../../components/roadmap/RoadmapSidePanel";
import { useSearchParams } from "react-router-dom";
import { useResumeData } from "../../hooks/useResumeData";
import { useRoadmapStore } from "../../stores/useRoadmapStore";

export default function RoadmapPage() {
  const [view, setView] = useState<'roadmap' | 'timeline'>('roadmap');
  const [searchParams] = useSearchParams();
  const resumeId = searchParams.get('id');
  const { data, loading, error } = useResumeData(resumeId);
  const { progress, setRoadmap } = useRoadmapStore();

  useEffect(() => {
    if (data && data.project_analysis?.roadmap) {
      setRoadmap(data.project_analysis.roadmap);
    }
  }, [data, setRoadmap]);

  if (loading) return <div className="p-8 text-text-muted">Loading roadmap...</div>;
  if (error) return <div className="p-8 text-danger">{error}</div>;
  if (!data || !data.project_analysis?.roadmap) return <div className="p-8 text-text-muted">No roadmap available for this resume.</div>;

  const roadmapData = data.project_analysis.roadmap;

  // Calculate real progress
  const totalNodes = roadmapData.tracks.reduce((acc: number, track: any) => acc + (track.nodes || []).length, 0);
  const completedNodes = roadmapData.tracks.reduce((acc: number, track: any) => {
    return acc + (track.nodes || []).filter((node: any) => progress[node.id]).length;
  }, 0);
  const completionPercentage = totalNodes > 0 ? Math.round((completedNodes / totalNodes) * 100) : 0;

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="h-full flex flex-col max-w-[1400px] mx-auto relative overflow-hidden">
      <div className="flex-none p-8 pb-4">
        <div className="flex justify-between items-end mb-6">
          <div>
            <h1 className="font-display text-4xl text-text-primary tracking-tight">Your Skill Roadmap</h1>
            <p className="text-text-secondary text-lg mt-1 font-medium">Target: <strong className="text-text-primary">{roadmapData.target_role || "ML Engineer"}</strong></p>
          </div>
          
          <div className="flex gap-4">
             <div className="flex bg-surface rounded-lg p-1 border border-border shadow-sm">
                <button 
                  onClick={() => setView('roadmap')}
                  className={`px-4 py-1.5 text-sm font-bold rounded-md transition-colors ${view === 'roadmap' ? 'bg-accent-soft text-accent' : 'text-text-secondary hover:text-text-primary'}`}
                >
                  Roadmap View
                </button>
                <button 
                  onClick={() => setView('timeline')}
                  className={`px-4 py-1.5 text-sm font-bold rounded-md transition-colors ${view === 'timeline' ? 'bg-accent-soft text-accent' : 'text-text-secondary hover:text-text-primary'}`}
                >
                  Timeline View
                </button>
             </div>
          </div>
        </div>

        <div className="bg-surface p-4 rounded-xl border border-border flex items-center gap-6 shadow-sm">
          <div className="flex-1">
             <div className="flex justify-between text-xs font-bold uppercase tracking-wider mb-2">
                <span className="text-text-primary">Progress</span>
                <span className="text-accent">{completionPercentage}% Complete</span>
             </div>
             <div className="w-full bg-cream h-2 rounded-full overflow-hidden">
               <div className="bg-accent h-full rounded-full transition-all duration-300" style={{width: `${completionPercentage}%`}}></div>
             </div>
          </div>
          <div className="text-sm font-bold text-text-secondary">
            Estimated Duration: <strong className="text-text-primary">{roadmapData.total_duration || "24 weeks"}</strong>
          </div>
        </div>
      </div>

      <div className="flex-1 p-8 pt-4 flex gap-8 min-h-0 relative">
        <div className="flex-1 bg-surface rounded-2xl border border-border shadow-sm overflow-hidden flex flex-col relative">
          {view === 'roadmap' ? (
             <div className="flex-1">
               <MermaidMindmap roadmap={roadmapData} />
             </div>
          ) : (
             <div className="flex-1 p-8 overflow-y-auto space-y-8 bg-cream">
               <h2 className="font-bold text-xl text-text-primary mb-4">Milestone Timeline</h2>
               {roadmapData.tracks.map((track: any) => (
                 <div key={track.track_id} className="bg-surface p-6 rounded-2xl border border-border shadow-sm space-y-4 mb-6">
                   <h3 className="font-bold text-lg text-text-primary border-b border-border pb-2">{track.track_name}</h3>
                   <div className="relative pl-6 border-l-2 border-accent/20 ml-3 space-y-6">
                     {(track.nodes || []).map((node: any) => {
                       const isNodeCompleted = !!progress[node.id];
                       return (
                         <div key={node.id} className="relative">
                           {/* Dot */}
                           <div className={`absolute -left-[31px] top-1.5 w-4 h-4 rounded-full border-2 bg-white transition-colors ${isNodeCompleted ? 'border-success bg-success' : 'border-accent'}`} />
                           <div className="bg-cream p-4 rounded-xl border border-border hover:border-accent transition-colors flex justify-between items-center">
                             <div>
                               <h4 className="font-bold text-text-primary">{node.label}</h4>
                               <div className="flex gap-2 mt-2">
                                 <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded ${
                                   node.priority === 'critical' ? 'bg-danger-soft text-danger' :
                                   node.priority === 'high' ? 'bg-warning-soft text-warning' :
                                   'bg-accent-soft text-accent'
                                 }`}>
                                   {node.priority}
                                 </span>
                                 <span className="text-[10px] font-semibold text-text-muted font-mono">{node.duration}</span>
                               </div>
                             </div>
                             <span className="text-xs font-semibold text-text-muted bg-surface border border-border px-2 py-1 rounded">
                               {isNodeCompleted ? "✓ Done" : "Todo"}
                             </span>
                           </div>
                         </div>
                       );
                     })}
                   </div>
                 </div>
               ))}
             </div>
          )}
        </div>

        {/* Dynamic Resource Side Panel */}
        <RoadmapSidePanel />
      </div>
    </motion.div>
  );
}
