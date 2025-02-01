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

    const res = await fetch('https://stash-link.fly.dev/users/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!res.ok) {
      throw error(401, 'Invalid credentials');
    }

    const { access_token } = await res.json();
    
    console.log("Setting token in login:", access_token ? "present" : "missing");
    
    // Properly set the cookie server-side
    cookies.set('token', access_token, {
      path: '/',
      httpOnly: true,
      secure: true,
      sameSite: 'strict',
      maxAge: 60 * 60 * 24 * 7 // 1 week
    });

    // Verify cookie was set
    const verifyToken = cookies.get('token');
    console.log("Verifying token was set:", verifyToken ? "present" : "missing");

    // Return a redirect instead of throwing it
    return {
      status: 303,
      redirect: '/stash'
    };
  }
};