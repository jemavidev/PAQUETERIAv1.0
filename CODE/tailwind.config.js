/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/templates/**/*.html",
    "./src/static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        'papyrus-blue': '#1e40af',
        'papyrus-green': '#059669',
        'papyrus-orange': '#ea580c',
        'papyrus-red': '#dc2626',
        'papyrus-yellow': '#d97706',
        'papyrus-purple': '#7c3aed',
        'papyrus-pink': '#db2777',
        'papyrus-indigo': '#4f46e5',
        'papyrus-teal': '#0d9488',
        'papyrus-cyan': '#0891b2',
        'papyrus-lime': '#65a30d',
        'papyrus-emerald': '#10b981',
        'papyrus-rose': '#e11d48',
        'papyrus-violet': '#7c3aed',
        'papyrus-fuchsia': '#c026d3',
        'papyrus-sky': '#0284c7',
        'papyrus-amber': '#d97706',
        'papyrus-stone': '#78716c',
        'papyrus-neutral': '#525252',
        'papyrus-slate': '#475569',
        'papyrus-gray': '#6b7280',
        'papyrus-zinc': '#71717a',
      }
    }
  },
  plugins: [],
}
