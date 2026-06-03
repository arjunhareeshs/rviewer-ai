import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mic, ShieldAlert, FileText } from 'lucide-react';
import { useResumeStore } from '../../stores/resumeStore';
import { useAuthStore } from '../../stores/authStore';
import { startInterview } from '../../lib/interviewApi';

export default function InterviewLobbyPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { activeResume } = useResumeStore();
  const { user } = useAuthStore();

  const handleStart = async () => {
    setLoading(true);
    setError(null);
    const roomName = `room_${Math.random().toString(36).substring(2, 10)}`;
    const candidateName = user?.name || "Candidate";
    
    try {
      const res = await startInterview(roomName, candidateName, activeResume?.id || undefined);
      navigate(`/workspace/interview/${res.room_name}`);
    } catch (err: any) {
      console.error("Failed to start interview:", err);
      setError(err.message || "Could not connect to the interview server. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="font-display text-4xl text-text-primary tracking-tight">Technical Interview</h1>
        <p className="text-text-secondary text-lg mt-1 font-medium">Prepare for your 10-minute AI evaluation.</p>
      </div>

      <div className="bg-surface rounded-2xl p-8 border border-border shadow-sm flex flex-col items-center text-center">
        <div className="w-20 h-20 bg-accent-soft rounded-full flex items-center justify-center text-accent mb-6 animate-pulse">
          <Mic size={32} />
        </div>
        
        <h2 className="text-2xl font-bold text-text-primary mb-2">Mic Check</h2>
        <p className="text-text-secondary mb-6 max-w-md">Ensure you are in a quiet environment. The AI will assess your technical depth, communication, and problem-solving skills.</p>
        
        {activeResume ? (
          <div className="flex gap-3 items-center bg-accent-soft/30 text-accent px-5 py-2.5 rounded-xl border border-accent/20 mb-6 text-sm font-semibold">
            <FileText size={18} />
            <span>Using uploaded resume: {activeResume.filename}</span>
          </div>
        ) : (
          <div className="flex gap-3 items-center bg-warning-soft text-warning px-5 py-2.5 rounded-xl border border-warning/20 mb-6 text-sm font-semibold">
            <ShieldAlert size={18} />
            <span>No resume selected. Proceeding with standard questions.</span>
          </div>
        )}
        
        <div className="flex gap-4 items-center bg-cream px-6 py-3 rounded-xl border border-border mb-8 w-full max-w-md text-sm text-text-secondary text-left font-medium">
          <ShieldAlert className="text-warning flex-none" size={20} />
          <span>This session is recorded and analyzed. Speak clearly and answer naturally. The interview will automatically conclude after 10 minutes.</span>
        </div>
        
        {error && (
          <div className="mb-6 w-full max-w-md p-4 bg-danger-soft border border-danger text-danger rounded-xl text-sm font-medium text-left">
            {error}
          </div>
        )}

        <button 
          onClick={handleStart}
          disabled={loading}
          className="px-8 py-4 bg-accent text-white font-bold text-lg rounded-xl shadow-md hover:shadow-lg hover:-translate-y-0.5 hover:bg-accent/90 transition-all w-full max-w-md disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Connecting...' : 'Start Interview'}
        </button>
      </div>
    </div>
  );
}
