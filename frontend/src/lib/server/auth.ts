import { redirect } from '@sveltejs/kit';
import type { Cookies } from '@sveltejs/kit';
import type { UserResponse } from '$lib/types';

export type ValidSession = {
  user: UserResponse | null;
  token: string | null;
};

export async function validateSession(cookies: Cookies): Promise<ValidSession> {
  const token = cookies.get('roastnotes_token');
  if (!token) {
    throw redirect(303, '/auth/logout');
  }

  const user_str = cookies.get('roastnotes_user');
  if (!user_str) {
    throw redirect(303, '/auth/logout');
  }

  try {
    const user: UserResponse = JSON.parse(user_str);
    return { user, token };
  } catch (e) {
    // If we can't parse the user data, clear cookies and redirect
    cookies.delete('roastnotes_token', { path: '/' });
    cookies.delete('roastnotes_user', { path: '/' });
    throw redirect(303, '/auth/logout');
  }
}


export async function checkSession(cookies: Cookies): Promise<ValidSession> {
  const token = cookies.get('roastnotes_token');
  if (!token) {
    return { user: null, token: null };
  }

  const user_str = cookies.get('roastnotes_user');
  if (!user_str) {
    return { user: null, token: null };
  }

  try {
    const user: UserResponse = JSON.parse(user_str);
    return { user, token };
  } catch (e) {
    // If we can't parse the user, return null session
    cookies.delete('roastnotes_token', { path: '/' });
    cookies.delete('roastnotes_user', { path: '/' });
    return { user: null, token: null };
  }
}
