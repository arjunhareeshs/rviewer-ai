import { useState } from 'react';
import api from '@/lib/api';
import { useResumeStore } from '@/stores/resumeStore';
import type { Resume, UploadResponse } from '@/types/resume';

export function useResume() {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const { setActiveResume, setSections } = useResumeStore();

  const uploadResume = async (file: File) => {
    setIsUploading(true);
    setError(null);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post<UploadResponse>('/resumes/upload', formData, {
        headers: {
          'Content-Type': undefined, // Let axios auto-set multipart/form-data with correct boundary
        },
      });
      
      let currentResume = response.data as unknown as Resume;
      setActiveResume(currentResume);
      setUploadProgress(20); // Initial uploaded state
      
      // Poll until the backend background task is complete
      let retries = 0;
      while (currentResume.status !== 'completed' && currentResume.status !== 'failed') {
        if (retries > 150) { // 5 minutes max (150 * 2s)
           throw new Error("Analysis pipeline timed out. The server might be overloaded or encountering an issue.");
        }
        await new Promise(resolve => setTimeout(resolve, 2000)); // Poll every 2s
        retries++;
        
        try {
          const pollResponse = await api.get<Resume>(`/resumes/${currentResume.id}`);
          currentResume = pollResponse.data;
          setActiveResume(currentResume);
          
          // Map backend status to progress bar
          if (currentResume.status === 'extracting') setUploadProgress(50);
          else if (currentResume.status === 'embedding') setUploadProgress(80);
          else if (currentResume.status === 'completed') setUploadProgress(100);
        } catch (pollErr) {
          console.error("Error polling resume status:", pollErr);
          // Continue polling despite temporary network errors
        }
      }

      if (currentResume.status === 'failed') {
        throw new Error("Analysis pipeline failed. Please check the file and try again.");
      }
      
      return currentResume;
    } catch (err: any) {
      setError(err.message || 'Failed to upload resume');
      throw err;
    } finally {
      setIsUploading(false);
    }
  };

  const pollResumeStatus = async (resumeId: string) => {
    try {
      const response = await api.get<Resume>(`/resumes/${resumeId}`);
      setActiveResume(response.data);
      return response.data;
    } catch (err: any) {
      setError(err.message || 'Failed to fetch resume status');
      throw err;
    }
  };

  const fetchSections = async (resumeId: string) => {
    try {
      const response = await api.get(`/resumes/${resumeId}/sections`);
      setSections(response.data.sections);
      return response.data.sections;
    } catch (err: any) {
      setError(err.message || 'Failed to fetch resume sections');
      throw err;
    }
  };

  return {
    uploadResume,
    pollResumeStatus,
    fetchSections,
    isUploading,
    uploadProgress,
    error,
  };
}
