/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './core/**/*.py',
    './accounts/**/*.py',
    './dashboard/**/*.py',
    './static/js/**/*.js'
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1A2B3C', 50: '#F4F6F8', 100: '#E4E8EC', 200: '#C4CCD4', 300: '#9AA7B4',
          400: '#63748A', 500: '#3F5165', 600: '#2C3D4E', 700: '#22303F', 800: '#1A2B3C', 900: '#111D29'
        },
        secondary: {
          DEFAULT: '#E67E22', 50: '#FEF6EC', 100: '#FCE8CE', 200: '#F8CE9A', 300: '#F3B266',
          400: '#EE973E', 500: '#E67E22', 600: '#C96512', 700: '#A04E0F', 800: '#7A3C0D', 900: '#572A0A'
        },
        accent: '#F3F4F6',
        body: '#333333'
      },
      fontFamily: {
        heading: ['Montserrat', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        body: ['Open Sans', 'ui-sans-serif', 'system-ui', 'sans-serif']
      },
      maxWidth: { '8xl': '1400px' },
      keyframes: {
        floaty: { '0%,100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-10px)' } }
      },
      animation: { floaty: 'floaty 6s ease-in-out infinite' }
    }
  },
  plugins: [require('@tailwindcss/forms'), require('@tailwindcss/typography')]
};