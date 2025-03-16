// src/routes/+page.server.ts
import type { PageServerLoad, Actions } from './$types';
import { error, redirect } from '@sveltejs/kit';
import type { Link, Category } from '$lib/types';
import { ApiClient, ApiError } from '$lib/server/api';

export const load: PageServerLoad = async ({ cookies }) => {
  const token = cookies.get('stash_token');
  if (!token) {
    throw redirect(303, '/login');
  }

  const api = new ApiClient(token);

  try {
    const [links, categories] = await Promise.all([
      api.get<Link[]>('/links'),
      api.get<Category[]>('/categories')
    ]);
    return { links, categories };
  } catch (e) {
    if (e instanceof ApiError && e.status === 401) {
      // If the API returns unauthorized, redirect to login
      cookies.delete('stash_token', { path: '/' }); // Clear the invalid token
      throw redirect(303, '/login');
    }
    throw e
  }
}

export const actions: Actions = {
  addLink: async ({ cookies, request }) => {
    const token = cookies.get('stash_token');
    if (!token) {
      throw redirect(303, '/login');
    }

    const api = new ApiClient(token);

    const data = await request.formData();
    const url = data.get('url')?.toString();
    const note = data.get('note')?.toString() || '';

    if (!url) {
      throw error(400, 'URL is required');
    }

    try {
      const res = await api.post('/links/save', { url, note });
      return res
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        // If the API returns unauthorized, redirect to login
        cookies.delete('stash_token', { path: '/' }); // Clear the invalid token
        throw redirect(303, '/login');
      }
      throw e
    }
  },

  toggleRead: async ({ cookies, request }) => {
    const token = cookies.get('stash_token');
    if (!token) {
      throw redirect(303, '/login');
    }

    const api = new ApiClient(token);

    const data = await request.formData();
    const id = data.get('id')?.toString();

    if (!id) {
      throw error(400, 'Link ID is required');
    }

    try {
      const res = await api.patch(`/links/${id}/read`);
      return { success: true, id }
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        // If the API returns unauthorized, redirect to login
        cookies.delete('stash_token', { path: '/' }); // Clear the invalid token
        throw redirect(303, '/login');
      }
      throw e
    }
  },

  removeLink: async ({ cookies, request }) => {
    const token = cookies.get('stash_token');
    if (!token) {
      throw redirect(303, '/login');
    }

    const data = await request.formData();
    const id = data.get('id')?.toString();

    if (!id) {
      throw error(400, 'Link ID is required');
    }

    const api = new ApiClient(token);

    try {
      const res = await api.delete(`/links/${id}`);
      return { success: true, id };
    } catch (e) {
      if (e instanceof ApiError) {
        if (e.status === 401) {
          // If the API returns unauthorized, redirect to login
          cookies.delete('stash_token', { path: '/' }); // Clear the invalid token
          throw redirect(303, '/login');
        }
      }
      throw e;
    }
  },

  addCategory: async ({ cookies, request }) => {
    const token = cookies.get('stash_token');
    if (!token) {
      throw redirect(303, '/login');
    }

    const data = await request.formData();
    const name = data.get('name')?.toString();

    if (!name) {
      throw error(400, 'Category name is required');
    }

    const api = new ApiClient(token);

    try {
      const res = await api.post<Category>('/categories', { name });
      return { success: true, id: res.id };
    } catch (e) {
      if (e instanceof ApiError) {
        if (e.status === 401) {
          // If the API returns unauthorized, redirect to login
          cookies.delete('stash_token', { path: '/' }); // Clear the invalid token
          throw redirect(303, '/login');
        }
      }
      throw e;
    }
  },

  editCategory: async ({ cookies, request }) => {
    const token = cookies.get('stash_token');
    if (!token) {
      throw redirect(303, '/login');
    }

    const data = await request.formData();
    const name = data.get('name')?.toString();
    const id = data.get('id')?.toString();

    if (!name || !id) {
      throw error(400, 'Category name and ID are required');
    }

    const api = new ApiClient(token);

    try {
      const res = await api.patch<Category>(`/categories/${id}`, { name });
      return { success: true, id: res.id };
    } catch (e) {
      if (e instanceof ApiError) {
        if (e.status === 401) {
          // If the API returns unauthorized, redirect to login
          cookies.delete('stash_token', { path: '/' }); // Clear the invalid token
          throw redirect(303, '/login');
        }
      }
      throw e;
    }
  },

  removeCategory: async ({ cookies, request }) => {
    const token = cookies.get('stash_token');
    if (!token) {
      throw redirect(303, '/login');
    }

    const data = await request.formData();
    const id = data.get('id')?.toString();

    if (!id) {
      throw error(400, 'Category ID is required');
    }

    const api = new ApiClient(token);

    try {
      await api.delete(`/categories/${id}`);
      return { success: true };
    } catch (e) {
      if (e instanceof ApiError) {
        if (e.status === 401) {
          // If the API returns unauthorized, redirect to login
          cookies.delete('stash_token', { path: '/' }); // Clear the invalid token
          throw redirect(303, '/login');
        }
      }
      throw e;
    }
  },

  assignCategory: async ({ cookies, request }) => {
    const token = cookies.get('stash_token');
    if (!token) {
      throw redirect(303, '/login');
    }

    const data = await request.formData();
    const id = data.get('id')?.toString();
    const categoryId = data.get('categoryId')?.toString();

    if (!id) {
      throw error(400, 'Link ID is required');
    }

    const api = new ApiClient(token);

    try {
      // If categoryId is empty, set it to null to remove the category
      const payload = { category_id: categoryId ? parseInt(categoryId) : null };
      await api.patch(`/links/${id}`, payload);
      return { success: true };
    } catch (e) {
      if (e instanceof ApiError) {
        if (e.status === 401) {
          // If the API returns unauthorized, redirect to login
          cookies.delete('stash_token', { path: '/' }); // Clear the invalid token
          throw redirect(303, '/login');
        }
      }
      throw e;
    }
  },

  logout: async ({ cookies }) => {
    cookies.delete('stash_token', { path: '/' });
    throw redirect(303, '/');
  }
};
