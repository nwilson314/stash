import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ cookies }) => {
    const token = cookies.get('token');

    if (token) {
        throw redirect(302, '/stash');
    }

    return {}; // normal landing page load
};