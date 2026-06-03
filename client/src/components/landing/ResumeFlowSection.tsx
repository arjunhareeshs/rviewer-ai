import { AnimatedSection } from '../ui/AnimatedSection';
import { AnimatedItem } from '../ui/AnimatedItem';
import { FileText, CheckCircle2, TrendingUp, Layers } from 'lucide-react';

export function ResumeFlowSection() {
  return (
    <div className="py-32 bg-white relative overflow-hidden" id="how-it-works">
      <div className="max-w-7xl mx-auto px-6">
        
        <div className="text-center mb-20">
          <h2 className="text-3xl md:text-5xl font-display text-text-primary mb-4">
            The Analysis <span className="italic font-light">Pipeline</span>
          </h2>
          <p className="text-text-secondary text-lg max-w-2xl mx-auto">
            Watch as our engine breaks down your resume, extracts key intelligence, and maps it against industry standards.
          </p>
        </div>

        <div className="flex flex-col lg:flex-row items-center gap-16">
          
          {/* Left Side: Mock Resume entering from left */}
          <AnimatedSection className="w-full lg:w-1/2">
            <AnimatedItem direction="left" distance={100} className="relative">
              <div className="absolute inset-0 bg-accent/5 blur-3xl rounded-full transform -rotate-12 translate-x-12 translate-y-12"></div>
              
              <div className="relative bg-surface rounded-2xl shadow-2xl border border-border p-8 aspect-[1/1.4] transform -rotate-3 hover:rotate-0 transition-transform duration-700">
                <div className="w-1/2 h-6 bg-border rounded-md mb-6"></div>
                <div className="w-3/4 h-3 bg-border/60 rounded mb-2"></div>
                <div className="w-full h-3 bg-border/60 rounded mb-8"></div>
                
                <div className="space-y-4 mb-8">
                  <div className="w-1/3 h-4 bg-border rounded mb-3"></div>
                  <div className="w-full h-2 bg-border/40 rounded"></div>
                  <div className="w-5/6 h-2 bg-border/40 rounded"></div>
                  <div className="w-4/6 h-2 bg-border/40 rounded"></div>
                </div>

                <div className="space-y-4">
                  <div className="w-1/3 h-4 bg-border rounded mb-3"></div>
                  <div className="flex gap-2">
                    <div className="w-16 h-6 bg-accent/10 rounded-full"></div>
                    <div className="w-20 h-6 bg-accent/10 rounded-full"></div>
                    <div className="w-14 h-6 bg-accent/10 rounded-full"></div>
                  </div>
                </div>

                {/* Animated scanning line overlay */}
                <div className="absolute top-0 left-0 w-full h-1 bg-accent/50 shadow-[0_0_15px_rgba(79,70,229,0.5)] animate-[slideDown_3s_ease-in-out_infinite]"></div>
              </div>
            </AnimatedItem>
          </AnimatedSection>

          {/* Right Side: Flow Steps entering from right */}
          <div className="w-full lg:w-1/2">
            <AnimatedSection staggerChildren={0.2}>
              {[
                { icon: <FileText className="w-6 h-6 text-accent" />, title: "Structural Parsing", desc: "Our document vision model perfectly reconstructs the layout and reads text just like a human recruiter." },
                { icon: <CheckCircle2 className="w-6 h-6 text-success" />, title: "ATS Optimization", desc: "We score your resume against 50+ ATS criteria and flag missing sections or formatting errors." },
                { icon: <Layers className="w-6 h-6 text-warning" />, title: "Skill Extraction", desc: "Every tool, language, and soft skill is identified and mapped to a standardized global ontology." },
                { icon: <TrendingUp className="w-6 h-6 text-accent" />, title: "Career Mapping", desc: "Based on your extracted profile, we generate an interactive roadmap to reach your next title." },
              ].map((step, idx) => (
                <AnimatedItem key={idx} direction="right" distance={50}>
                  <div className="flex gap-6 mb-10 group">
                    <div className="flex-none">
                      <div className="w-14 h-14 rounded-2xl bg-cream border border-border flex items-center justify-center shadow-sm group-hover:border-accent group-hover:bg-accent-soft transition-colors">
                        {step.icon}
                      </div>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-text-primary mb-2">{step.title}</h3>
                      <p className="text-text-secondary leading-relaxed">{step.desc}</p>
                    </div>
                  </div>
                </AnimatedItem>
              ))}
            </AnimatedSection>
          </div>

        </div>
      </div>
      
      <style>{`
        @keyframes slideDown {
          0% { top: 0; opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { top: 100%; opacity: 0; }
        }
      `}</style>
    </div>
  );
}
