<script lang="ts">
    import type { PageProps } from './$types';
    import type { Link } from '$lib/types';
    import { LinkStatusTab } from '$lib/types';
    import Header from '$lib/Header.svelte';

	let { data }: PageProps = $props();
    let links: Link[] = $state(data.links);
    let newUrl = $state('');
    let newNote = $state('');
    let activeTab: LinkStatusTab = $state(LinkStatusTab.Unread);
    let pendingDeleteId = $state('');

    async function addLink() {
        if (!newUrl.trim()) return;
        
        const formData = new FormData();
        formData.append('url', newUrl);
        formData.append('note', newNote);

        const res = await fetch('?/addLink', {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            const savedLink = await res.json();
            const parsedData = JSON.parse(savedLink.data);
            
            const linkDataKeys = parsedData[0];
            const newLink: Link = {
              id: parsedData[linkDataKeys.id],
              url: parsedData[linkDataKeys.url],
              note: parsedData[linkDataKeys.note],
              read: parsedData[linkDataKeys.read]
            };
            console.log(newLink);
            links = [newLink, ...links];
            newUrl = '';
            newNote = '';
            activeTab = LinkStatusTab.Unread; // Switch to unread tab after adding
            pendingDeleteId = ''; // Clear any pending delete state
        } else {
            console.error('failed to save link:', await res.text());
        }
    }
  
    async function toggleRead(id: string) {
        const formData = new FormData();
        formData.append('id', id);

        const res = await fetch('?/toggleRead', {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            const result = await res.json();
            links = links.map((l: Link) => (l.id === id ? { ...l, read: !l.read } : l));
        } else {
            console.error('failed to toggle read status:', await res.text());
        }
    }
  
    async function initiateDelete(id: string) {
        pendingDeleteId = id;
    }

    async function confirmDelete(id: string) {
        const formData = new FormData();
        formData.append('id', id);

        const res = await fetch('?/removeLink', {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            links = links.filter((l: Link) => l.id !== id);
            pendingDeleteId = '';
        } else {
            console.error('failed to delete link:', await res.text());
        }
    }
  </script>
  
<div class="min-h-screen bg-gray-900 text-gray-200">
    <Header showLogout={true} />
  
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
            class="bg-gray-700 hover:bg-gray-600 text-gray-100 px-3 py-1 rounded w-24 transition-colors font-medium"
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
  
      {#if links.length === 0}
        <div class="text-center py-8">
          <p class="text-gray-400 mb-4">looks like you're stash-less</p>
          <a href="/docs" class="inline-block bg-gray-800 hover:bg-gray-700 text-gray-200 px-6 py-3 rounded-lg transition-colors">
            learn to stash from mobile →
          </a>
          <p class="text-sm text-gray-500 italic mt-4">(or start stashing above)</p>
        </div>
      {:else if activeTab === 'unread'}
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
                onclick={() => toggleRead(link.id)}
                class="border border-gray-600 hover:bg-gray-700 px-2 py-1 rounded text-sm text-gray-300"
              >
                mark read
              </button>
              {#if pendingDeleteId === link.id}
                <div class="flex items-center gap-2">
                  <button
                    onclick={() => confirmDelete(link.id)}
                    class="border border-gray-600 hover:bg-gray-700 px-2 py-1 rounded text-sm text-red-400"
                  >
                    confirm?
                  </button>
                </div>
              {:else}
                <button
                  onclick={() => initiateDelete(link.id)}
                  class="border border-gray-600 hover:bg-gray-700 px-2 py-1 rounded text-sm text-red-600"
                >
                  delete
                </button>
              {/if}
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
              <span class="text-gray-500 text-sm">read</span>
              <button
                onclick={() => toggleRead(link.id)}
                class="border border-gray-600 hover:bg-gray-700 px-2 py-1 rounded text-sm text-gray-300"
              >
                mark unread
              </button>
              {#if pendingDeleteId === link.id}
                <div class="flex items-center gap-2">
                  <button
                    onclick={() => confirmDelete(link.id)}
                    class="border border-gray-600 hover:bg-gray-700 px-2 py-1 rounded text-sm text-red-400"
                  >
                    confirm?
                  </button>
                </div>
              {:else}
                <button
                  onclick={() => initiateDelete(link.id)}
                  class="border border-gray-600 hover:bg-gray-700 px-2 py-1 rounded text-sm text-red-400"
                >
                  delete
                </button>
              {/if}
            </div>
          </div>
        {/each}
      {/if}
    </main>
  </div>