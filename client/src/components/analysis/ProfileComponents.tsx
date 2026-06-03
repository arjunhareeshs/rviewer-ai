import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';

// --- Heatmap Calendar Component ---
export const HeatmapCalendar = ({ data, username }: { data: any, username: string }) => {
  // If data is from GitHub, we render an image directly (easiest/most reliable way)
  if (data?.heatmap_url) {
    return (
      <div className="mt-4 p-4 bg-surface border border-border rounded-xl">
        <h4 className="text-xs font-bold text-text-muted uppercase mb-4">Contribution Activity</h4>
        <div className="w-full overflow-x-auto">
          <img src={data.heatmap_url} alt={`${username}'s GitHub Activity`} className="min-w-[600px] h-auto object-contain" />
        </div>
      </div>
    );
  }

  // If data is LeetCode submissionCalendar
  if (data?.heatmap) {
    const calendarData = data.heatmap;
    const timestamps = Object.keys(calendarData).sort((a, b) => Number(a) - Number(b));
    
    if (timestamps.length === 0) return null;

    // We'll generate a simple block matrix for recent activity (last 30 active days max, or generic representation)
    const recentActivity = timestamps.slice(-60); // Last 60 active timestamps
    
    return (
      <div className="mt-4 p-4 bg-surface border border-border rounded-xl">
        <h4 className="text-xs font-bold text-text-muted uppercase mb-4">Recent Activity (Active Days)</h4>
        <div className="flex flex-wrap gap-1">
          {recentActivity.map(ts => {
            const count = calendarData[ts];
            const date = new Date(Number(ts) * 1000).toLocaleDateString();
            
            // Determine color intensity
            let bgColor = 'bg-accent/10';
            if (count > 0) bgColor = 'bg-accent/30';
            if (count > 2) bgColor = 'bg-accent/60';
            if (count > 5) bgColor = 'bg-accent/90';
            if (count > 10) bgColor = 'bg-accent';

            return (
              <motion.div 
                key={ts}
                whileHover={{ scale: 1.2 }}
                title={`${date}: ${count} submissions`}
                className={`w-3 h-3 rounded-sm ${bgColor} cursor-pointer`}
              />
            );
          })}
        </div>
      </div>
    );
  }

  return null;
};

// --- LeetCode Problem Chart ---
export const LeetCodeChart = ({ problems }: { problems: Record<string, number> }) => {
  const data = [
    { name: 'Easy', value: problems.Easy || 0, color: '#00b8a3' },
    { name: 'Medium', value: problems.Medium || 0, color: '#ffc01e' },
    { name: 'Hard', value: problems.Hard || 0, color: '#ef4743' },
  ].filter(item => item.value > 0);

  if (data.length === 0) return null;

  return (
    <div className="flex items-center gap-4 mt-4 p-4 bg-surface border border-border rounded-xl">
      <div className="w-32 h-32">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={30}
              outerRadius={50}
              paddingAngle={5}
              dataKey="value"
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="flex-1 grid grid-cols-1 gap-2">
        {data.map(item => (
          <div key={item.name} className="flex justify-between items-center text-sm">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
              <span className="font-semibold text-text-primary">{item.name}</span>
            </div>
            <span className="font-bold text-text-secondary">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// --- GitHub Top Repos List ---
export const GitHubTopRepos = ({ repos }: { repos: any[] }) => {
  if (!repos || repos.length === 0) return null;

  return (
    <div className="mt-4 flex flex-col gap-3">
      <h4 className="text-xs font-bold text-text-muted uppercase">Top Repositories</h4>
      {repos.map((repo, i) => (
        <a 
          key={i} 
          href={repo.url} 
          target="_blank" 
          rel="noreferrer"
          className="p-3 bg-surface border border-border rounded-xl hover:border-accent/40 transition-colors group block"
        >
          <div className="flex justify-between items-start">
            <h5 className="font-bold text-text-primary text-sm group-hover:text-accent transition-colors">{repo.name}</h5>
            <div className="flex items-center gap-1 text-xs font-bold text-text-secondary bg-cream px-2 py-0.5 rounded">
              <span>⭐</span> {repo.stars}
            </div>
          </div>
          {repo.description && (
            <p className="text-xs text-text-secondary mt-1 line-clamp-1">{repo.description}</p>
          )}
        </a>
      ))}
    </div>
  );
};
