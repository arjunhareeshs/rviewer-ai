import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, useScroll, useMotionValueEvent } from 'framer-motion';

export function Navbar() {
  const { scrollY } = useScroll();
  const [isScrolled, setIsScrolled] = useState(false);

  useMotionValueEvent(scrollY, "change", (latest) => {
    setIsScrolled(latest > 50);
  });

  return (
    <motion.nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled 
          ? 'bg-white/80 backdrop-blur-xl border-b border-border shadow-sm py-3' 
          : 'bg-transparent py-5'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 flex justify-between items-center">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center text-white font-bold text-xl">
            R
          </div>
          <span className="font-display font-bold text-2xl tracking-tight text-text-primary">
            RViewer
          </span>
        </Link>

        <div className="hidden md:flex items-center gap-8 font-medium text-sm text-text-secondary">
          <a href="#features" className="hover:text-accent transition-colors">Features</a>
          <a href="#how-it-works" className="hover:text-accent transition-colors">How it Works</a>
          <a href="#pricing" className="hover:text-accent transition-colors">Pricing</a>
        </div>

        <div className="flex items-center gap-4">
          <Link to="/login" className="text-sm font-semibold text-text-primary hover:text-accent transition-colors hidden sm:block">
            Sign In
          </Link>
          <Link to="/register" className="px-5 py-2.5 rounded-full bg-accent text-white text-sm font-semibold hover:bg-accent/90 shadow-sm transition-all hover:shadow hover:-translate-y-0.5">
            Get Started
          </Link>
        </div>
      </div>
    </motion.nav>
  );
}
