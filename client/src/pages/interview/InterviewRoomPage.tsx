import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { LiveKitRoom } from '@livekit/components-react';
import { getInterviewToken } from '../../lib/interviewApi';
import { useAuthStore } from '../../stores/authStore';
import InterviewRoomInner from './InterviewRoomInner';
import { Loader2, AlertCircle } from 'lucide-react';

export default function InterviewRoomPage() {
  const navigate = useNavigate();
  const { roomId } = useParams<{ roomId: string }>();
  const { user } = useAuthStore();
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const livekitUrl = import.meta.env.VITE_LIVEKIT_URL || 'ws://localhost:7880';

  useEffect(() => {
    if (!roomId) return;
    
    const fetchToken = async () => {
      try {
        const candidateName = user?.name || "Candidate";
        const data = await getInterviewToken(roomId, candidateName);
        setToken(data.token);
      } catch (err: any) {
        console.error("Failed to load interview room token:", err);
        setError(err.message || "Failed to retrieve connection credentials. Check if backend is running.");
      } finally {
        setLoading(false);
      }
    };

    fetchToken();
  }, [roomId, user]);

  if (loading) {
    return (
      <div className="fixed inset-0 z-[100] bg-[#0D0D0F] text-white flex flex-col items-center justify-center gap-4">
        <Loader2 className="animate-spin text-[#38BDF8]" size={36} />
        <div className="text-center">
          <p className="text-lg font-bold text-white/90">Establishing Secure Connection</p>
          <p className="text-sm text-white/40">Fetching room credentials...</p>
        </div>
      </div>
    );
  }

  if (error || !token) {
    return (
      <div className="fixed inset-0 z-[100] bg-[#0D0D0F] text-white flex flex-col items-center justify-center p-6">
        <div className="bg-white/5 border border-white/10 p-8 rounded-2xl max-w-md text-center space-y-6 shadow-2xl">
          <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center text-red-500 mx-auto border border-red-500/20">
            <AlertCircle size={28} />
          </div>
          <div className="space-y-2">
            <h2 className="text-xl font-bold">Connection Failed</h2>
            <p className="text-sm text-white/55 leading-relaxed">
              {error || "Could not retrieve the security token to join the interview room."}
            </p>
          </div>
          <div className="flex gap-4">
            <button 
              onClick={() => window.location.reload()} 
              className="flex-grow py-3 bg-white/10 hover:bg-white/15 text-white text-sm font-bold rounded-xl border border-white/10 transition-colors"
            >
              Retry Connection
            </button>
            <button 
              onClick={() => navigate('/workspace/interview')} 
              className="flex-grow py-3 bg-red-500 hover:bg-red-500/90 text-white text-sm font-bold rounded-xl shadow-md transition-colors"
            >
              Exit Interview
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <LiveKitRoom
      token={token}
      serverUrl={livekitUrl}
      connect={true}
      audio={true}
      video={false}
      onDisconnected={() => {
        navigate('/workspace/interview');
      }}
    >
      <InterviewRoomInner />
    </LiveKitRoom>
  );
}
