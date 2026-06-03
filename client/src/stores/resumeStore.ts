import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { Resume, ResumeSection } from '@/types/resume';

interface ResumeState {
  activeResume: Resume | null;
  sections: ResumeSection[];
  setActiveResume: (resume: Resume | null) => void;
  setSections: (sections: ResumeSection[]) => void;
  clearActiveResume: () => void;
}

export const useResumeStore = create<ResumeState>()(
  persist(
    (set) => ({
      activeResume: null,
      sections: [],
      setActiveResume: (resume) => set({ activeResume: resume }),
      setSections: (sections) => set({ sections }),
      clearActiveResume: () => set({ activeResume: null, sections: [] }),
    }),
    {
      name: 'resume-storage', // key in sessionStorage
      storage: createJSONStorage(() => sessionStorage),
    }
  )
);
