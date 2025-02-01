import { redirect, error } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions: Actions = {
    default: async ({ cookies, request }) => {
        const data = await request.formData();
        const email = data.get('email')?.toString();
        const password = data.get('password')?.toString();

        if (!email || !password) {
            throw error(400, 'Email and password are required');
        }

        const res = await fetch('https://stash-link.fly.dev/users/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (!res.ok) {
            throw error(400, 'Failed to register. User might already exist.');
        }

        const { access_token } = await res.json();

        // Set the cookie server-side with proper security options
        cookies.set('token', access_token, {
            path: '/',
            httpOnly: true,
            secure: true,
            sameSite: 'strict',
            maxAge: 60 * 60 * 24 * 7 // 1 week
        });

        // Return a redirect instead of throwing it
        return {
            status: 303,
            redirect: '/stash'
        };
    }
};