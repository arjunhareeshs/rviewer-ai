export type ResumeStatus = 'uploaded' | 'extracting' | 'embedding' | 'completed' | 'failed';

export interface Resume {
  id: string;
  userId: string;
  filename: string;
  filePath: string;
  fileType: 'pdf' | 'image';
  status: ResumeStatus;
  extraction_method?: string;
  rawText?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ResumeSection {
  id: string;
  section_label: string;
  content: string;
  section_order: number;
  metadata?: Record<string, any>;
}

export interface UploadResponse {
  id: string;
  filename: string;
  file_type: string;
  status: string;
  extraction_method?: string;
  created_at: string;
  message: string;
  resume: Resume; // Add this since hooks expect response.data.resume
}

export interface ContactInfo {
  email?: string;
  phone?: string;
  links?: string[];
  location?: string;
}

export interface ExperienceEntry {
  company?: string;
  role?: string;
  dates?: string;
  description?: string;
}

export interface EducationEntry {
  institution?: string;
  degree?: string;
  dates?: string;
  metrics?: string;
}

export interface ProjectEntry {
  name?: string;
  description?: string;
  technologies?: string[];
}

