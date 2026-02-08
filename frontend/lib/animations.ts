import { motion, Variants } from 'framer-motion';

// Default spring transition configuration
export const springTransition = {
  type: 'spring',
  stiffness: 100,
  damping: 15,
} as const;

// Subtle motion transition configuration
export const subtleMotionTransition = {
  type: 'spring',
  stiffness: 300,
  damping: 30,
} as const;

// Page transition variants
export const pageVariants: Variants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  in: {
    opacity: 1,
    y: 0,
    transition: springTransition,
  },
  out: {
    opacity: 0,
    y: -20,
    transition: springTransition,
  },
};

// Stagger container variants
export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

// Stagger item variants
export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: subtleMotionTransition,
  },
};

// Fade in variants
export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: springTransition
  },
};

// Slide in from left variants
export const slideInLeft: Variants = {
  hidden: { x: -100, opacity: 0 },
  visible: {
    x: 0,
    opacity: 1,
    transition: springTransition
  },
};

// Slide in from right variants
export const slideInRight: Variants = {
  hidden: { x: 100, opacity: 0 },
  visible: {
    x: 0,
    opacity: 1,
    transition: springTransition
  },
};

// Scale in variants
export const scaleIn: Variants = {
  hidden: { scale: 0.8, opacity: 0 },
  visible: {
    scale: 1,
    opacity: 1,
    transition: springTransition
  },
};

// Focus mode overlay variants
export const focusModeOverlay: Variants = {
  hidden: {
    opacity: 0,
    transition: {
      duration: 0.3,
    }
  },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.3,
    }
  },
};

// Focus mode content variants
export const focusModeContent: Variants = {
  hidden: {
    scale: 0.95,
    opacity: 0,
    transition: {
      duration: 0.3,
    }
  },
  visible: {
    scale: 1,
    opacity: 1,
    transition: {
      duration: 0.3,
      delay: 0.1,
    }
  },
};

export { motion };