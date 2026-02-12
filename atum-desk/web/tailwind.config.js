/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        atum: {
          50: '#fdf8e8',
          100: '#f9efc2',
          200: '#f5e299',
          300: '#edc86b',
          400: '#d4a73b',
          500: '#b88a2a',
          600: '#9a7020',
          700: '#7c591c',
          800: '#63481a',
          900: '#503c18',
          950: '#2d1f0b',
        },
        gold: {
          50: '#fdf8e8',
          100: '#f9efc2',
          200: '#f5e299',
          300: '#edc86b',
          400: '#d4a73b',
          500: '#b88a2a',
          600: '#9a7020',
          700: '#7c591c',
          800: '#63481a',
          900: '#503c18',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Cinzel', 'Georgia', 'serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(212, 167, 59, 0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(212, 167, 59, 0.8), 0 0 40px rgba(212, 167, 59, 0.4)' },
        },
      },
    },
  },
  plugins: [],
}
