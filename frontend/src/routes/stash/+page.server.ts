// src/routes/+page.server.ts
import type { PageServerLoad, Actions } from './$types';
import { error, redirect } from '@sveltejs/kit';
import type { Link } from '$lib/types';

export const load: PageServerLoad = async ({ cookies }) => {
  const token = cookies.get('token');
  if (!token) {
    throw redirect(303, '/login');
  }

  const res = await fetch('https://stash-link.fly.dev/links', {
    method: 'GET',
    headers: {
      "authorization": `Bearer ${token}`,
      "Accept": "*/*",
      "cache-control": "no-cache",
      'accept-encoding': 'gzip, deflate, br'
    },
    credentials: 'include'
  });

  if (!res.ok) {
    if (res.status === 401) {
      // If the API returns unauthorized, redirect to login
      cookies.delete('token', { path: '/' }); // Clear the invalid token
      throw redirect(303, '/login');
    }
    throw error(res.status, 'Failed to fetch links');
  }

  const links = await res.json();
  return { 
    links: links.map((link: Link) => ({
      id: link.id,
      url: link.url,
      note: link.note,
      read: link.read
    }))
  };
}

export const actions: Actions = {
  addLink: async ({ cookies, request }) => {
    const token = cookies.get('token');
    if (!token) {
      throw redirect(303, '/login');
    }

    const data = await request.formData();
    const url = data.get('url')?.toString();
    const note = data.get('note')?.toString() || '';

    if (!url) {
      throw error(400, 'URL is required');
    }

    const res = await fetch('https://stash-link.fly.dev/links/save', {
      method: 'POST',
      headers: { 
        'content-type': 'application/json',
        'authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ url, note })
    });

    if (!res.ok) {
      if (res.status === 401) {
        // If the API returns unauthorized, redirect to login
        cookies.delete('token', { path: '/' }); // Clear the invalid token
        throw redirect(303, '/login');
      }
      throw error(res.status, 'Failed to save link');
    }

    return await res.json();
  },

  toggleRead: async ({ cookies, request }) => {
    const token = cookies.get('token');
    if (!token) {
      throw redirect(303, '/login');
    }

    const data = await request.formData();
    const id = data.get('id')?.toString();

    if (!id) {
      throw error(400, 'Link ID is required');
    }

    const res = await fetch(`https://stash-link.fly.dev/links/${id}/read`, {
      method: 'PATCH',
      headers: {
        'authorization': `Bearer ${token}`
      }
    });

    if (!res.ok) {
      if (res.status === 401) {
        // If the API returns unauthorized, redirect to login
        cookies.delete('token', { path: '/' }); // Clear the invalid token
        throw redirect(303, '/login');
      }
      throw error(res.status, 'Failed to toggle read status');
    }

    return { success: true, id };
  },

  removeLink: async ({ cookies, request }) => {
    const token = cookies.get('token');
    if (!token) {
      throw redirect(303, '/login');
    }

    const data = await request.formData();
    const id = data.get('id')?.toString();

    if (!id) {
      throw error(400, 'Link ID is required');
    }

    const res = await fetch(`https://stash-link.fly.dev/links/${id}`, {
      method: 'DELETE',
      headers: {
        'authorization': `Bearer ${token}`
      }
    });

    if (!res.ok) {
      if (res.status === 401) {
        // If the API returns unauthorized, redirect to login
        cookies.delete('token', { path: '/' }); // Clear the invalid token
        throw redirect(303, '/login');
      }
      throw error(res.status, 'Failed to delete link');
    }

    return { success: true, id };
  },

  logout: async ({ cookies }) => {
    cookies.delete('token', { path: '/' });
    throw redirect(303, '/');
  }
};
