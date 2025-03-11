import { error, fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import type { AuthResponse } from '$lib/types';
import { ApiClient, ApiError } from '$lib/server/api';

export const actions: Actions = {
  default: async ({ cookies, request }) => {
    const data = await request.formData();
    const email = data.get('email')?.toString();
    const password = data.get('password')?.toString();

    if (!email || !password) {
      throw error(400, 'Email and password are required');
    }

    const api = new ApiClient('');
    try {
      const auth_response = await api.post<AuthResponse>('/users/login', {
        email, password
      });
      cookies.set('stash_token', auth_response.token.access_token, {path: '/'});
      cookies.set('stash_user', JSON.stringify(auth_response.user), {path: '/'});

      throw redirect(303, '/stash');
    } catch (e) {
      if (e instanceof ApiError) {
        return fail(e.status, {
          invalid: true,
          message: e.message
        });
      } else {
        throw e;
      }
    }
  }
};