import { useState, useEffect, useCallback } from "react";
import { useBuilderStore } from "../../stores/useBuilderStore";
import { useResumeStore } from "../../stores/resumeStore";
import api from "../../lib/api";
import { builderApi } from "../../lib/builderApi";
import type { TemplateResponse } from "../../lib/builderApi";
import { useNavigate } from "react-router-dom";
import DynamicResumePreview from "../../components/builder/DynamicResumePreview";

export default function BuilderPage() {
  const [templates, setTemplates] = useState<TemplateResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [isRefining, setIsRefining] = useState<string | null>(null);
  
  // Accordion state for left panel
  const [activeAccordion, setActiveAccordion] = useState<'templates' | 'design' | 'content'>('templates');

  const { activeResume } = useResumeStore();
  const builderStore = useBuilderStore();
  const navigate = useNavigate();

  const saveCurrentDraft = useCallback(async () => {
    if (!activeResume?.id) return;
    try {
      const state = useBuilderStore.getState();
      const state_json = { 
        layoutType: state.layoutType, 
        columnRatio: state.columnRatio, 
        typography: state.typography, 
        colors: state.colors, 
        dividers: state.dividers, 
        bulletStyle: state.bulletStyle, 
        dateFormat: state.dateFormat, 
        sections: state.sections, 
        content: state.content, 
        selectedTemplate: state.selectedTemplate 
      };
      await builderApi.saveDraft(activeResume.id, state_json);
    } catch (err) {
      console.error("Failed to save draft:", err);
    }
  }, [activeResume]);

  useEffect(() => {
    if (!activeResume?.id) {
      navigate('/dashboard');
      return;
    }

    const fetchData = async () => {
      try {
        setIsLoading(true);
        // Load templates first
        const tpls = await builderApi.getTemplates();
        setTemplates(tpls);

        // Try to load an existing draft
        let draft = null;
        try {
          draft = await builderApi.getDraft(activeResume.id);
        } catch (e: any) {
          if (e.response?.status !== 404 && e.status !== 404) {
            console.warn("Draft fetch failed:", e);
          }
        }
        
        const store = useBuilderStore.getState();
        
        if (draft && draft.state_json) {
          // Hydrate from draft
          store.restoreState(draft.state_json);
          // Ensure a template is selected if we have one in state, else pick first
          if (!draft.state_json.selectedTemplate && tpls.length > 0) {
            store.setTemplate(tpls[0].template_schema);
          }
        } else {
          // No draft exists, load standardized resume data
          const res = await api.get(`/analysis/${activeResume.id}`);
          const standard = res.data.standardized_resume;

          if (standard) {
            store.updateContent('personalInfo', {
              name: standard.name || '',
              title: standard.role || '',
              email: standard.contact_info?.email || '',
              phone: standard.contact_info?.phone || '',
              links: standard.contact_info?.links || [],
              location: standard.contact_info?.location || '',
            });
            store.updateContent('summary', standard.professional_summary || '');
            store.updateContent('experience', standard.experience || []);
            store.updateContent('education', standard.education || []);
            store.updateContent('projects', standard.projects || []);
            store.updateContent('skills', standard.skills || []);
            store.updateContent('certifications', standard.certifications || []);
            
            if (tpls.length > 0) {
              store.setTemplate(tpls[0].template_schema);
            }
            
            // Auto-save the initial draft
            await saveCurrentDraft();
          }
        }
      } catch (err) {
        console.error("Failed to load builder data:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [activeResume, navigate, saveCurrentDraft]);

  const handleRefine = async (section: string, text: string) => {
    setIsRefining(section);
    try {
      const res = await builderApi.refineContent(section, text);
      const store = useBuilderStore.getState();
      if (section === 'Summary') {
        store.updateContent('summary', res.refined_text);
      } else {
        alert(`Refined ${section}:\n\n${res.refined_text}`);
      }
      await saveCurrentDraft();
    } catch (err) {
      console.error("Refinement failed:", err);
    } finally {
      setIsRefining(null);
    }
  };

  const handleDownloadPdf = async () => {
    const el = document.getElementById('resume-preview');
    if (!el) return;
    setIsExporting(true);
    try {
      const html = el.outerHTML;
      const fullHtml = `
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8">
            <style>
              body { font-family: 'Inter', sans-serif; padding: 0; margin: 0; background: white; }
              * { box-sizing: border-box; }
              .mb-1 { margin-bottom: 0.25rem; }
              .mb-2 { margin-bottom: 0.5rem; }
              .mb-3 { margin-bottom: 0.75rem; }
              .mb-4 { margin-bottom: 1rem; }
              .mb-6 { margin-bottom: 1.5rem; }
              .pb-1 { padding-bottom: 0.25rem; }
              .mt-1 { margin-top: 0.25rem; }
              .flex { display: flex; }
              .justify-between { justify-content: space-between; }
              .items-start { align-items: flex-start; }
              .gap-2 { gap: 0.5rem; }
              .gap-4 { gap: 1rem; }
              .block { display: block; }
              .whitespace-pre-line { white-space: pre-line; }
              .font-bold { font-weight: 700; }
              .text-sm { font-size: 0.875rem; }
              .px-2 { padding-left: 0.5rem; padding-right: 0.5rem; }
              .py-1 { padding-top: 0.25rem; padding-bottom: 0.25rem; }
              .rounded { border-radius: 0.25rem; }
              .flex-wrap { flex-wrap: wrap; }
            </style>
          </head>
          <body>
            ${html}
          </body>
        </html>
      `;
      const blob = await builderApi.exportPdf(fullHtml);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${content.personalInfo.name?.replace(/\s+/g, '_') || 'resume'}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("PDF Export failed", err);
      alert("Failed to export PDF.");
    } finally {
      setIsExporting(false);
    }
  };

  const handleTemplateSelect = (schema: any) => {
    builderStore.setTemplate(schema);
    saveCurrentDraft();
  };

  if (isLoading) {
    return <div className="flex justify-center items-center h-[calc(100vh-64px)]">Loading builder data...</div>;
  }

  const { content, selectedTemplate } = builderStore;

  const AccordionHeader = ({ id, title }: { id: typeof activeAccordion, title: string }) => (
    <button 
      onClick={() => setActiveAccordion(id)}
      className={`w-full flex justify-between items-center px-6 py-4 font-display font-bold text-lg border-b border-border transition-colors ${activeAccordion === id ? 'bg-cream text-accent' : 'bg-surface text-text-primary hover:bg-cream'}`}
    >
      <span>{title}</span>
      <span className="text-xl">{activeAccordion === id ? '−' : '+'}</span>
    </button>
  );

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col bg-cream overflow-hidden">
      
      {/* Top Bar */}
      <div className="flex-none bg-surface border-b border-border px-8 py-4 flex justify-between items-center z-10 shadow-sm">
        <h2 className="font-display text-xl text-text-primary font-bold">Resume Builder</h2>
        <button 
          onClick={handleDownloadPdf}
          disabled={isExporting || !selectedTemplate}
          className="px-6 py-2 rounded-lg font-bold text-sm text-white bg-accent hover:bg-accent/90 shadow-sm disabled:opacity-50"
        >
          {isExporting ? 'Exporting...' : 'Download PDF'}
        </button>
      </div>

      {/* Builder Body */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left Panel - Controls */}
        <div className="w-[420px] flex-none bg-surface border-r border-border flex flex-col z-10 shadow-lg overflow-y-auto">
          
          {/* Templates Section */}
          <div className="border-b border-border">
            <AccordionHeader id="templates" title="1. Choose Template" />
            {activeAccordion === 'templates' && (
              <div className="p-6 bg-surface grid grid-cols-2 gap-4">
                {templates.length === 0 ? (
                  <p className="text-xs text-text-secondary italic col-span-2">No templates available.</p>
                ) : (
                  templates.map((t) => (
                    <div 
                      key={t.id} 
                      onClick={() => handleTemplateSelect(t.template_schema)}
                      className={`aspect-[1/1.4] bg-cream border rounded-xl cursor-pointer flex flex-col items-center justify-center p-3 text-center transition-all ${
                        selectedTemplate?.name === t.name || JSON.stringify(selectedTemplate) === JSON.stringify(t.template_schema)
                          ? 'border-accent ring-2 ring-accent-soft shadow-md' 
                          : 'border-border hover:border-text-secondary'
                      }`}
                    >
                      <span className="text-sm font-bold text-text-primary">{t.name}</span>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          {/* Design Section */}
          <div className="border-b border-border">
            <AccordionHeader id="design" title="2. Design & Layout" />
            {activeAccordion === 'design' && (
              <div className="p-6 bg-surface space-y-6">
                {selectedTemplate ? (
                  <>
                    {/* Font Dropdown */}
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-bold text-text-primary uppercase">Font</label>
                      <select 
                        className="bg-cream border border-border text-sm p-1.5 rounded w-48"
                        value={selectedTemplate.typography?.body?.font_family || 'Inter'}
                        onChange={(e) => {
                          const newTemplate = JSON.parse(JSON.stringify(selectedTemplate));
                          const font = e.target.value;
                          if (newTemplate.typography.h1) newTemplate.typography.h1.font_family = font;
                          if (newTemplate.typography.h2) newTemplate.typography.h2.font_family = font;
                          if (newTemplate.typography.body) newTemplate.typography.body.font_family = font;
                          builderStore.setTemplate(newTemplate);
                        }}
                      >
                        <option value="Inter">Inter</option>
                        <option value="Poppins">Poppins</option>
                        <option value="Arial">Arial</option>
                        <option value="Georgia">Georgia</option>
                        <option value="Roboto">Roboto</option>
                        <option value="Outfit">Outfit</option>
                      </select>
                    </div>

                    {/* Line Height */}
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-bold text-text-primary uppercase w-1/3">Line Height</label>
                      <div className="flex items-center w-2/3 gap-3">
                        <span className="text-xs text-text-secondary w-10 text-right">{Math.round((selectedTemplate.typography?.body?.line_height || 1.5) * 100)}%</span>
                        <input 
                          type="range" min="1" max="2.5" step="0.1"
                          value={selectedTemplate.typography?.body?.line_height || 1.5}
                          onChange={(e) => {
                            const newTemplate = JSON.parse(JSON.stringify(selectedTemplate));
                            if (!newTemplate.typography.body) newTemplate.typography.body = {};
                            newTemplate.typography.body.line_height = parseFloat(e.target.value);
                            builderStore.setTemplate(newTemplate);
                          }}
                          className="flex-1 accent-accent"
                        />
                      </div>
                    </div>

                    {/* List Line Height */}
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-bold text-text-primary uppercase w-1/3">List Line Height</label>
                      <div className="flex items-center w-2/3 gap-3">
                        <span className="text-xs text-text-secondary w-10 text-right">{Math.round((selectedTemplate.visual_elements?.list_line_height || 1.2) * 100)}%</span>
                        <input 
                          type="range" min="1" max="2.5" step="0.1"
                          value={selectedTemplate.visual_elements?.list_line_height || 1.2}
                          onChange={(e) => {
                            const newTemplate = JSON.parse(JSON.stringify(selectedTemplate));
                            if (!newTemplate.visual_elements) newTemplate.visual_elements = {};
                            newTemplate.visual_elements.list_line_height = parseFloat(e.target.value);
                            builderStore.setTemplate(newTemplate);
                          }}
                          className="flex-1 accent-accent"
                        />
                      </div>
                    </div>

                    {/* Accent Color Preset Row */}
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-bold text-text-primary uppercase">Accent Color</label>
                      <div className="flex items-center gap-1.5 flex-wrap justify-end">
                        {['#000000', '#6B7280', '#0D9488', '#B45309', '#EF4444', '#991B1B', '#3B82F6', '#1D4ED8', '#F97316'].map(color => (
                          <button
                            key={color}
                            className={`w-6 h-6 rounded-full border border-border shadow-sm hover:scale-110 transition-transform ${selectedTemplate.color_palette?.primary === color ? 'ring-2 ring-accent ring-offset-1' : ''}`}
                            style={{ backgroundColor: color }}
                            onClick={() => {
                              const newTemplate = JSON.parse(JSON.stringify(selectedTemplate));
                              newTemplate.color_palette.primary = color;
                              builderStore.setTemplate(newTemplate);
                            }}
                          />
                        ))}
                        {/* Custom Color Picker */}
                        <label className="w-6 h-6 rounded-full cursor-pointer overflow-hidden border border-border shadow-sm flex items-center justify-center hover:scale-110 transition-transform relative" style={{background: 'linear-gradient(135deg, red, yellow, green, blue, purple)'}}>
                          <input 
                            type="color" 
                            className="absolute opacity-0 w-full h-full cursor-pointer"
                            value={selectedTemplate.color_palette?.primary || '#000000'}
                            onChange={(e) => {
                              const newTemplate = JSON.parse(JSON.stringify(selectedTemplate));
                              newTemplate.color_palette.primary = e.target.value;
                              builderStore.setTemplate(newTemplate);
                            }}
                          />
                        </label>
                      </div>
                    </div>

                    {/* Date Format */}
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-bold text-text-primary uppercase">Date Format</label>
                      <select 
                        className="bg-cream border border-border text-sm p-1.5 rounded w-48"
                        value={builderStore.dateFormat}
                        onChange={(e) => builderStore.updateContent('dateFormat' as any, e.target.value)}
                      >
                        <option value="MM/YYYY">Numbers (MM/YYYY)</option>
                        <option value="Month YYYY">Letters (Month, YYYY)</option>
                        <option value="YYYY">Year Only</option>
                        <option value="Hidden">Hidden</option>
                      </select>
                    </div>

                    <hr className="border-border my-4" />

                    {/* Alignments & Layouts Section */}
                    <div>
                      <h4 className="text-sm font-bold text-[#0D9488] mb-4 flex items-center gap-2">
                        <span>v</span> Alignments & Layouts
                      </h4>

                      {/* Header Alignment */}
                      <div className="mb-6">
                        <label className="text-xs font-bold text-text-primary uppercase mb-2 block">Header Alignment</label>
                        <div className="flex gap-2">
                          {['left', 'center', 'right'].map(align => (
                            <button
                              key={align}
                              onClick={() => {
                                const newTemplate = JSON.parse(JSON.stringify(selectedTemplate));
                                if (!newTemplate.layout) newTemplate.layout = {};
                                newTemplate.layout.header_alignment = align;
                                builderStore.setTemplate(newTemplate);
                              }}
                              className={`flex-1 border p-2 rounded flex flex-col items-center ${selectedTemplate.layout?.header_alignment === align ? 'border-accent bg-accent-soft ring-1 ring-accent' : 'border-border bg-white hover:bg-cream'}`}
                            >
                              {/* Visual Indicator of alignment */}
                              <div className={`w-full h-8 flex flex-col justify-center ${align === 'center' ? 'items-center' : align === 'right' ? 'items-end' : 'items-start'}`}>
                                <div className="w-1/2 h-1.5 bg-text-primary rounded mb-1"></div>
                                <div className="w-1/3 h-1 bg-text-secondary rounded"></div>
                              </div>
                              <span className="text-[10px] capitalize font-bold text-text-secondary mt-1">{align}</span>
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Date Alignment */}
                      <div>
                        <label className="text-xs font-bold text-text-primary uppercase mb-2 block">Date Alignment</label>
                        <div className="flex gap-2">
                          {['left', 'right'].map(align => (
                            <button
                              key={align}
                              onClick={() => {
                                const newTemplate = JSON.parse(JSON.stringify(selectedTemplate));
                                if (!newTemplate.layout) newTemplate.layout = {};
                                newTemplate.layout.date_alignment = align;
                                builderStore.setTemplate(newTemplate);
                              }}
                              className={`flex-1 border p-2 rounded flex flex-col ${selectedTemplate.layout?.date_alignment === align ? 'border-accent bg-accent-soft ring-1 ring-accent' : 'border-border bg-white hover:bg-cream'}`}
                            >
                              <div className={`w-full flex ${align === 'right' ? 'justify-between' : 'justify-start gap-4'} mb-1`}>
                                <div className="w-1/3 h-1.5 bg-text-primary rounded"></div>
                                <div className="w-1/4 h-1.5 bg-text-secondary rounded"></div>
                              </div>
                              <div className="w-1/3 h-1 bg-text-secondary rounded"></div>
                              <div className="text-[10px] capitalize font-bold text-text-secondary mt-1 mt-auto">{align}</div>
                            </button>
                          ))}
                        </div>
                      </div>

                    </div>
                  </>
                ) : (
                  <p className="text-xs text-text-secondary italic">Select a template first to edit its design.</p>
                )}
              </div>
            )}
          </div>

          {/* Content Section */}
          <div className="border-b border-border">
            <AccordionHeader id="content" title="3. Adjust Content" />
            {activeAccordion === 'content' && (
              <div className="p-6 bg-surface space-y-4">
                <p className="text-sm text-text-secondary mb-4">Edit your resume content or use AI to refine your statements.</p>
                
                {["Summary", "Experience", "Education", "Projects", "Skills"].map(section => (
                  <div key={section} className="p-4 border border-border rounded-xl bg-cream group">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-bold text-text-primary">{section}</span>
                      <button 
                        onClick={() => handleRefine(section, JSON.stringify(content[section.toLowerCase() as keyof typeof content]))}
                        disabled={isRefining === section}
                        className="text-xs font-bold text-accent bg-accent-soft px-3 py-1 rounded-full transition-opacity hover:opacity-80 disabled:opacity-50"
                      >
                        {isRefining === section ? 'Refining...' : 'Refine ✨'}
                      </button>
                    </div>
                    {section === 'Summary' ? (
                       <textarea 
                         value={content.summary}
                         onChange={(e) => builderStore.updateContent('summary', e.target.value)}
                         className="w-full text-sm p-2 border border-border rounded-md bg-white resize-none"
                         rows={4}
                       />
                    ) : (
                      <div className="text-xs text-text-secondary line-clamp-2">
                         {`${(content[section.toLowerCase() as keyof typeof content] as any[])?.length || 0} entries connected from analysis`}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Panel - Live Preview */}
        <div className="flex-1 bg-[#e5e7eb] flex justify-center py-12 overflow-y-auto">
           <DynamicResumePreview />
        </div>
      </div>
    </div>
  );
}
