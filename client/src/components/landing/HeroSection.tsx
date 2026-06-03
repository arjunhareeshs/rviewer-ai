import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { AnimatedSection } from '../ui/AnimatedSection';
import { AnimatedItem } from '../ui/AnimatedItem';

export function HeroSection() {
  const containerRef = useRef(null);
  const navigate = useNavigate();
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"]
  });

  // Parallax effects
  const yBg = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
  const yCards = useTransform(scrollYProgress, [0, 1], ["0%", "20%"]);
  const opacityText = useTransform(scrollYProgress, [0, 0.5], [1, 0]);

  return (
    <div 
      ref={containerRef}
      className="relative min-h-[90vh] flex flex-col items-center justify-center overflow-hidden pt-20 perspective-1000"
    >
      {/* Background grid parallax layer */}
      <motion.div 
        style={{ y: yBg }}
        className="absolute inset-0 z-0 opacity-[0.03] pointer-events-none"
      >
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
      </motion.div>

      {/* Floating Elements Layer */}
      <motion.div 
        style={{ y: yCards }}
        className="absolute inset-0 z-0 pointer-events-none"
      >
        <div className="absolute top-1/4 left-[10%] glass p-4 rounded-2xl animate-fade-in [animation-delay:0.5s] opacity-0 rotate-[-6deg] shadow-lg">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-success/10 flex items-center justify-center text-success font-bold">92</div>
            <div>
              <p className="text-xs font-bold text-text-secondary uppercase tracking-wider">ATS Score</p>
              <p className="font-mono font-bold text-text-primary">Excellent</p>
            </div>
          </div>
        </div>

        <div className="absolute bottom-1/3 right-[10%] glass p-4 rounded-2xl animate-fade-in [animation-delay:0.7s] opacity-0 rotate-[4deg] shadow-lg">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center text-accent font-bold">88</div>
            <div>
              <p className="text-xs font-bold text-text-secondary uppercase tracking-wider">Interview</p>
              <p className="font-mono font-bold text-text-primary">Top 10%</p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Foreground Content */}
      <motion.div style={{ opacity: opacityText }} className="relative z-10 w-full max-w-4xl mx-auto px-6 text-center">
        <AnimatedSection staggerChildren={0.15}>
          <AnimatedItem>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-soft text-accent text-xs font-bold uppercase tracking-widest mb-6">
              <span className="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
              RViewer AI Engine 2.0
            </div>
          </AnimatedItem>

          <AnimatedItem>
            <h1 className="text-5xl md:text-7xl font-display text-text-primary leading-[1.1] tracking-tight mb-6">
              Transform Your Resume Into <br />
              <span className="font-light italic text-gradient">Career Intelligence</span>
            </h1>
          </AnimatedItem>

          <AnimatedItem>
            <p className="text-lg md:text-xl text-text-secondary max-w-2xl mx-auto mb-10 leading-relaxed">
              Upload your resume and experience a full-scale AI analysis. We don't just score it—we simulate your interview, map your skills, and build your career roadmap.
            </p>
          </AnimatedItem>

          <AnimatedItem>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button 
                onClick={() => navigate('/register?role=student')}
                className="w-full sm:w-auto px-8 py-4 rounded-xl bg-accent text-white font-bold text-lg hover:bg-accent/90 transition-all hover:shadow-xl hover:-translate-y-1"
              >
                I'm a Candidate
              </button>
              <button 
                onClick={() => navigate('/register?role=recruiter')}
                className="w-full sm:w-auto px-8 py-4 rounded-xl bg-surface border-2 border-border text-text-primary font-bold text-lg hover:border-accent hover:text-accent transition-all hover:shadow-md hover:-translate-y-1"
              >
                I'm a Recruiter
              </button>
            </div>
            <p className="mt-4 text-sm text-text-muted font-medium">Free forever for basic analysis. No credit card required.</p>
          </AnimatedItem>
        </AnimatedSection>
      </motion.div>

    </div>
  );
}
