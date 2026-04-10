/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'aether-black': '#0a0a0c',
                'aether-glass': 'rgba(255, 255, 255, 0.03)',
                'aether-border': 'rgba(255, 255, 255, 0.08)',
                'aether-accent': '#00d4ff',
            },
            backdropBlur: {
                'glass': '12px',
            }
        },
    },
    plugins: [],
}
