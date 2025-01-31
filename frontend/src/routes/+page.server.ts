// src/routes/+page.server.ts
import type { PageServerLoad } from './$types';
import type { Link } from '$lib/types';


export const load: PageServerLoad = async () => {
  try {
    const res = await fetch('https://stash-link.fly.dev/links');
    const links = await res.json()
    return { 
      links: links.map((link: Link) => ({
        id: link.id,
        url: link.url,
        note: link.note,
        read: link.read
      }))
     };
  } catch (e) {
    console.error('error fetching links', e);
    return { links: [] };
  }
}
