/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        tiktok: {
          red: '#fe2c55',
          cyan: '#25f4ee',
          dark: '#010101',
        },
      },
    },
  },
  plugins: [],
}
