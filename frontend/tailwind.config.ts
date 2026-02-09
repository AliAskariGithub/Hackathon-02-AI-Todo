import type { Config } from 'tailwindcss';

export default {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0FFF50', // New primary green
          light: '#f6f6f6',   // Light mode primary
          dark: '#161616',    // Dark mode primary
        },
        secondary: {
          dark: '#232323',    // Dark mode secondary
          light: '#f5f4f2',   // Light mode secondary
        },
      },
      fontFamily: {
        'montserrat': ['var(--font-montserrat)', 'sans-serif'],
        'space-grotesk': ['var(--font-space-grotesk)', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config;