import api from './api';


export interface TemplateResponse {
  id: string;
  name: string;
  description: string;
  is_premium: boolean;
  template_schema: any;
}

export interface DraftResponse {
  id: string;
  resume_id: string;
  template_id?: string;
  state_json: any;
}

export const builderApi = {
  getTemplates: async (): Promise<TemplateResponse[]> => {
    const response = await api.get('/builder/templates');
    return response.data;
  },

  getDraft: async (resumeId: string): Promise<DraftResponse | null> => {
    try {
      const response = await api.get(`/builder/draft/${resumeId}`);
      return response.data;
    } catch (err: any) {
      if (err.response?.status === 404) return null;
      throw err;
    }
  },

  saveDraft: async (resumeId: string, state_json: any, templateId?: string): Promise<DraftResponse> => {
    const response = await api.post('/builder/draft', {
      resume_id: resumeId,
      template_id: templateId,
      state_json,
    });
    return response.data;
  },

  refineContent: async (section: string, raw_text: string, context?: string): Promise<{ refined_text: string }> => {
    const response = await api.post('/builder/refine', {
      section,
      raw_text,
      context,
    });
    return response.data;
  },

  exportPdf: async (html_content: string): Promise<Blob> => {
    const response = await api.post(
      '/builder/export-pdf',
      { html_content },
      { responseType: 'blob' }
    );
    return response.data;
  },
};
