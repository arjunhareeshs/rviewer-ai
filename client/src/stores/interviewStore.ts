import { create } from 'zustand';
import type { InterviewPhase, EvaluationScore } from '@/types/interview';

interface InterviewState {
  roomName: string | null;
  candidateName: string;
  token: string | null;
  phase: InterviewPhase;
  isConnected: boolean;
  isInterviewActive: boolean;
  reportReady: boolean;
  evaluationData: EvaluationScore | null;
  
  setRoomDetails: (roomName: string, token: string, candidateName: string) => void;
  setConnected: (status: boolean) => void;
  updatePhase: (phase: InterviewPhase) => void;
  endInterview: () => void;
  setReportReady: (status: boolean) => void;
  reset: () => void;
}

export const useInterviewStore = create<InterviewState>((set) => ({
  roomName: null,
  candidateName: 'Candidate',
  token: null,
  phase: 'introduction',
  isConnected: false,
  isInterviewActive: false,
  reportReady: false,
  evaluationData: null,

  setRoomDetails: (roomName, token, candidateName) => set({ roomName, token, candidateName, isInterviewActive: true }),
  setConnected: (isConnected) => set({ isConnected }),
  updatePhase: (phase) => set({ phase }),
  endInterview: () => set({ isInterviewActive: false, isConnected: false }),
  setReportReady: (reportReady) => set({ reportReady }),
  reset: () => set({
    roomName: null,
    candidateName: 'Candidate',
    token: null,
    phase: 'introduction',
    isConnected: false,
    isInterviewActive: false,
    reportReady: false,
    evaluationData: null,
  })
}));
