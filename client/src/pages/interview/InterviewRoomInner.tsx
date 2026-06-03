import { useEffect, useState, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Scissors, Volume2, Mic } from 'lucide-react';
import { RoomAudioRenderer, useLocalParticipant, useParticipants } from '@livekit/components-react';
import { endInterview } from '../../lib/interviewApi';

export default function InterviewRoomInner() {
  const navigate = useNavigate();
  const { roomId } = useParams<{ roomId: string }>();
  const [secondsLeft, setSecondsLeft] = useState(600); // 10 minutes

  const { localParticipant } = useLocalParticipant();
  const remoteParticipants = useParticipants();
  
  const isUserSpeaking = localParticipant?.isSpeaking ?? false;
  const isAgentSpeaking = remoteParticipants.some(p => p.isSpeaking);

  const [wasUserSpeakingRecently, setWasUserSpeakingRecently] = useState(false);

  const handleEnd = useCallback(async () => {
    if (roomId) {
      try {
        await endInterview(roomId);
      } catch (err) {
        console.error("Failed to end interview:", err);
      }
      navigate(`/workspace/interview/${roomId}/report`);
    } else {
      navigate('/workspace/interview');
    }
  }, [roomId, navigate]);

  useEffect(() => {
    // Hide default light background from WorkspaceLayout, force dark mode for this route
    document.body.style.backgroundColor = '#0D0D0F';
    return () => {
      document.body.style.backgroundColor = '';
    };
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          setTimeout(handleEnd, 0); // avoid state update in render
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [handleEnd]);

  // Track user speech to show "Thinking" state right after candidate stops speaking
  useEffect(() => {
    const delay = isUserSpeaking ? 0 : 3000;
    const timer = setTimeout(() => {
      setWasUserSpeakingRecently(isUserSpeaking);
    }, delay);
    return () => clearTimeout(timer);
  }, [isUserSpeaking]);

  const formatTime = (totalSeconds: number) => {
    const m = Math.floor(totalSeconds / 60);
    const s = totalSeconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  // Determine agent status
  let agentStatus: 'Speaking' | 'Listening' | 'Thinking' | 'Waiting' = 'Waiting';
  if (isAgentSpeaking) {
    agentStatus = 'Speaking';
  } else if (isUserSpeaking) {
    agentStatus = 'Listening';
  } else if (wasUserSpeakingRecently) {
    agentStatus = 'Thinking';
  }

  // Waveform animation duration
  const getWaveformDuration = (index: number) => {
    if (isAgentSpeaking) {
      return 0.3 + (index % 5) * 0.08;
    } else if (isUserSpeaking) {
      return 0.5 + (index % 5) * 0.12;
    } else {
      return 1.8 + (index % 5) * 0.25;
    }
  };

  return (
    <div className="fixed inset-0 z-[100] bg-[#0D0D0F] text-white flex flex-col font-sans select-none">
      {/* LiveKit Audio playback for browsers */}
      <RoomAudioRenderer />

      {/* Top Bar */}
      <div className="flex justify-between items-start p-8">
        <div>
          <div className="text-[#38BDF8] text-xs font-bold uppercase tracking-[0.2em] mb-1">
            Interview Session
          </div>
          <div className="text-xl font-bold text-white flex items-center gap-2">
            <span>AI Interviewer</span>
            <span className="w-1.5 h-1.5 rounded-full bg-[#38BDF8] animate-ping"></span>
          </div>
        </div>
        
        <div className="flex flex-col items-end gap-3">
          <div className="flex items-center gap-4 bg-white/5 backdrop-blur-md px-4 py-2 rounded-full border border-white/10 shadow-[0_4px_30px_rgba(0,0,0,0.5)]">
            <div className="flex items-center gap-2 text-white/80">
              <span className="text-xs">⏱</span>
              <span className="font-mono font-bold text-sm tracking-wider">{formatTime(secondsLeft)}</span>
            </div>
            <div className="w-px h-4 bg-white/20"></div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#10B981] shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-pulse"></span>
              <span className="text-[10px] font-bold uppercase tracking-wider text-white/80">Connected</span>
            </div>
          </div>
          
          {/* Status Indicators */}
          <div className="flex flex-col items-end gap-2 pr-2 bg-white/5 p-3.5 rounded-2xl border border-white/5 shadow-inner">
            {([
              { key: 'Speaking', color: 'bg-[#38BDF8] shadow-[0_0_10px_rgba(56,189,248,0.8)]' },
              { key: 'Listening', color: 'bg-[#10B981] shadow-[0_0_10px_rgba(16,185,129,0.8)]' },
              { key: 'Thinking', color: 'bg-[#F59E0B] shadow-[0_0_10px_rgba(245,158,11,0.8)] animate-pulse' },
              { key: 'Waiting', color: 'bg-white/30 animate-pulse' }
            ] as const).map((stat) => (
              <div key={stat.key} className="flex items-center gap-2.5">
                <span className={`text-[10px] uppercase font-bold tracking-wider transition-all duration-300 ${
                  agentStatus === stat.key ? 'text-white' : 'text-white/30'
                }`}>
                  {stat.key}
                </span>
                <span className={`w-2 h-2 rounded-full transition-all duration-300 ${
                  agentStatus === stat.key ? stat.color : 'bg-white/20'
                }`}></span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content / Waveform Area */}
      <div className="flex-1 flex flex-col items-center justify-center relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[500px] bg-[#38BDF8]/5 opacity-[0.05] blur-[150px] rounded-full pointer-events-none"></div>
        
        {/* Dynamic Waveform Visualizer */}
        <div className="w-full max-w-2xl h-40 flex items-center justify-center gap-1.5 mb-12 px-4">
          {Array.from({ length: 40 }).map((_, i) => {
            const distFromCenter = Math.abs(20 - i);
            const baseHeight = 45 - distFromCenter * 1.6;
            const maxMultiplier = isAgentSpeaking ? 1.7 : isUserSpeaking ? 1.2 : 0.35;
            const heightVal = Math.max(6, baseHeight * maxMultiplier);
            return (
              <motion.div
                key={i}
                animate={{ 
                  height: [heightVal * 0.6, heightVal * 1.35, heightVal * 0.6] 
                }}
                transition={{ 
                  duration: getWaveformDuration(i), 
                  repeat: Infinity, 
                  ease: "easeInOut" 
                }}
                className={`w-1.5 rounded-full transition-colors duration-500 ${
                  isAgentSpeaking 
                    ? 'bg-[#38BDF8] shadow-[0_0_12px_rgba(56,189,248,0.5)]' 
                    : isUserSpeaking 
                      ? 'bg-[#10B981] shadow-[0_0_12px_rgba(16,185,129,0.5)]' 
                      : 'bg-white/20'
                }`}
                style={{ opacity: 1 - distFromCenter * 0.04 }}
              />
            );
          })}
        </div>

        {/* Dynamic Speech & VAD / Noise Cancellation Badges */}
        <div className="flex gap-4 items-center justify-center mb-8">
          <div className={`flex items-center gap-2 px-4 py-1.5 rounded-full border text-xs font-bold transition-all duration-300 ${
            isUserSpeaking 
              ? 'bg-[#10B981]/10 border-[#10B981]/30 text-[#10B981] shadow-[0_0_15px_rgba(16,185,129,0.15)]' 
              : 'bg-white/5 border-white/10 text-white/40'
          }`}>
            <Mic size={12} className={isUserSpeaking ? 'animate-bounce' : ''} />
            <span>VAD: {isUserSpeaking ? 'Speech Detected' : 'Silent'}</span>
          </div>

          <div className="flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-white/80 text-xs font-bold shadow-md">
            <Volume2 size={12} className="text-[#38BDF8]" />
            <span>Noise Cancellation: Active</span>
          </div>
        </div>

        <div className="text-center space-y-2 relative z-10">
          <h3 className={`text-xl font-bold tracking-wide transition-colors duration-300 ${
            isAgentSpeaking ? 'text-[#38BDF8]' : isUserSpeaking ? 'text-[#10B981]' : 'text-white/60'
          }`}>
            {isAgentSpeaking ? 'Interviewer Speaking' : isUserSpeaking ? 'Listening to You...' : wasUserSpeakingRecently ? 'Thinking...' : 'Waiting for Input'}
          </h3>
          <p className="text-white/40 text-sm">
            {isAgentSpeaking ? 'AI is explaining the details' : isUserSpeaking ? 'Your speech is being transcribed' : wasUserSpeakingRecently ? 'Processing your response...' : 'Say something to respond'}
          </p>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="p-8 flex justify-center items-center gap-6">
        <button 
          onClick={handleEnd}
          className="flex items-center gap-2 px-8 py-3 rounded-full border border-red-500/50 text-red-500 font-bold text-sm hover:bg-red-500/10 hover:border-red-500 transition-all duration-300 shadow-[0_4px_20px_rgba(239,68,68,0.1)] hover:-translate-y-0.5"
        >
          <Scissors size={16} />
          End Interview
        </button>
      </div>
    </div>
  );
}
