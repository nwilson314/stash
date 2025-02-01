// src/routes/+page.server.ts
import type { PageServerLoad, Actions } from './$types';
import { error } from '@sveltejs/kit';
import type { Link } from '$lib/types';

export const load: PageServerLoad = async ({ cookies, fetch }) => {
  let token = cookies.get('token')
  if (!token) {
    throw error(401, 'Unauthorized')
  }
  const headers = {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json",
    "Accept": "application/json"
  };
  
  console.log("Request headers:", headers);
  
  const res = await fetch('https://stash-link.fly.dev/links', {
    method: 'GET',
    headers,
    // Remove credentials since we're using Authorization header
  });

  console.log("Response headers:", Object.fromEntries(res.headers.entries()));
  console.log("Response status:", res.status);
  const links = await res.json()
  console.log("fetched links ", links)

  if (!res.ok) {
    throw error(res.status, 'Failed to fetch links');
  }

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
      throw error(401, 'Unauthorized');
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
      throw error(res.status, 'Failed to save link');
    }

    return await res.json();
  },

  markRead: async ({ cookies, request }) => {
    const token = cookies.get('token');
    if (!token) {
      throw error(401, 'Unauthorized');
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
      throw error(res.status, 'Failed to mark link as read');
    }

    return { success: true, id };
  },

  removeLink: async ({ cookies, request }) => {
    const token = cookies.get('token');
    if (!token) {
      throw error(401, 'Unauthorized');
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
      throw error(res.status, 'Failed to delete link');
    }

    return { success: true, id };
  }
};
