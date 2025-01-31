<script lang="ts">
    import type { PageProps } from './$types';
    import type { Link } from '$lib/types';
    import { LinkStatusTab } from '$lib/types';

	let { data }: PageProps = $props();
    let links: Link[] = $state(data.links);
    let newUrl = $state('');
    let newNote = $state('');
    let activeTab: LinkStatusTab = $state(LinkStatusTab.Unread);

    async function addLink() {
        // event.preventDefault();
        if (!newUrl.trim()) return;
        try {
        const body = { url: newUrl, note: newNote };
        const res = await fetch('https://stash-link.fly.dev/save', {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify(body)
        });
        const savedLink = await res.json();
        // prepend or push to array
        links = [savedLink, ...links];
        // reset fields
        newUrl = '';
        newNote = '';
        } catch (err) {
        console.error('failed to save link:', err);
        }
    }
  
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
        <!-- add new link form -->
    <form class="flex flex-col space-y-2"
        onsubmit={addLink}>
        <input
            type="text"
            placeholder="link url"
            bind:value={newUrl}
            class="px-2 py-1 rounded bg-gray-800 text-white border border-gray-700 focus:outline-none"
        />
        <input
            type="text"
            placeholder="note (optional)"
            bind:value={newNote}
            class="px-2 py-1 rounded bg-gray-800 text-white border border-gray-700 focus:outline-none"
        />
        <button
            type="submit"
            class="bg-blue-600 hover:bg-blue-700 text-white rounded px-3 py-1 w-24"
        >
        add
        </button>
    </form>
      <!-- tabs -->
      <div class="flex space-x-4 border-b border-gray-700 mb-4">
        <button
          class="py-2 px-4 hover:bg-gray-800 focus:outline-none"
          class:font-bold={activeTab === LinkStatusTab.Unread}
          onclick={() => (activeTab = LinkStatusTab.Unread)}
        >
          unread
        </button>
        <button
          class="py-2 px-4 hover:bg-gray-800 focus:outline-none"
          class:font-bold={activeTab === LinkStatusTab.Read}
          onclick={() => (activeTab = LinkStatusTab.Read)}
        >
          read
        </button>
      </div>
  
      {#if activeTab === 'unread'}
        <!-- unread links -->
        {#each links.filter((l) => !l.read) as link}
          <div class="bg-gray-800 rounded p-4 flex justify-between items-center gap-2">
            <div class="flex flex-col">
              <a href={link.url} target="_blank" rel="noreferrer" class="text-blue-400 hover:underline break-all w-64 truncate">
                {link.url}
              </a>
              <span class="text-sm text-gray-400 italic">{link.note}</span>
            </div>
            <div class="flex gap-2">
              <button
                onclick={() => markRead(link.id)}
                class="bg-green-600 hover:bg-green-700 px-2 py-1 rounded text-sm"
              >
                mark read
              </button>
              <button
                onclick={() => removeLink(link.id)}
                class="bg-red-600 hover:bg-red-700 px-2 py-1 rounded text-sm"
              >
                delete
              </button>
            </div>
          </div>
        {/each}
      {:else}
        <!-- read links -->
        {#each links.filter((l) => l.read) as link}
          <div class="bg-gray-800 rounded p-4 flex justify-between items-center gap-2">
            <div class="flex flex-col">
              <a href={link.url} target="_blank" rel="noreferrer" class="text-blue-400 hover:underline break-all w-64 truncate">
                {link.url}
              </a>
              <span class="text-sm text-gray-400 italic">{link.note}</span>
            </div>
            <div class="flex gap-2">
              <span class="text-green-400 text-sm font-semibold">read</span>
              <button
                onclick={() => removeLink(link.id)}
                class="bg-red-600 hover:bg-red-700 px-2 py-1 rounded text-sm"
              >
                delete
              </button>
            </div>
          </div>
        {/each}
      {/if}
    </main>
  </div>