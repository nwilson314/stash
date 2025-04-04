import { redirect, error } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { ApiClient, ApiError } from '$lib/server/api';
import type { UserResponse, LinkActivity } from '$lib/types';

export const load: PageServerLoad = async ({ cookies }) => {
  const token = cookies.get('stash_token');
  const user_cookie = cookies.get('stash_user');
  if (!token || !user_cookie) {
    throw redirect(303, '/login');
  }

  const api = new ApiClient(token);
  const userObj = JSON.parse(user_cookie);
  
  try {
    const [user, linkActivity] = await Promise.all([
      api.get<UserResponse>(`/users/${userObj.id}`),
      api.get<LinkActivity>(`/users/${userObj.id}/activity`)
    ]);

    return {
      user,
      linkActivity
    };
  } catch (e) {
    if (e instanceof ApiError) {
      if (e.status === 401) {
        // If the API returns unauthorized, redirect to login
        cookies.delete('stash_token', { path: '/' });
        cookies.delete('stash_user', { path: '/' });
        throw redirect(303, '/login');
      }
    }
    throw error(500, 'Failed to load profile data');
  }
};

// Generate realistic dummy activity data for development
function generateDummyActivityData(): LinkActivity {
  const days: Record<string, number> = {};
  const today = new Date();
  
  // Generate activity for the last 120 days with some patterns
  for (let i = 0; i < 120; i++) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split('T')[0];
    
    // Create a realistic pattern:
    // - More activity on weekdays
    // - Some days with no activity
    // - Occasional days with high activity
    const dayOfWeek = date.getDay();
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    
    if (Math.random() < (isWeekend ? 0.6 : 0.3)) {
      // No activity this day
      continue;
    }
    
    // Occasional high activity day
    if (Math.random() < 0.1) {
      days[dateStr] = Math.floor(Math.random() * 8) + 5; // 5-12 links
    } else {
      // Normal activity day
      days[dateStr] = Math.floor(Math.random() * 4) + 1; // 1-4 links
    }
    
    // Create a streak for the last 5 days
    if (i < 5) {
      days[dateStr] = Math.floor(Math.random() * 3) + 1; // Ensure recent activity
    }
  }
  
  return { days };
}

export const actions: Actions = {
  updateProfile: async ({ cookies, request }) => {
    const token = cookies.get('stash_token');
    const user_cookie = cookies.get('stash_user');
    if (!token || !user_cookie) {
      throw redirect(303, '/login');
    }

    const api = new ApiClient(token);
    const data = await request.formData();
    const user = JSON.parse(user_cookie);
    
    const email = data.get('email')?.toString();
    const username = data.get('username')?.toString();
    
    // Get AI preferences
    const allowAiCategorization = data.has('allow_ai_categorization');
    const allowAiCreateCategories = data.has('allow_ai_create_categories');
    const aiConfidenceThreshold = parseFloat(data.get('ai_confidence_threshold')?.toString() || '0.7');
    
    // Get newsletter preferences
    const newsletterEnabled = data.has('newsletter_enabled');
    const newsletterFrequency = 'weekly'; // Currently only weekly is supported
    
    try {
      const updatedUser = await api.patch<UserResponse>(`/users/${user.id}`, { 
        email, 
        username,
        allow_ai_categorization: allowAiCategorization,
        allow_ai_create_categories: allowAiCreateCategories,
        ai_confidence_threshold: aiConfidenceThreshold,
        newsletter_enabled: newsletterEnabled,
        newsletter_frequency: newsletterFrequency
      });
      
      // Update the stored user data
      cookies.set('stash_user', JSON.stringify(updatedUser), { path: '/' });
      
      return { success: true, user: updatedUser };
    } catch (e) {
      if (e instanceof ApiError) {
        return { success: false, error: e.message };
      }
      throw e;
    }
  },
  
  changePassword: async ({ cookies, request }) => {
    const token = cookies.get('stash_token');
    if (!token) {
      throw redirect(303, '/login');
    }

    const api = new ApiClient(token);
    const data = await request.formData();
    
    const currentPassword = data.get('currentPassword')?.toString();
    const newPassword = data.get('newPassword')?.toString();
    
    if (!currentPassword || !newPassword) {
      return { success: false, error: 'Both current and new password are required' };
    }
    
    try {
      await api.patch('/users/password', {
        password: currentPassword,
        new_password: newPassword
      });
      
      return { success: true };
    } catch (e) {
      if (e instanceof ApiError) {
        return { success: false, error: e.message };
      }
      throw e;
    }
  },
  
  deleteAccount: async ({ cookies, request }) => {
    const token = cookies.get('stash_token');
    const user_str = cookies.get('stash_user');
    if (!token || !user_str) {
      throw redirect(303, '/login');
    }
    const user: UserResponse = JSON.parse(user_str);

    const api = new ApiClient(token);
    const data = await request.formData();
    
    const confirmDelete = data.get('confirmDelete')?.toString();
    
    if (confirmDelete !== 'DELETE') {
      return { success: false, error: 'Please type DELETE to confirm account deletion' };
    }
    
    try {
      await api.delete(`/users/${user.id}`);
      
      // Clear all cookies
      cookies.delete('stash_token', { path: '/' });
      cookies.delete('stash_user', { path: '/' });
      
      throw redirect(303, '/');
    } catch (e) {
      if (e instanceof ApiError && e.status !== 401) {
        return { success: false, error: e.message };
      }
      throw e;
    }
  },

  logout: async ({ cookies }) => {
    cookies.delete('stash_token', { path: '/' });
    throw redirect(303, '/');
  }
};
