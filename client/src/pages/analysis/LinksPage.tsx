import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useResumeData } from '../../hooks/useResumeData';
import { HeatmapCalendar, LeetCodeChart, GitHubTopRepos } from '../../components/analysis/ProfileComponents';

export default function LinksPage() {
  const [searchParams] = useSearchParams();
  const resumeId = searchParams.get('id');
  const { data, loading, error } = useResumeData(resumeId);

  if (loading) return <div className="p-8 text-text-muted">Loading digital footprint analysis...</div>;
  if (error) return <div className="p-8 text-danger">{error}</div>;
  if (!data) return <div className="p-8 text-text-muted">No footprint data found. Please upload a resume first.</div>;

  const linkAnalysis = data.link_analysis || {};
  const presenceScore = linkAnalysis.overall_presence_score || 0;
  const platforms = linkAnalysis.platforms || [];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }} 
      animate={{ opacity: 1, y: 0 }} 
      className="p-8 max-w-[1200px] mx-auto space-y-8"
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-surface p-8 rounded-3xl border border-border shadow-sm">
        <div>
          <h1 className="font-display text-4xl text-text-primary tracking-tight">External Identity</h1>
          <p className="text-text-secondary text-lg mt-1 font-medium">Digital footprint analysis across platforms.</p>
        </div>
        <div className="flex items-center gap-4 bg-cream p-4 rounded-2xl border border-border">
          <div className="text-right">
            <span className="text-xs font-bold text-text-muted uppercase tracking-wider block">Presence Score</span>
            <span className="text-sm font-semibold text-text-secondary">Footprint Score: {presenceScore}/100</span>
          </div>
          <div className="w-16 h-16 rounded-full border-4 border-accent flex items-center justify-center font-mono font-bold text-xl text-accent">
            {presenceScore}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-8">
        {platforms.map((p: any, idx: number) => {
          const metrics = p.metrics || {};
          const activity = p.activity_data || {};
          
          return (
            <motion.div 
              key={idx}
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: idx * 0.1 }}
              className="bg-surface p-6 rounded-2xl border border-border shadow-sm flex flex-col justify-between overflow-hidden"
            >
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="font-bold text-text-primary uppercase tracking-widest text-sm flex items-center gap-2">
                    {p.platform === 'GitHub' && <span>🐙</span>}
                    {p.platform === 'LeetCode' && <span>💻</span>}
                    {p.platform === 'LinkedIn' && <span>💼</span>}
                    {p.platform} Profile
                  </h2>
                  <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${p.valid_link ? 'bg-success/15 text-success' : 'bg-danger/15 text-danger'}`}>
                    {p.valid_link ? 'Connected' : 'Not Found'}
                  </span>
                </div>

                {!p.valid_link ? (
                  <div className="bg-cream/50 p-6 rounded-xl border border-border text-center">
                    <p className="text-text-secondary text-sm">
                      We couldn't find your {p.platform} link. Add it to your resume to unlock these analytics!
                    </p>
                  </div>
                ) : (
                  <>
                    <div className="flex items-center gap-4 mb-6">
                      <div className="w-12 h-12 bg-accent-soft rounded-full flex items-center justify-center font-bold text-xl text-accent">
                        {p.username?.[0]?.toUpperCase() || p.platform[0]}
                      </div>
                      <div>
                        <p className="font-bold text-text-primary text-lg">{p.username}</p>
                        {metrics.bio && <p className="text-text-secondary text-xs truncate max-w-md">{metrics.bio}</p>}
                      </div>
                    </div>

                    {/* Platform Specific Rendering */}
                    {p.platform === 'GitHub' && (
                      <div className="space-y-6">
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                          <StatCard title="Public Repos" value={metrics.public_repos} />
                          <StatCard title="Followers" value={metrics.followers} />
                          <StatCard title="Total Stars" value={metrics.total_stars} />
                          <StatCard title="Total Forks" value={metrics.total_forks} />
                        </div>
                        <GitHubTopRepos repos={metrics.top_repos} />
                        <HeatmapCalendar data={activity} username={p.username} />
                      </div>
                    )}

                    {p.platform === 'LeetCode' && (
                      <div className="space-y-6">
                        <div className="grid grid-cols-2 gap-4">
                          <StatCard title="Global Ranking" value={metrics.ranking as string | number} />
                          <StatCard title="Total Solved" value={Number(Object.values(metrics.problems_solved || {}).reduce((a: any, b: any) => a + b, 0))} />
                        </div>
                        <LeetCodeChart problems={metrics.problems_solved || {}} />
                        <HeatmapCalendar data={activity} username={p.username} />
                      </div>
                    )}

                    {p.platform === 'LinkedIn' && (
                      <div className="space-y-6">
                        <div className="grid grid-cols-1 gap-4">
                          <StatCard title="Profile ID" value={metrics.profile_id as string | number} />
                        </div>
                      </div>
                    )}

                    {/* Generic Fallback for other platforms */}
                    {p.platform !== 'GitHub' && p.platform !== 'LeetCode' && p.platform !== 'LinkedIn' && Object.keys(metrics).length > 0 && (
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-4">
                        {Object.entries(metrics).map(([key, val]: [string, any]) => (
                          <StatCard key={key} title={key.replace('_', ' ')} value={typeof val === 'object' ? JSON.stringify(val) : String(val)} />
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>

              {p.valid_link && p.username && (
                <a 
                  href={getProfileUrl(p.platform, p.username)}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-6 text-sm font-bold text-accent hover:underline flex items-center gap-1 self-start"
                >
                  View Full Profile ↗
                </a>
              )}
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}

// --- Helper Components & Functions ---

const StatCard = ({ title, value }: { title: string, value: string | number }) => (
  <div className="bg-cream p-4 rounded-xl border border-border">
    <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider block mb-1">
      {title}
    </span>
    <span className="text-xl font-display font-semibold text-text-primary block truncate">
      {value}
    </span>
  </div>
);

const getProfileUrl = (platform: string, username: string) => {
  switch(platform.toLowerCase()) {
    case 'github': return `https://github.com/${username}`;
    case 'leetcode': return `https://leetcode.com/${username}`;
    case 'linkedin': return `https://linkedin.com/in/${username}`;
    default: return '#';
  }
};

