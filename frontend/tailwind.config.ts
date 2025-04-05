import type { Config } from 'tailwindcss';
import typography from '@tailwindcss/typography';

export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],

	theme: {
		extend: {
			typography: {
				DEFAULT: {
					css: {
						maxWidth: 'none',
						color: '#e2e8f0',
						a: {
							color: '#60a5fa',
							'&:hover': {
								color: '#93c5fd',
							},
						},
						h1: {
							color: '#f8fafc',
						},
						h2: {
							color: '#f8fafc',
						},
						h3: {
							color: '#f8fafc',
						},
						h4: {
							color: '#f8fafc',
						},
						strong: {
							color: '#f8fafc',
						},
						code: {
							color: '#f8fafc',
							backgroundColor: '#1e293b',
							padding: '0.2em 0.4em',
							borderRadius: '0.25rem',
						},
						blockquote: {
							color: '#cbd5e1',
							borderLeftColor: '#475569',
						},
						hr: {
							borderColor: '#475569',
						},
					},
				},
			},
		}
	},

	plugins: [
		typography,
	]
} satisfies Config;
