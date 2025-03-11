import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies }) => {
    const token = cookies.get('stash_token');
    if (token) {
        throw redirect(303, '/stash');
    }
    return {};
};