import api from './api';
import type { SessionStatus } from '@/types/interview';

export const startInterview = async (roomName: string, candidateName: string = "Candidate", resumeId?: string) => {
  const formData = new FormData();
  formData.append('room_name', roomName);
  formData.append('candidate_name', candidateName);
  if (resumeId) {
    formData.append('resume_id', resumeId);
  }
  // Unset Content-Type so axios auto-sets multipart/form-data with the correct boundary
  const response = await api.post('/interview/start', formData, {
    headers: { 'Content-Type': undefined },
  });
  return response.data;
};

export const uploadResumeForInterview = async (file: File, roomName: string, candidateName: string = "Candidate") => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('room_name', roomName);
  formData.append('candidate_name', candidateName);

  const response = await api.post('/interview/upload-resume', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getInterviewToken = async (roomName: string, candidateName: string = "Candidate") => {
  const response = await api.get('/interview/token', {
    params: { room_name: roomName, candidate_name: candidateName }
  });
  return response.data;
};

export const endInterview = async (roomName: string) => {
  const response = await api.post('/interview/end-interview', null, {
    params: { room_name: roomName }
  });
  return response.data;
};

export const getSessionStatus = async (roomName: string): Promise<SessionStatus> => {
  const response = await api.get(`/interview/session-status/${roomName}`);
  return response.data;
};

import { API_BASE_URL } from './constants';

export const downloadReport = (roomName: string) => {
  // Using direct URL for download to leverage browser's file handling
  const baseUrl = API_BASE_URL || 'http://localhost:8000';
  window.open(`${baseUrl}/api/v1/interview/download-report/${roomName}`, '_blank');
};
