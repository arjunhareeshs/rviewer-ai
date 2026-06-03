import { create } from 'zustand';

export interface RoadmapNode {
  id: string;
  label: string;
  type: 'skill' | 'project' | 'certification';
  priority: 'critical' | 'high' | 'medium' | 'low';
  duration: string;
  depends_on: string[];
  milestone: boolean;
  resources?: {
    article?: { title: string; url: string; snippet: string }[];
    video?: { title: string; url: string; snippet: string }[];
    course?: { title: string; url: string; snippet: string }[];
    practice?: { title: string; url: string; snippet: string }[];
    docs?: { title: string; url: string; snippet: string }[];
    github?: { title: string; url: string; snippet: string }[];
  };
}

export interface RoadmapTrack {
  track_id: string;
  track_name: string;
  color: string;
  nodes: RoadmapNode[];
}

export interface RoadmapMilestone {
  id: string;
  label: string;
  at_week: number;
  requires: string[];
}

export interface RoadmapData {
  candidate: string;
  target_role: string;
  total_duration: string;
  current_state: {
    label: string;
    strengths: string[];
    score: number;
  };
  tracks: RoadmapTrack[];
  milestones: RoadmapMilestone[];
}

export interface RoadmapState {
  roadmap: RoadmapData | null;
  progress: Record<string, boolean>; // node_id -> completed
  viewMode: 'mindmap' | 'timeline';
  trackMode: 'deep' | 'fast';
  selectedNode: RoadmapNode | null;
  
  setRoadmap: (data: RoadmapData) => void;
  setProgress: (progress: Record<string, boolean>) => void;
  toggleNodeCompletion: (nodeId: string, completed: boolean) => void;
  setViewMode: (mode: 'mindmap' | 'timeline') => void;
  setTrackMode: (mode: 'deep' | 'fast') => void;
  setSelectedNode: (node: RoadmapNode | null) => void;
}

export const useRoadmapStore = create<RoadmapState>((set) => ({
  roadmap: null,
  progress: {},
  viewMode: 'mindmap',
  trackMode: 'deep',
  selectedNode: null,

  setRoadmap: (data) => set({ roadmap: data }),
  setProgress: (progress) => set({ progress }),
  toggleNodeCompletion: (nodeId, completed) => 
    set((state) => ({ progress: { ...state.progress, [nodeId]: completed } })),
  setViewMode: (mode) => set({ viewMode: mode }),
  setTrackMode: (mode) => set({ trackMode: mode }),
  setSelectedNode: (node) => set({ selectedNode: node }),
}));
