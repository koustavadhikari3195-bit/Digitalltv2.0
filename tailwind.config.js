/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/*.html',
    './apps/**/*.py',
  ],
  theme: {
    extend: {
      colors: {
        orange: '#FF6B00',
        black: '#000000',
        white: '#FFFFFF',
        'gray-1': '#0A0A0A',
        'gray-2': '#141414',
        'gray-3': '#A0A0A0',
      },
      fontFamily: {
        display: ['Syne', 'sans-serif'],
        body: ['DM Sans', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
