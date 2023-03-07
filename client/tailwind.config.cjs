/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './index.html',
    './src/**/*.{html,svelte,ts,js}'
  ],
  theme: {
    extend: {
      backgroundImage: {
        'logo': '../assets/img/popchat-logo.png'
      },
      colors: {
        'pri': {
          500: 'rgba(37, 54, 64, 0.5)',
          900: '#253640'
        },
        'sec': {
          700: 'rgba(31, 219, 165, 0.7)',
          900: '#1FDBA5'
        },
        'dark-pri': '#090E0F',
        'dark-sec': '#151B1C',
        'dark-transp': 'rgba(255, 255, 255, 0.1)',
        'msg-blue': '#00A8C5'
      },
      gridTemplateColumns: {
        'home': '1fr 2fr'
      }
    },
  },
  plugins: [],
}
