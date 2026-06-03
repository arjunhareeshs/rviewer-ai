import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-cream flex items-center justify-center p-6 relative overflow-hidden">
      
      {/* Abstract Background Elements */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-accent/5 blur-[120px] rounded-full pointer-events-none"></div>
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 text-center"
      >
        <h1 className="text-[12rem] font-display font-black text-transparent bg-clip-text bg-gradient-to-br from-accent to-blue-300 leading-none tracking-tighter drop-shadow-sm">
          404
        </h1>
        <h2 className="text-3xl font-display font-bold text-text-primary mt-4 mb-4">
          Page Not Found
        </h2>
        <p className="text-text-secondary text-lg max-w-md mx-auto mb-10">
          The page you are looking for doesn't exist or has been moved.
        </p>
        
        <Link 
          to="/" 
          className="inline-flex px-8 py-4 bg-surface border-2 border-border text-text-primary font-bold text-lg rounded-xl hover:border-accent hover:text-accent transition-all shadow-sm hover:shadow hover:-translate-y-0.5"
        >
          Return Home
        </Link>
      </motion.div>
    </div>
  );
}
