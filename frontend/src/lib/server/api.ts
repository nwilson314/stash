import { redirect } from '@sveltejs/kit';
import type { Cookies } from '@sveltejs/kit';
import { API_URL } from '$env/static/private';

// API Error class for consistent error handling
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class ApiClient {
  private baseUrl: string = API_URL;
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  private async fetch<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const headers = {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = null;
      }
      console.log("Error response:", errorData)
      
      throw new ApiError(
        errorData?.message || 'An error occurred',
        response.status,
        errorData
      );
    }

    // Handle empty responses
    if (response.status === 204) {
      return null as T;
    }

    return await response.json();
  }

  async get<T>(path: string): Promise<T> {
    return this.fetch<T>(path, { method: 'GET' });
  }

  async post<T>(path: string, data?: any): Promise<T> {
    return this.fetch<T>(path, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T>(path: string, data?: any): Promise<T> {
    return this.fetch<T>(path, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(path: string, data: any): Promise<T> {
    return this.fetch<T>(path, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(path: string): Promise<T> {
    return this.fetch<T>(path, { method: 'DELETE' });
  }
}

// Helper to create an API client from cookies
export async function createApiClient(cookies: Cookies): Promise<ApiClient> {
  const token = cookies.get('stash_token');
  if (!token) {
    throw redirect(303, '/login');
  }
  return new ApiClient(token);
}
