/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      "./templates/**/*.html",
      "./static/src/**/*.js",
      "./node_modules/flowbite/**/*.js"
    ],
    theme: {
      extend: {
        fontFamily: {
          sans: ['Poppins', 'ui-sans-serif', 'system-ui'],
        },
      },
    },
    plugins: [
      require('flowbite/plugin')
    ],
  }
  