import { create } from 'zustand';

export interface AdminFilters {
  skills?: string[];
  ats_score_min?: number | null;
  ats_score_max?: number | null;
  interview_score_min?: number | null;
  interview_completed?: boolean | null;
  role_match?: string | null;
  institutions?: string[];
  has_internship?: boolean | null;
  has_certifications?: boolean | null;
  sort_by: "overall_score" | "ats_score" | "interview_score" | "recent";
  sort_order: "asc" | "desc";
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export interface AdminState {
  activeFilters: AdminFilters;
  searchQuery: string;
  chatHistory: ChatMessage[];
  shortlistedIds: string[]; // Mocking local state for now
  
  setSearchQuery: (query: string) => void;
  setActiveFilters: (filters: Partial<AdminFilters>) => void;
  resetFilters: () => void;
  addChatMessage: (msg: Omit<ChatMessage, 'id'>) => void;
  clearChat: () => void;
  toggleShortlist: (id: string) => void;
}

const defaultFilters: AdminFilters = {
  sort_by: "overall_score",
  sort_order: "desc"
};

export const useAdminStore = create<AdminState>((set) => ({
  activeFilters: { ...defaultFilters },
  searchQuery: "",
  chatHistory: [
    { id: '1', role: 'assistant', content: 'Hello! I am your AI Filter Assistant. Describe the ideal candidate you are looking for.' }
  ],
  shortlistedIds: [],

  setSearchQuery: (query) => set({ searchQuery: query }),
  setActiveFilters: (filters) => set((state) => ({ 
    activeFilters: { ...state.activeFilters, ...filters } 
  })),
  resetFilters: () => set({ activeFilters: { ...defaultFilters }, searchQuery: "" }),
  addChatMessage: (msg) => set((state) => ({
    chatHistory: [...state.chatHistory, { ...msg, id: Date.now().toString() }]
  })),
  clearChat: () => set({ chatHistory: [
    { id: '1', role: 'assistant', content: 'Chat history cleared. How can I help you filter candidates?' }
  ]}),
  toggleShortlist: (id) => set((state) => {
    const exists = state.shortlistedIds.includes(id);
    return {
      shortlistedIds: exists 
        ? state.shortlistedIds.filter(i => i !== id) 
        : [...state.shortlistedIds, id]
    };
  })
}));
