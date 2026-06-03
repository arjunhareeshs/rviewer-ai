import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface AnimatedItemProps {
  children: ReactNode;
  className?: string;
  direction?: 'up' | 'down' | 'left' | 'right';
  distance?: number;
}

export function AnimatedItem({ 
  children, 
  className = '',
  direction = 'up',
  distance = 30
}: AnimatedItemProps) {
  
  const getInitialOffset = () => {
    switch (direction) {
      case 'up': return { y: distance, x: 0 };
      case 'down': return { y: -distance, x: 0 };
      case 'left': return { x: distance, y: 0 };
      case 'right': return { x: -distance, y: 0 };
    }
  };

  const initial = { opacity: 0, ...getInitialOffset() };

  return (
    <motion.div
      variants={{
        hidden: initial,
        visible: {
          opacity: 1,
          x: 0,
          y: 0,
          transition: {
            type: 'spring',
            stiffness: 100,
            damping: 20
          }
        }
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
