<script lang="ts">
    import type { PageProps } from './$types';
    import type { Link } from '$lib/types';

	let { data }: PageProps = $props();
    let links = $state(data.links);
  
    async function markRead(id: string) {
      try {
        await fetch(`https://stash-link.fly.dev/links/${id}/read`, {
          method: 'PATCH'
        });
        links = links.map((l: Link) => (l.id === id ? { ...l, read: true } : l));
      } catch(e) {
        console.error('failed to mark as read', e);
      }
    }
  
    async function removeLink(id: string) {
      try {
        await fetch(`https://stash-link.fly.dev/links/${id}`, {
          method: 'DELETE'
        });
        links = links.filter((l: Link) => l.id !== id);
      } catch(e) {
        console.error('failed to delete link', e);
      }
    }
  </script>
  
  <div class="min-h-screen bg-gray-900 text-gray-200">
    <header class="bg-gray-800 py-4">
      <h1 class="text-center text-2xl font-bold">stash links</h1>
    </header>
  
    <main class="max-w-2xl mx-auto p-4 space-y-4">
      {#each links as link}
        <div class="bg-gray-800 rounded p-4 flex justify-between items-center gap-2">
          <div class="flex flex-col">
            <a
                href={link.url}
                target="_blank"
                rel="noreferrer"
                class="text-blue-400 hover:underline break-all block w-64 truncate"
            >
              {link.url}
            </a>
            <span class="text-sm text-gray-400 italic">{link.note}</span>
          </div>
          <div class="flex gap-2">
            <button
              class="bg-green-600 hover:bg-green-700 px-2 py-1 rounded text-sm"
              onclick={() => markRead(link.id)}
              disabled={link.read}
            >
              mark read
            </button>
            <button
              class="bg-red-600 hover:bg-red-700 px-2 py-1 rounded text-sm"
              onclick={() => removeLink(link.id)}
            >
              delete
            </button>
          </div>
        </div>
      {/each}
    </main>
  </div>
  