import type { Config } from 'tailwindcss'

// Paleta de Locus (app/CLAUDE.md). Usar exactamente estos valores.
export default {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        color1: '#282832', // fondo principal / navbar / footer
        color2: '#77181e', // acento principal: botones, CTAs
        color3: '#a92727', // acento secundario: hover, activo
        color4: '#c6d6d6', // fondos secundarios, bordes suaves
        color5: '#dee7e7', // fondo de tarjetas, chips inactivos
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        // Tarjetas claras sobre fondo oscuro: filo superior de luz + sombra profunda y suave.
        tarjeta: '0 1px 0 0 rgba(255,255,255,0.7) inset, 0 18px 40px -20px rgba(0,0,0,0.75)',
        'tarjeta-hover':
          '0 1px 0 0 rgba(255,255,255,0.7) inset, 0 26px 60px -22px rgba(169,39,39,0.65)',
        panel: '0 24px 60px -24px rgba(0,0,0,0.8)',
      },
    },
    screens: {
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
      '2xl': '1536px',
      // Ventanas altas: la portada aprovecha el espacio vertical extra sin empujar las tarjetas fuera de vista.
      tall: { raw: '(min-height: 820px)' },
    },
  },
  plugins: [],
} satisfies Config
