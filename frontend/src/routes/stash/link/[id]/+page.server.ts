import { redirect, error } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { ApiClient, ApiError } from '$lib/server/api';
import type { Link, Category } from '$lib/types';

export const load: PageServerLoad = async ({ params, cookies }) => {
  const token = cookies.get('stash_token');
  if (!token) {
    throw redirect(303, '/login');
  }

  const api = new ApiClient(token);
  
  try {
    // Get the specific link by ID
    const link = await api.get<Link>(`/links/${params.id}`);
    
    // Get all categories for the dropdown
    const categories = await api.get<Category[]>('/categories');
    
    return {
      link,
      categories
    };
  } catch (e) {
    if (e instanceof ApiError) {
      if (e.status === 401) {
        // If the API returns unauthorized, redirect to login
        cookies.delete('stash_token', { path: '/' }); // Clear the invalid token
        throw redirect(303, '/login');
      } else if (e.status === 404) {
        throw error(404, 'Link not found');
      }
    }
    throw error(500, 'Failed to load link details');
  }
}

export const actions: Actions = {
  logout: async ({ cookies }) => {
    cookies.delete('stash_token', { path: '/' });
    throw redirect(303, '/');
  },
  
  generateSummary: async ({ request, cookies, params }) => {
    const token = cookies.get('stash_token');
    if (!token) {
      throw redirect(303, '/login');
    }
    
    const api = new ApiClient(token);
    
    try {
      // Get the form data
      const formData = await request.formData();
      
      // Call the API endpoint to generate a summary
      const result = await api.patch<Link>(`/links/${params.id}/summarize`, {});
      
      return result
    } catch (e) {
      console.error('Error generating summary:', e);
      
      if (e instanceof ApiError) {
        if (e.status === 401) {
          cookies.delete('stash_token', { path: '/' });
          throw redirect(303, '/login');
        }
        console.log(e)
        return {
          success: false,
          error: e.message
        };
      }
      console.log(e)
      return {
        success: false,
        error: 'Failed to generate summary'
      };
    }
  }
};
