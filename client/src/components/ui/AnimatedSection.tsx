import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface AnimatedSectionProps {
  children: ReactNode;
  className?: string;
  staggerChildren?: number;
  delayChildren?: number;
}

export function AnimatedSection({ 
  children, 
  className = '', 
  staggerChildren = 0.1,
  delayChildren = 0
}: AnimatedSectionProps) {
  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-100px" }}
      variants={{
        hidden: {},
        visible: {
          transition: {
            staggerChildren,
            delayChildren
          }
        }
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
