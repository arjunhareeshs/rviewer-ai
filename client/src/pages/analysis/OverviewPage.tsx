import { useSearchParams } from 'react-router-dom';
import { RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import { motion } from 'framer-motion';
import { useResumeData } from '../../hooks/useResumeData';
import { useAuthStore } from '../../stores/authStore';

export default function OverviewPage() {
  const [searchParams] = useSearchParams();
  const resumeId = searchParams.get('id');
  const { data, loading, error } = useResumeData(resumeId);
  const { user } = useAuthStore();

  if (loading) return <div className="p-6 text-text-muted">Loading intelligence report...</div>;
  if (error) return <div className="p-6 text-danger">{error}</div>;
  if (!data) return <div className="p-6 text-text-muted">No analysis data found. Please upload a resume first.</div>;

  const atsResult = data.ats_result || {};
  const overallScore = data.overall_score || 0;
  const atsScore = data.ats_score || 0;

  const atsBreakdown = (atsResult.criteria_scores || []).map((c: any) => ({
    criteria: c.name,
    score: c.score,
  }));

  const roles = (data.role_recommendations?.recommendations || []).slice(0, 3).map((r: any) => ({
    title: r.role_name || r.role || 'Recommended Role',
    match: r.match_percentage || r.match_score || 0,
  }));

  const strengths = (atsResult.criteria_scores || [])
    .filter((c: any) => c.passed)
    .map((c: any) => `${c.name}: ${c.details}`);

  const weaknesses = (atsResult.gaps || []).map((g: any) => `${g.criterion}: ${g.description}`);

  const summary = data.role_recommendations?.overall_summary || '';

  const parsedResume = data.standardized_resume || {};
  const experience = parsedResume.experience || [];
  const educationList = parsedResume.education || [];
  const projectList = parsedResume.projects || [];
  const skillsList = parsedResume.skills || [];
  const profileSummary = parsedResume.professional_summary;

  // Dynamic bar chart height: 32px per item, min 80px
  const barChartHeight = Math.max(80, atsBreakdown.length * 32);

  const radialData = [{ name: 'Score', value: overallScore, fill: 'var(--accent)' }];

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="p-5 max-w-[1400px] mx-auto space-y-5"
    >
      {/* Header */}
      <div>
        <h1 className="font-display text-3xl text-text-primary tracking-tight">
          Welcome back, {user?.name?.split(' ')[0] || 'User'}
        </h1>
        <p className="text-text-secondary text-sm mt-0.5 font-medium">Here's your resume intelligence report.</p>
      </div>

      {/* Top row: Scores left + Resume content right */}
      <div className="flex flex-col lg:flex-row gap-5">

        {/* Left Column — Score cards */}
        <div className="w-full lg:w-[340px] flex-none space-y-4">

          {/* Overall Score */}
          <motion.div whileHover={{ scale: 1.01 }} className="bg-surface rounded-2xl p-5 shadow-sm border border-border text-center">
            <h2 className="font-bold text-text-primary uppercase tracking-widest text-[10px] mb-3">Overall Score</h2>
            <div className="h-36 relative flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <RadialBarChart cx="50%" cy="50%" innerRadius="68%" outerRadius="100%" barSize={16} data={radialData} startAngle={90} endAngle={-270}>
                  <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
                  <RadialBar background dataKey="value" cornerRadius={8} />
                </RadialBarChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="font-mono text-4xl font-bold text-text-primary">{overallScore}</span>
                <span className="font-mono text-xs text-text-muted">/100</span>
              </div>
            </div>
          </motion.div>

          {/* ATS Score bar chart */}
          <motion.div whileHover={{ scale: 1.01 }} className="bg-surface rounded-2xl p-5 shadow-sm border border-border">
            <div className="flex justify-between items-center mb-3">
              <h2 className="font-bold text-text-primary uppercase tracking-widest text-[10px]">ATS Score</h2>
              <span className="font-mono font-bold text-lg text-text-primary">{atsScore}/100</span>
            </div>
            {atsBreakdown.length > 0 ? (
              <div style={{ height: barChartHeight }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={atsBreakdown} layout="vertical" margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                    <XAxis type="number" domain={[0, 100]} hide />
                    <YAxis dataKey="criteria" type="category" axisLine={false} tickLine={false} width={120} tick={{ fill: 'var(--text-muted)', fontSize: 9, fontWeight: 600 }} />
                    <Tooltip cursor={{ fill: 'var(--accent-soft)' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                    <Bar dataKey="score" fill="var(--accent)" radius={[0, 4, 4, 0]} barSize={10} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="text-xs text-text-muted">No ATS breakdown available.</p>
            )}
          </motion.div>

          {/* Role Recommendations — moved to left column so right isn't sparse */}
          {roles.length > 0 && (
            <motion.div whileHover={{ scale: 1.01 }} className="bg-surface rounded-2xl p-5 shadow-sm border border-border">
              <h2 className="font-bold text-text-primary uppercase tracking-widest text-[10px] mb-3">Role Recommendations</h2>
              <div className="space-y-2">
                {roles.map((r: any, idx: number) => (
                  <div key={idx} className="flex justify-between items-center p-2.5 rounded-lg border border-border hover:border-accent transition-colors bg-cream">
                    <span className="font-bold text-text-primary text-xs">{r.title}</span>
                    <span className="font-mono font-bold text-accent bg-accent-soft px-2 py-0.5 rounded text-xs">{r.match}%</span>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </div>

        {/* Right Column — Resume sections */}
        <div className="flex-1 space-y-4">

          {/* Professional Summary */}
          {profileSummary && (
            <motion.div whileHover={{ scale: 1.01 }} className="bg-surface rounded-2xl p-5 shadow-sm border border-border">
              <h2 className="font-bold text-text-primary uppercase tracking-widest text-[10px] mb-2">Professional Summary</h2>
              <p className="text-text-secondary text-sm leading-relaxed">{profileSummary}</p>
            </motion.div>
          )}

          {/* Experience + Education side by side */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">

            {/* Experience */}
            {experience.length > 0 && (
              <motion.div whileHover={{ scale: 1.01 }} className="bg-surface rounded-2xl p-5 shadow-sm border border-border">
                <h2 className="font-bold text-text-primary uppercase tracking-widest text-[10px] mb-3">Work Experience</h2>
                <div className="space-y-2.5">
                  {experience.map((exp: any, i: number) => (
                    <div key={i} className="p-3 bg-cream rounded-xl border border-border">
                      <div className="flex justify-between items-start gap-2">
                        <div className="min-w-0">
                          <h3 className="font-bold text-text-primary text-xs truncate">{exp.role}</h3>
                          <p className="font-medium text-text-secondary text-[11px]">{exp.company}</p>
                        </div>
                        {exp.dates && (
                          <span className="text-[10px] font-bold text-text-muted bg-surface px-2 py-0.5 rounded border border-border whitespace-nowrap flex-shrink-0">{exp.dates}</span>
                        )}
                      </div>
                      {exp.description && (
                        <p className="text-text-secondary text-[11px] mt-1.5 line-clamp-2">{exp.description}</p>
                      )}
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Education */}
            {educationList.length > 0 && (
              <motion.div whileHover={{ scale: 1.01 }} className="bg-surface rounded-2xl p-5 shadow-sm border border-border">
                <h2 className="font-bold text-text-primary uppercase tracking-widest text-[10px] mb-3">Education</h2>
                <div className="space-y-2.5">
                  {educationList.map((edu: any, i: number) => (
                    <div key={i} className="p-3 bg-cream rounded-xl border border-border">
                      <h3 className="font-bold text-text-primary text-xs">{edu.degree}</h3>
                      <p className="font-medium text-text-secondary text-[11px]">{edu.institution}</p>
                      <div className="flex items-center gap-2 mt-1.5">
                        {edu.dates && (
                          <span className="text-[10px] font-bold text-text-muted bg-surface px-2 py-0.5 rounded border border-border">{edu.dates}</span>
                        )}
                        {edu.metrics && (
                          <span className="text-[10px] font-bold text-accent bg-accent-soft px-2 py-0.5 rounded">{edu.metrics}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </div>

          {/* Projects */}
          {projectList.length > 0 && (
            <motion.div whileHover={{ scale: 1.01 }} className="bg-surface rounded-2xl p-5 shadow-sm border border-border">
              <h2 className="font-bold text-text-primary uppercase tracking-widest text-[10px] mb-3">Projects</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {projectList.map((proj: any, i: number) => (
                  <div key={i} className="p-3 bg-cream rounded-xl border border-border">
                    <h3 className="font-bold text-text-primary text-xs mb-1">{proj.name}</h3>
                    {proj.description && (
                      <p className="text-text-secondary text-[11px] mb-2 line-clamp-2">{proj.description}</p>
                    )}
                    <div className="flex flex-wrap gap-1">
                      {(proj.technologies || []).slice(0, 4).map((tech: string, j: number) => (
                        <span key={j} className="text-[10px] font-bold text-text-secondary bg-surface px-1.5 py-0.5 rounded border border-border">{tech}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Skills */}
          {skillsList.length > 0 && (
            <motion.div whileHover={{ scale: 1.01 }} className="bg-surface rounded-2xl p-5 shadow-sm border border-border">
              <h2 className="font-bold text-text-primary uppercase tracking-widest text-[10px] mb-3">Top Skills</h2>
              <div className="flex flex-wrap gap-1.5">
                {skillsList.map((s: string) => (
                  <span key={s} className="px-2.5 py-1 bg-cream border border-border rounded-lg text-xs font-semibold text-text-primary">{s}</span>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      {(strengths.length > 0 || weaknesses.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {strengths.length > 0 && (
            <motion.div whileHover={{ scale: 1.01 }} className="bg-accent-soft rounded-2xl p-5 border border-accent/20">
              <h2 className="font-bold text-text-primary mb-3 flex items-center gap-2 text-sm">✅ Strengths</h2>
              <ul className="space-y-1.5">
                {strengths.map((s: string, i: number) => (
                  <li key={i} className="flex gap-2 text-text-primary font-medium text-xs"><span className="text-accent mt-0.5">•</span> {s}</li>
                ))}
              </ul>
            </motion.div>
          )}
          {weaknesses.length > 0 && (
            <motion.div whileHover={{ scale: 1.01 }} className="bg-danger-soft rounded-2xl p-5 border border-danger/20">
              <h2 className="font-bold text-danger mb-3 flex items-center gap-2 text-sm">⚠️ Areas to Improve</h2>
              <ul className="space-y-1.5">
                {weaknesses.map((w: string, i: number) => (
                  <li key={i} className="flex gap-2 text-danger font-medium text-xs"><span className="text-danger mt-0.5">•</span> {w}</li>
                ))}
              </ul>
            </motion.div>
          )}
        </div>
      )}

      {/* AI Summary */}
      {summary && (
        <motion.div whileHover={{ scale: 1.01 }} className="bg-surface rounded-2xl p-5 border border-border shadow-sm">
          <h2 className="font-bold text-text-primary uppercase tracking-widest text-[10px] mb-2">AI Executive Summary</h2>
          <p className="text-base leading-relaxed text-text-secondary font-medium">{summary}</p>
        </motion.div>
      )}
    </motion.div>
  );
}
