import { useSearchParams } from 'react-router-dom';
import { useResumeData } from '../../hooks/useResumeData';

export default function FullAnalysisPage() {
  const [searchParams] = useSearchParams();
  const resumeId = searchParams.get('id');
  const { data, loading, error } = useResumeData(resumeId);

  if (loading) return <div className="p-8 text-text-muted">Loading analysis...</div>;
  if (error) return <div className="p-8 text-danger">{error}</div>;
  if (!data) return <div className="p-8 text-text-muted">No analysis data found.</div>;

  const atsResult = data.ats_result || {};
  const criteriaScores = atsResult.criteria_scores || [];
  const gaps = atsResult.gaps || [];

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="bg-surface rounded-3xl p-8 shadow-sm border border-border mb-8 relative overflow-hidden">
        <div className="flex items-center justify-between relative z-10">
          <div>
            <h1 className="text-3xl font-display font-bold text-text-primary mb-2">ATS Compatibility Score</h1>
            <p className="text-text-secondary">How well applicant tracking systems can parse your resume.</p>
          </div>
          <div className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-br from-accent to-blue-400">
            {data.ats_score || 0}<span className="text-2xl text-text-muted">/100</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h2 className="text-xl font-bold text-text-primary mb-4">Criteria Breakdown</h2>
          <div className="space-y-4">
            {criteriaScores.map((c: any, i: number) => (
              <div key={i} className="bg-surface p-5 rounded-2xl border border-border shadow-sm flex items-start gap-4 hover:border-accent/30 transition-colors">
                <div className={`p-3 rounded-full ${c.passed ? 'bg-success/10 text-success' : 'bg-danger-soft text-danger'}`}>
                  {c.passed ? (
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                  ) : (
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                  )}
                </div>
                <div>
                  <h3 className="font-semibold text-text-primary">{c.name}</h3>
                  <p className="text-sm text-text-secondary mt-1">{c.details}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-xl font-bold text-text-primary mb-4">Critical Gaps & Fixes</h2>
          <div className="space-y-4">
            {gaps.map((g: any, i: number) => (
              <div key={i} className="bg-danger-soft p-6 rounded-2xl border border-danger/20">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-2 py-1 rounded text-xs font-bold uppercase tracking-wider ${
                    g.severity === 'critical' ? 'bg-danger text-white' :
                    g.severity === 'major' ? 'bg-orange-500 text-white' :
                    'bg-warning/20 text-warning'
                  }`}>
                    {g.severity}
                  </span>
                  <h3 className="font-bold text-text-primary">{g.criterion}</h3>
                </div>
                <p className="text-text-primary font-medium text-sm mb-3">{g.description}</p>
                <div className="bg-white/60 p-3 rounded-xl border border-white/40">
                  <p className="text-sm font-medium text-text-primary"><span className="mr-2">💡</span>{g.recommendation}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
