import { useRoadmapStore } from "@/stores/useRoadmapStore";
import type { RoadmapData } from "@/stores/useRoadmapStore";

interface TimelineProps {
  roadmap: RoadmapData;
}

export default function TimelineView({ roadmap }: TimelineProps) {
  const { trackMode, progress } = useRoadmapStore();

  // Basic timeline logic: we'll spread nodes horizontally based on their duration.
  // We mock the "weeks" dimension for visualization based on the dependencies.
  
  // Create a timeline grid of 24 weeks
  const WEEKS = 24;
  
  return (
    <div className="w-full h-full overflow-auto bg-white p-8">
      
      <div className="min-w-[1000px]">
        {/* Timeline Header */}
        <div className="flex border-b-2 border-gray-200 pb-2 mb-6 ml-48">
          {Array.from({ length: WEEKS / 2 }).map((_, i) => (
            <div key={i} className="flex-1 text-xs font-bold text-gray-400 text-center">
              Wk {(i * 2) + 1}
            </div>
          ))}
        </div>

        {/* Tracks */}
        <div className="space-y-8">
          {roadmap.tracks.map(track => {
            
            // Filter nodes if in fast mode
            const visibleNodes = trackMode === 'fast' 
              ? track.nodes.filter(n => n.priority === 'critical' || n.priority === 'high')
              : track.nodes;
              
            if (visibleNodes.length === 0) return null;

            return (
              <div key={track.track_id} className="relative flex">
                {/* Track Label */}
                <div className="w-48 flex-none border-r border-gray-200 pr-4 py-2">
                  <h3 className="font-bold text-gray-800 text-sm">{track.track_name}</h3>
                </div>
                
                {/* Track Lane */}
                <div className="flex-1 relative bg-gray-50/50 rounded-r-lg border border-transparent hover:border-gray-100 flex items-center px-4 gap-2 overflow-hidden py-2 min-h-[60px]">
                  
                  {visibleNodes.map((node) => {
                    const isDone = !!progress[node.id];
                    // Very simplistic Gantt blocks - in a real D3/react-gantt setup, 
                    // width would be mapped strictly to node.duration, and left offset to node.depends_on path.
                    // For UI visualization matching the spec text representation:
                    return (
                      <div 
                        key={node.id}
                        className={`flex-none h-10 px-3 py-1.5 rounded-md border text-xs font-medium flex items-center justify-center transition-all ${
                          isDone 
                            ? 'bg-green-100 border-green-300 text-green-800'
                            : 'bg-indigo-50 border-indigo-200 text-indigo-700 hover:bg-indigo-100'
                        }`}
                        style={{
                          // Rough duration mapping (e.g. "3 weeks" -> width)
                          width: node.duration.includes('week') ? `${parseInt(node.duration) * 40}px` : '120px'
                        }}
                        title={node.label}
                      >
                        <span className="truncate">{node.label}</span>
                      </div>
                    )
                  })}
                  
                </div>
              </div>
            )
          })}
        </div>
        
        {/* Milestones overlay (simplified text render below tracks) */}
        <div className="mt-12 ml-48 border-t border-gray-200 pt-6">
           <h4 className="text-sm font-bold text-gray-500 mb-4 uppercase tracking-wider">Target Milestones</h4>
           <div className="flex gap-4">
             {roadmap.milestones.map(m => (
                <div key={m.id} className="bg-white border-2 border-blue-400 p-3 rounded-lg shadow-sm">
                  <div className="text-blue-500 font-bold text-xl mb-1">◆</div>
                  <div className="font-bold text-sm text-gray-800">{m.label}</div>
                  <div className="text-xs text-gray-500">Target: Week {m.at_week}</div>
                </div>
             ))}
           </div>
        </div>

      </div>
    </div>
  );
}
