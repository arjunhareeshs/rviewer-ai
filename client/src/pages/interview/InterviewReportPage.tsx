import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { Loader2, AlertCircle, CheckCircle, AlertTriangle, FileText, ArrowRight } from 'lucide-react';
import api from '../../lib/api';
import { downloadReport } from '../../lib/interviewApi';

interface EvaluationScore {
  answer_quality: number;
  technical_correctness: number;
  communication: number;
  problem_solving: number;
  attitude_confidence: number;
  overall_recommendation: number;
  feedback_details: Record<string, string>;
  summary: string;
  strengths: string[];
  areas_for_improvement: string[];
}

interface InterviewSession {
  room_name: string;
  candidate_name: string;
  start_time: string;
  end_time?: string;
  state: {
    phase: string;
    exchange_count: number;
    evaluation?: EvaluationScore;
  };
  report_pdf_path?: string;
}

export default function InterviewReportPage() {
  const { roomId } = useParams<{ roomId: string }>();
  const [loading, setLoading] = useState(true);
  const [pollingStatus, setPollingStatus] = useState('Checking report status...');
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!roomId) return;

    let isMounted = true;
    let pollInterval: any = null;

    const checkStatusAndFetch = async () => {
      try {
        // 1. Poll the session status first
        const statusRes = await api.get(`/interview/session-status/${roomId}`);
        const isReady = statusRes.data.report_ready;

        if (isReady) {
          clearInterval(pollInterval);
          // 2. Fetch full session details
          const sessionRes = await api.get(`/interview/session/${roomId}`);
          if (isMounted) {
            setSession(sessionRes.data);
            setLoading(false);
          }
        } else {
          if (isMounted) {
            setPollingStatus('AI is analyzing your answers & generating report...');
          }
        }
      } catch (err: any) {
        console.error("Error fetching report status:", err);
        // If it's a 404, the session might be a demo room or not found
        if (err.response?.status === 404) {
          clearInterval(pollInterval);
          if (isMounted) {
            setError("Session not found. Demo report is displayed as fallback.");
            setLoading(false);
          }
        } else {
          // Retry or handle other errors
          if (isMounted) {
            setPollingStatus('Retrying connection to evaluation service...');
          }
        }
      }
    };

    // Run immediately, then poll every 3 seconds
    checkStatusAndFetch();
    pollInterval = setInterval(checkStatusAndFetch, 3000);

    return () => {
      isMounted = false;
      clearInterval(pollInterval);
    };
  }, [roomId]);

  const handleDownload = () => {
    if (roomId) {
      downloadReport(roomId);
    }
  };

  // Fallback demo data if error or not found
  const demoEvaluation: EvaluationScore = {
    answer_quality: 7.5,
    technical_correctness: 7.1,
    communication: 8.5,
    problem_solving: 7.5,
    attitude_confidence: 6.8,
    overall_recommendation: 7.6,
    feedback_details: {},
    summary: "Solid overall performance during the interview. Articulated structural software development decisions well and maintained a highly professional demeanor. Scalability questions could use more depth.",
    strengths: [
      "Articulate and structured communication on standard programming topics.",
      "Clear explanation of project architectural layouts during introductory phase.",
      "Maintained professional composure and confidence throughout."
    ],
    areas_for_improvement: [
      "Struggled with system design depth, specifically caching strategies and horizontal scaling.",
      "Could elaborate more on specific performance optimizations and runtime complexity."
    ]
  };

  const hasRealData = session?.state?.evaluation;
  const evaluation = hasRealData ? session.state.evaluation! : demoEvaluation;

  // Format scores out of 100
  const getScorePercentage = (val: number) => {
    // If the model output a score <= 10, scale it to 100
    if (val <= 10) {
      return Math.round(val * 10);
    }
    return Math.round(val);
  };

  const finalScore = getScorePercentage(evaluation.overall_recommendation);

  const radarData = [
    { subject: 'Communication', A: getScorePercentage(evaluation.communication) },
    { subject: 'Technical Depth', A: getScorePercentage(evaluation.technical_correctness) },
    { subject: 'Problem Solving', A: getScorePercentage(evaluation.problem_solving) },
    { subject: 'Answer Quality', A: getScorePercentage(evaluation.answer_quality) },
    { subject: 'Confidence', A: getScorePercentage(evaluation.attitude_confidence) },
  ];

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 p-8 text-center">
        <Loader2 className="animate-spin text-accent" size={40} />
        <div className="space-y-1">
          <h2 className="text-xl font-bold text-text-primary">Generating Performance Report</h2>
          <p className="text-sm text-text-secondary max-w-sm">{pollingStatus}</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="p-8 max-w-[1200px] mx-auto space-y-8">
      {error && (
        <div className="flex items-center gap-3 bg-warning-soft text-warning px-5 py-3 rounded-xl border border-warning/20 text-sm font-semibold">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
        <div>
          <h1 className="font-display text-4xl text-text-primary tracking-tight">Interview Evaluation</h1>
          <p className="text-text-secondary text-lg mt-1 font-medium">
            Candidate: {session?.candidate_name || "Guest Candidate"}
          </p>
        </div>
        <Link to="/workspace/analysis/overview" className="px-6 py-2.5 bg-surface border border-border rounded-xl font-bold text-sm text-text-primary hover:bg-cream transition-all hover:scale-[1.02] shadow-sm flex items-center gap-2">
          <span>Back to Dashboard</span>
          <ArrowRight size={14} />
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column - Score & Radar */}
        <div className="space-y-8">
          <motion.div whileHover={{ scale: 1.01 }} className="bg-surface rounded-2xl p-8 border border-border shadow-sm text-center flex flex-col items-center justify-center">
             <h2 className="text-xs font-bold uppercase tracking-widest text-text-muted mb-4">Overall Score</h2>
             <div className={`w-32 h-32 rounded-full border-8 flex items-center justify-center shadow-lg transition-all ${
               finalScore >= 80 ? 'border-success shadow-success/10' : finalScore >= 60 ? 'border-accent shadow-accent/10' : 'border-danger shadow-danger/10'
             }`}>
               <span className="font-mono text-4xl font-bold text-text-primary">{finalScore}</span>
             </div>
             <p className="mt-4 font-bold text-text-primary">
               {finalScore >= 80 ? 'Exceptional Performance!' : finalScore >= 60 ? 'Solid Technical Baseline' : 'Requires Alignment'}
             </p>
          </motion.div>

          <motion.div whileHover={{ scale: 1.01 }} className="bg-surface rounded-2xl p-6 border border-border shadow-sm">
             <h2 className="text-xs font-bold uppercase tracking-widest text-text-primary mb-6">Dimension Analysis</h2>
             <div className="h-64">
               <ResponsiveContainer width="100%" height="100%">
                 <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
                   <PolarGrid stroke="var(--border)" />
                   <PolarAngleAxis dataKey="subject" tick={{fill: 'var(--text-muted)', fontSize: 11, fontWeight: 600}} />
                   <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                   <Radar dataKey="A" stroke="var(--accent)" fill="var(--accent)" fillOpacity={0.2} />
                 </RadarChart>
               </ResponsiveContainer>
             </div>
          </motion.div>
        </div>

        {/* Right Column - Breakdowns */}
        <div className="lg:col-span-2 space-y-8">
          
          <motion.div whileHover={{ scale: 1.01 }} className="bg-surface rounded-2xl p-8 border border-border shadow-sm">
             <h2 className="text-xs font-bold uppercase tracking-widest text-text-primary mb-4">Interviewer's Executive Summary</h2>
             <p className="text-text-secondary leading-relaxed text-sm font-medium">
               {evaluation.summary}
             </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <motion.div whileHover={{ scale: 1.01 }} className="bg-accent-soft rounded-2xl p-6 border border-accent/25 shadow-sm">
              <h2 className="font-bold text-text-primary mb-4 flex items-center gap-2">
                <CheckCircle size={18} className="text-success" />
                <span>Strengths Identified</span>
              </h2>
              <ul className="space-y-3">
                {evaluation.strengths?.map((str, idx) => (
                  <li key={idx} className="text-sm font-medium text-text-primary flex items-start gap-2.5">
                    <span className="text-success mt-0.5">•</span>
                    <span>{str}</span>
                  </li>
                )) || <span className="text-xs text-text-muted">None documented.</span>}
              </ul>
            </motion.div>
            
            <motion.div whileHover={{ scale: 1.01 }} className="bg-danger-soft rounded-2xl p-6 border border-danger/25 shadow-sm">
              <h2 className="font-bold text-danger mb-4 flex items-center gap-2">
                <AlertTriangle size={18} className="text-danger" />
                <span>Areas to Improve</span>
              </h2>
              <ul className="space-y-3">
                {evaluation.areas_for_improvement?.map((str, idx) => (
                  <li key={idx} className="text-sm font-medium text-danger flex items-start gap-2.5">
                    <span className="text-danger mt-0.5">•</span>
                    <span>{str}</span>
                  </li>
                )) || <span className="text-xs text-text-muted">None documented.</span>}
              </ul>
            </motion.div>
          </div>

          <button 
            onClick={handleDownload}
            disabled={!hasRealData}
            className="w-full py-4 bg-accent text-white font-bold text-lg rounded-xl hover:bg-accent/90 transition-all shadow-md mt-4 flex items-center justify-center gap-2.5 disabled:opacity-40 disabled:cursor-not-allowed hover:-translate-y-0.5 active:translate-y-0"
          >
            <FileText size={20} />
            <span>Download Full PDF Report</span>
          </button>
        </div>
      </div>
    </motion.div>
  );
}
