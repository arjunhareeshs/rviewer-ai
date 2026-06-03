
import { useBuilderStore } from '../../stores/useBuilderStore';

export default function DynamicResumePreview() {
  const { content, selectedTemplate, dateFormat } = useBuilderStore();

  if (!selectedTemplate) {
    return (
      <div className="flex items-center justify-center h-full text-text-secondary italic">
        Select a template from the left panel to preview your resume.
      </div>
    );
  }

  const { color_palette, typography, layout, sections_layout, visual_elements } = selectedTemplate;
  const isMultiColumn = layout?.columns > 1;

  // Convert "70:30" to gridTemplateColumns: "7fr 3fr"
  const getGridTemplateColumns = () => {
    if (!isMultiColumn || !layout?.column_ratio) return "1fr";
    const [left, right] = layout.column_ratio.split(':');
    return `${left}fr ${right}fr`;
  };

  const dividerColor = visual_elements?.dividers?.present ? (visual_elements?.dividers?.color || color_palette?.primary) : 'transparent';
  const dividerThickness = visual_elements?.dividers?.thickness || '1px';

  const renderSection = (key: string) => {
    switch (key) {
      case 'personalInfo':
        return (
          <div key={key} className="mb-6" style={{ textAlign: (layout?.header_alignment as any) || 'left' }}>
            <h1 className="mb-2" style={{ 
              fontFamily: typography?.h1?.font_family, 
              fontSize: `${typography?.h1?.size_pt || 24}pt`, 
              fontWeight: typography?.h1?.weight, 
              textTransform: typography?.h1?.text_transform as any, 
              color: color_palette?.primary 
            }}>
              {content.personalInfo.name || "Your Name"}
            </h1>
            {content.personalInfo.title && (
              <h3 className="mb-2 font-bold" style={{ color: color_palette?.secondary }}>
                {content.personalInfo.title}
              </h3>
            )}
            <p style={{ color: color_palette?.text, fontSize: `${typography?.body?.size_pt || 10}pt` }}>
              {content.personalInfo.email} 
              {content.personalInfo.phone ? ` • ${content.personalInfo.phone}` : ''}
              {content.personalInfo.location ? ` • ${content.personalInfo.location}` : ''}
            </p>
          </div>
        );

      case 'summary':
        if (!content.summary) return null;
        return (
          <div key={key} className="mb-6">
            <h2 className="mb-2 pb-1" style={{ 
              fontFamily: typography?.h2?.font_family, 
              fontSize: `${typography?.h2?.size_pt || 14}pt`, 
              fontWeight: typography?.h2?.weight, 
              textTransform: typography?.h2?.text_transform as any, 
              color: color_palette?.primary, 
              borderBottom: `${dividerThickness} solid ${dividerColor}`
            }}>
              Summary
            </h2>
            <p className="whitespace-pre-line" style={{ 
              fontFamily: typography?.body?.font_family, 
              fontSize: `${typography?.body?.size_pt || 10}pt`, 
              lineHeight: typography?.body?.line_height, 
              color: color_palette?.text 
            }}>
              {content.summary}
            </p>
          </div>
        );

      case 'experience':
        if (!content.experience?.length) return null;
        return (
          <div key={key} className="mb-6">
            <h2 className="mb-3 pb-1" style={{ 
              fontFamily: typography?.h2?.font_family, 
              fontSize: `${typography?.h2?.size_pt || 14}pt`, 
              fontWeight: typography?.h2?.weight, 
              textTransform: typography?.h2?.text_transform as any, 
              color: color_palette?.primary, 
              borderBottom: `${dividerThickness} solid ${dividerColor}`
            }}>
              Experience
            </h2>
            {content.experience.map((exp, i) => (
              <div key={i} className="mb-4">
                <div className={`flex ${layout?.date_alignment === 'left' ? 'flex-col sm:flex-row sm:gap-2' : 'justify-between'} font-bold mb-1`} style={{ 
                  fontFamily: typography?.body?.font_family, 
                  fontSize: `${typography?.body?.size_pt || 10}pt`, 
                  color: color_palette?.text 
                }}>
                  <span>{exp.role} {exp.company ? `at ${exp.company}` : ''}</span>
                  {dateFormat !== 'Hidden' && (
                    <span style={{ fontWeight: 'normal', color: color_palette?.secondary }}>{exp.dates}</span>
                  )}
                </div>
                {exp.description && (
                  <div className="mt-1" style={{ 
                    fontFamily: typography?.body?.font_family, 
                    fontSize: `${typography?.body?.size_pt || 10}pt`, 
                    lineHeight: typography?.body?.line_height, 
                    color: color_palette?.text 
                  }}>
                    {exp.description.split('\n').map((line, idx) => {
                      const text = line.replace(/^[-*\u2022]\s*/, '').trim();
                      if (!text) return null;
                      return (
                        <div key={idx} className="flex items-start gap-2" style={{ marginBottom: `${(visual_elements?.list_line_height || 1.2) - 1}rem` }}>
                           <span style={{ color: color_palette?.primary }}>{visual_elements?.bullet_style === 'none' ? '' : '•'}</span>
                           <span>{text}</span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}
          </div>
        );

      case 'education':
        if (!content.education?.length) return null;
        return (
          <div key={key} className="mb-6">
            <h2 className="mb-3 pb-1" style={{ 
              fontFamily: typography?.h2?.font_family, 
              fontSize: `${typography?.h2?.size_pt || 14}pt`, 
              fontWeight: typography?.h2?.weight, 
              textTransform: typography?.h2?.text_transform as any, 
              color: color_palette?.primary, 
              borderBottom: `${dividerThickness} solid ${dividerColor}`
            }}>
              Education
            </h2>
            {content.education.map((edu, i) => (
              <div key={i} className="mb-3">
                <div className={`flex ${layout?.date_alignment === 'left' ? 'flex-col sm:flex-row sm:gap-2' : 'justify-between'} font-bold mb-1`} style={{ 
                  fontFamily: typography?.body?.font_family, 
                  fontSize: `${typography?.body?.size_pt || 10}pt`, 
                  color: color_palette?.text 
                }}>
                  <span>{edu.degree} {edu.institution ? `— ${edu.institution}` : ''}</span>
                  {dateFormat !== 'Hidden' && (
                    <span style={{ fontWeight: 'normal', color: color_palette?.secondary }}>{edu.dates}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        );

      case 'projects':
        if (!content.projects?.length) return null;
        return (
          <div key={key} className="mb-6">
            <h2 className="mb-3 pb-1" style={{ 
              fontFamily: typography?.h2?.font_family, 
              fontSize: `${typography?.h2?.size_pt || 14}pt`, 
              fontWeight: typography?.h2?.weight, 
              textTransform: typography?.h2?.text_transform as any, 
              color: color_palette?.primary, 
              borderBottom: `${dividerThickness} solid ${dividerColor}`
            }}>
              Projects
            </h2>
            {content.projects.map((proj, i) => (
              <div key={i} className="mb-4">
                <div className="font-bold mb-1" style={{ 
                  fontFamily: typography?.body?.font_family, 
                  fontSize: `${typography?.body?.size_pt || 10}pt`, 
                  color: color_palette?.text 
                }}>
                  {proj.name}
                </div>
                {proj.description && (
                  <div className="mt-1" style={{ 
                    fontFamily: typography?.body?.font_family, 
                    fontSize: `${typography?.body?.size_pt || 10}pt`, 
                    lineHeight: typography?.body?.line_height, 
                    color: color_palette?.text 
                  }}>
                    {proj.description.split('\n').map((line, idx) => {
                      const text = line.replace(/^[-*\u2022]\s*/, '').trim();
                      if (!text) return null;
                      return (
                        <div key={idx} className="flex items-start gap-2" style={{ marginBottom: `${(visual_elements?.list_line_height || 1.2) - 1}rem` }}>
                           <span style={{ color: color_palette?.primary }}>{visual_elements?.bullet_style === 'none' ? '' : '•'}</span>
                           <span>{text}</span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}
          </div>
        );

      case 'skills':
        if (!content.skills?.length) return null;
        return (
          <div key={key} className="mb-6">
            <h2 className="mb-3 pb-1" style={{ 
              fontFamily: typography?.h2?.font_family, 
              fontSize: `${typography?.h2?.size_pt || 14}pt`, 
              fontWeight: typography?.h2?.weight, 
              textTransform: typography?.h2?.text_transform as any, 
              color: color_palette?.primary, 
              borderBottom: `${dividerThickness} solid ${dividerColor}`
            }}>
              Skills
            </h2>
            <div className="flex flex-wrap gap-2">
              {content.skills.map((skill, i) => (
                <span key={i} className="px-2 py-1 rounded" style={{ 
                  backgroundColor: `${color_palette?.primary}15`, 
                  color: color_palette?.primary,
                  fontFamily: typography?.body?.font_family,
                  fontSize: `${(typography?.body?.size_pt || 10) - 1}pt`
                }}>
                  {skill}
                </span>
              ))}
            </div>
          </div>
        );

      case 'certifications':
        if (!content.certifications?.length) return null;
        return (
          <div key={key} className="mb-6">
            <h2 className="mb-3 pb-1" style={{ 
              fontFamily: typography?.h2?.font_family, 
              fontSize: `${typography?.h2?.size_pt || 14}pt`, 
              fontWeight: typography?.h2?.weight, 
              textTransform: typography?.h2?.text_transform as any, 
              color: color_palette?.primary, 
              borderBottom: `${dividerThickness} solid ${dividerColor}`
            }}>
              Certifications
            </h2>
            <ul style={{ 
              fontFamily: typography?.body?.font_family, 
              fontSize: `${typography?.body?.size_pt || 10}pt`, 
              color: color_palette?.text 
            }}>
              {content.certifications.map((cert, i) => (
                <li key={i} className="mb-1">{cert}</li>
              ))}
            </ul>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div id="resume-preview" className="w-full max-w-[800px] bg-white shadow-md border border-border" style={{ 
      aspectRatio: '1 / 1.414',
      backgroundColor: color_palette?.background || '#FFFFFF',
      paddingTop: layout?.margins?.top || '40px',
      paddingBottom: layout?.margins?.bottom || '40px',
      paddingLeft: layout?.margins?.left || '40px',
      paddingRight: layout?.margins?.right || '40px',
    }}>
      {isMultiColumn ? (
        <div style={{ display: 'grid', gridTemplateColumns: getGridTemplateColumns(), gap: '30px' }}>
          <div>
            {sections_layout?.main_column?.map(renderSection)}
          </div>
          <div>
            {sections_layout?.sidebar_column?.map(renderSection)}
          </div>
        </div>
      ) : (
        <div>
          {sections_layout?.main_column?.map(renderSection)}
        </div>
      )}
    </div>
  );
}
