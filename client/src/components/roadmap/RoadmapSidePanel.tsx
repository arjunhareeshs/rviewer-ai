import { useRoadmapStore } from "@/stores/useRoadmapStore";

export default function RoadmapSidePanel() {
  const { selectedNode, setSelectedNode, progress, toggleNodeCompletion } = useRoadmapStore();

  if (!selectedNode) return null;

  const isCompleted = !!progress[selectedNode.id];

  const renderResources = (type: string, title: string, icon: string) => {
    const resources = (selectedNode.resources as Record<string, Array<{url: string, title: string, snippet: string}>>)?.[type];
    if (!resources || resources.length === 0) return null;

    return (
      <div className="mb-6">
        <h4 className="text-sm font-bold text-gray-700 dark:text-gray-300 flex items-center gap-2 mb-3">
          <span className="text-lg">{icon}</span> {title}
        </h4>
        <div className="space-y-3">
          {resources.map((res: {url: string, title: string, snippet: string}, idx: number) => (
            <a 
              key={idx} 
              href={res.url} 
              target="_blank" 
              rel="noreferrer"
              className="block p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-indigo-400 dark:hover:border-indigo-500 transition-colors group"
            >
              <h5 className="font-semibold text-indigo-600 dark:text-indigo-400 text-sm group-hover:underline line-clamp-1">{res.title}</h5>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">{res.snippet}</p>
              <span className="text-[10px] text-gray-400 mt-2 block uppercase tracking-wider">{new URL(res.url).hostname}</span>
            </a>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="w-[400px] h-full bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-700 flex flex-col shadow-2xl z-20 absolute right-0 top-0 overflow-y-auto">
      {/* Header */}
      <div className="p-5 border-b border-gray-200 dark:border-gray-700 flex justify-between items-start sticky top-0 bg-white/90 dark:bg-gray-900/90 backdrop-blur z-10">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded ${
              selectedNode.priority === 'critical' ? 'bg-red-100 text-red-700' :
              selectedNode.priority === 'high' ? 'bg-orange-100 text-orange-700' :
              selectedNode.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
              'bg-green-100 text-green-700'
            }`}>
              {selectedNode.priority} Priority
            </span>
            <span className="text-xs text-gray-500 font-medium">⏱️ {selectedNode.duration}</span>
          </div>
          <h2 className="text-xl font-extrabold text-gray-900 dark:text-white mt-2 leading-tight">
            {selectedNode.label}
          </h2>
        </div>
        <button 
          onClick={() => setSelectedNode(null)}
          className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full text-gray-400 hover:text-gray-600"
        >
          ✕
        </button>
      </div>

      {/* Action Bar */}
      <div className="p-5 bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-700">
        <label className="flex items-center gap-3 cursor-pointer">
          <input 
            type="checkbox" 
            className="w-5 h-5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
            checked={isCompleted}
            onChange={(e) => toggleNodeCompletion(selectedNode.id, e.target.checked)}
          />
          <span className={`font-semibold ${isCompleted ? 'text-green-600 line-through' : 'text-gray-700 dark:text-gray-200'}`}>
            {isCompleted ? "Marked as Complete!" : "Mark as Complete"}
          </span>
        </label>
      </div>

      {/* Resources */}
      <div className="p-5 flex-1">
        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-5">Curated Learning Resources</h3>
        
        {renderResources('course', 'Structured Courses', '🎓')}
        {renderResources('video', 'Video Tutorials', '▶️')}
        {renderResources('article', 'Articles & Guides', '📖')}
        {renderResources('practice', 'Hands-on Practice', '💻')}
        {renderResources('docs', 'Official Documentation', '📄')}
        {renderResources('github', 'Code Examples', '🐙')}
        
        {!selectedNode.resources && (
          <div className="text-center p-8 text-gray-400">
            <div className="animate-pulse flex flex-col items-center">
              <div className="w-8 h-8 border-4 border-gray-200 border-t-indigo-500 rounded-full animate-spin mb-4"></div>
              <p className="text-sm">Fetching fresh links...</p>
            </div>
          </div>
        )}
        {selectedNode.resources && Object.keys(selectedNode.resources).length === 0 && (
          <div className="text-center p-8 text-gray-500">
            <p className="text-sm">No specific external links found for this node.</p>
          </div>
        )}
      </div>
    </div>
  );
}
