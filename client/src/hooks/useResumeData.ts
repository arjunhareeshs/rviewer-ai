import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/lib/api';
import { useResumeStore } from '@/stores/resumeStore';

export interface AnalysisData {
  resume_id: string;
  ats_score: number;
  ats_result: any;
  role_recommendations: any;
  project_analysis: any;
  link_analysis: any;
  overall_score: number;
  standardized_resume?: any;
}

export function useResumeData(urlResumeId: string | null) {
  const { activeResume } = useResumeStore();
  const resumeId = urlResumeId || activeResume?.id;

  const [data, setData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!resumeId) return;

    const fetchAnalysis = async () => {
      setLoading(true);
      try {
        const res = await api.get(`/analysis/${resumeId}`);
        setData(res.data);
        setError(null);
      } catch (err: any) {
        if (err.response?.status === 404) {
          // If the analysis doesn't exist (e.g., DB reset), redirect to upload
          navigate('/upload', { replace: true });
        } else {
          setError(err.response?.data?.detail || err.message || 'Failed to fetch analysis data');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [resumeId, navigate]);

  return { data, loading, error };
}
