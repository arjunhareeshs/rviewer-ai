import { create } from 'zustand';
import type { ContactInfo, ExperienceEntry, EducationEntry, ProjectEntry } from '../types/resume';

// Types representing the entire builder state
export type LayoutType = 'single_column' | 'two_column_sidebar_left' | 'two_column_sidebar_right' | 'two_column_equal';

export interface TypographySettings {
  primary_font: string;
  section_title_size: number;
  body_size: number;
  name_size: number;
  line_height: number;
  list_line_height: number;
}

export interface ColorSettings {
  accent: string;
  sidebar_bg: string;
  header_bg: string;
}

export interface SectionDef {
  id: string;
  name: string;
  column: 'left' | 'right' | 'full';
  heading_style: 'uppercase' | 'titlecase';
  heading_underline: boolean;
  item_layout: 'stacked' | 'inline_date_right';
  has_bullets: boolean;
}

export interface TemplateSpec {
  id?: string;
  name?: string;
  color_palette: { primary: string; secondary: string; background: string; text: string; };
  typography: { h1: any; h2: any; body: any; };
  layout: { columns: number; column_ratio: string; margins: any; header_alignment?: string; date_alignment?: string; };
  sections_layout: { main_column: string[]; sidebar_column: string[]; };
  visual_elements: any;
}

export interface BuilderState {
  // Global Design State
  layoutType: LayoutType;
  columnRatio: [number, number];
  typography: TypographySettings;
  colors: ColorSettings;
  dividers: 'line' | 'space' | 'none' | 'dot' | 'dash';
  bulletStyle: 'dot' | 'dash' | 'chevron' | 'arrow' | 'none';
  dateFormat: string;
  
  // Active Template Spec
  selectedTemplate: TemplateSpec | null;

  // Section Ordering
  sections: SectionDef[];
  
  // Content State (populated from extraction)
  content: {
    personalInfo: ContactInfo & { name?: string; title?: string };
    summary: string;
    experience: ExperienceEntry[];
    education: EducationEntry[];
    projects: ProjectEntry[];
    skills: string[];
    certifications: string[];
  };

  // Actions
  setLayoutType: (layout: LayoutType) => void;
  updateTypography: (updates: Partial<TypographySettings>) => void;
  updateColors: (updates: Partial<ColorSettings>) => void;
  setBulletStyle: (style: BuilderState['bulletStyle']) => void;
  reorderSections: (newSections: SectionDef[]) => void;
  updateContent: <K extends keyof BuilderState['content']>(key: K, data: BuilderState['content'][K]) => void;
  restoreState: (state: Partial<BuilderState>) => void;
  setTemplate: (template: TemplateSpec) => void;
}

export const useBuilderStore = create<BuilderState>((set) => ({
  selectedTemplate: null,
  layoutType: 'two_column_sidebar_left',
  columnRatio: [0.35, 0.65],
  
  typography: {
    primary_font: 'Inter',
    section_title_size: 11,
    body_size: 10,
    name_size: 24,
    line_height: 1.2,
    list_line_height: 1.2,
  },
  
  colors: {
    accent: '#3b82f6', // blue-500
    sidebar_bg: '#f8fafc',
    header_bg: 'none',
  },
  
  dividers: 'line',
  bulletStyle: 'dot',
  dateFormat: 'MM/YYYY',
  
  sections: [
    { id: 'contacts', name: 'Contacts', column: 'left', heading_style: 'uppercase', heading_underline: true, item_layout: 'stacked', has_bullets: false },
    { id: 'skills', name: 'Skills', column: 'left', heading_style: 'uppercase', heading_underline: true, item_layout: 'stacked', has_bullets: true },
    { id: 'summary', name: 'Summary', column: 'right', heading_style: 'uppercase', heading_underline: true, item_layout: 'stacked', has_bullets: false },
    { id: 'experience', name: 'Experience', column: 'right', heading_style: 'uppercase', heading_underline: true, item_layout: 'inline_date_right', has_bullets: true },
    { id: 'education', name: 'Education', column: 'right', heading_style: 'uppercase', heading_underline: true, item_layout: 'inline_date_right', has_bullets: false },
    { id: 'projects', name: 'Projects', column: 'right', heading_style: 'uppercase', heading_underline: true, item_layout: 'inline_date_right', has_bullets: true },
  ],
  
  content: {
    personalInfo: { name: '', title: '', email: '', phone: '', location: '' },
    summary: '',
    experience: [],
    education: [],
    projects: [],
    skills: [],
    certifications: [],
  },

  setLayoutType: (layout) => set({ layoutType: layout }),
  updateTypography: (updates) => set((state) => ({ typography: { ...state.typography, ...updates } })),
  updateColors: (updates) => set((state) => ({ colors: { ...state.colors, ...updates } })),
  setBulletStyle: (style) => set({ bulletStyle: style }),
  reorderSections: (newSections) => set({ sections: newSections }),
  updateContent: (key, data) => set((state) => ({ content: { ...state.content, [key]: data } })),
  restoreState: (state) => set((prev) => ({ ...prev, ...state })),
  setTemplate: (template) => set({ selectedTemplate: template }),
}));
