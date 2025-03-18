<script lang="ts">
    import type { PageProps } from './$types';
    import type { Link, Category } from '$lib/types';
    import Header from '$lib/Header.svelte';
    import { goto } from '$app/navigation';
    
    let { data }: PageProps = $props();
    let link: Link = $state(data.link);
    let categories: Category[] = $state(data.categories);
    
    // Function to get category name by id
    function getCategoryName(categoryId: number | undefined): string {
        if (!categoryId) return 'Uncategorized';
        const category = categories.find(c => c.id === categoryId);
        return category ? category.name : 'Uncategorized';
    }
    
    // Handle category selection change
    async function handleCategoryChange(event: Event) {
        const select = event.target as HTMLSelectElement;
        const categoryId = select.value ? parseInt(select.value) : null;
        
        const formData = new FormData();
        formData.append('id', link.id);
        formData.append('categoryId', categoryId?.toString() || '');
        
        const res = await fetch('/stash?/assignCategory', {
            method: 'POST',
            body: formData
        });
        
        if (res.ok) {
            link = { ...link, category_id: categoryId || undefined };
        } else {
            console.error('Failed to update category:', await res.text());
        }
    }
    
    // Toggle read status
    async function toggleRead() {
        const formData = new FormData();
        formData.append('id', link.id);
        
        const res = await fetch('/stash?/toggleRead', {
            method: 'POST',
            body: formData
        });
        
        if (res.ok) {
            link = { ...link, read: !link.read };
        } else {
            console.error('Failed to toggle read status:', await res.text());
        }
    }
    
    // Delete link and navigate back to list
    async function deleteLink() {
        const formData = new FormData();
        formData.append('id', link.id);
        
        const res = await fetch('/stash?/removeLink', {
            method: 'POST',
            body: formData
        });
        
        if (res.ok) {
            // Navigate back to the stash page after successful deletion
            goto('/stash');
        } else {
            console.error('Failed to delete link:', await res.text());
        }
    }
    
    // Go back to stash page
    function goBack() {
        goto('/stash');
    }
</script>

<div class="min-h-screen bg-gray-900 text-gray-200">
    <Header showLogout={true} />
    
    <main class="max-w-2xl mx-auto p-4 space-y-6">
        <!-- Back button -->
        <button 
            onclick={goBack}
            class="flex items-center gap-1 text-gray-400 hover:text-gray-200 transition-colors"
        >
            ← Back to stash
        </button>
        
        <!-- Link details card -->
        <div class="bg-gray-800 rounded-lg p-6 space-y-4">
            <div class="space-y-2">
                <h1 class="text-xl font-medium text-white break-words">
                    {link.title || 'Untitled Link'}
                </h1>
                
                <a 
                    href={link.url} 
                    target="_blank" 
                    rel="noreferrer" 
                    class="text-blue-400 hover:underline break-all"
                >
                    {link.url}
                </a>
                
                {#if link.note}
                    <div class="mt-4 bg-gray-700 p-3 rounded">
                        <h3 class="text-sm font-medium text-gray-400 mb-1">Note:</h3>
                        <p class="text-gray-200">{link.note}</p>
                    </div>
                {/if}
                
                <!-- Short summary section -->
                {#if link.short_summary}
                    <div class="mt-4 bg-gray-700 p-3 rounded">
                        <h3 class="text-sm font-medium text-gray-400 mb-1">Short Summary:</h3>
                        <p class="text-gray-200">{link.short_summary}</p>
                    </div>
                {/if}
            </div>
            
            <!-- Category management -->
            <div class="pt-4 border-t border-gray-700">
                <h3 class="text-sm font-medium text-gray-400 mb-2">Category:</h3>
                <select 
                    class="bg-gray-700 border border-gray-600 text-sm rounded px-3 py-2 text-gray-300 w-full"
                    value={link.category_id || ""}
                    onchange={handleCategoryChange}
                >
                    <option value="">Uncategorized</option>
                    {#each categories as category}
                        <option value={category.id}>{category.name}</option>
                    {/each}
                </select>
            </div>
            
            <!-- Future AI summary section -->
            <div class="pt-4 border-t border-gray-700">
                <h3 class="text-sm font-medium text-gray-400 mb-2">AI Summary:</h3>
                <div class="bg-gray-700 p-3 rounded text-gray-400 italic">
                    AI summary will be integrated here in a future update.
                </div>
            </div>
            
            <!-- Actions -->
            <div class="pt-4 border-t border-gray-700 flex flex-wrap gap-3">
                <button
                    onclick={toggleRead}
                    class="bg-gray-700 hover:bg-gray-600 px-3 py-2 rounded text-sm transition-colors"
                >
                    {link.read ? 'Mark as unread' : 'Mark as read'}
                </button>
                
                <button
                    onclick={deleteLink}
                    class="bg-red-900 hover:bg-red-800 px-3 py-2 rounded text-sm transition-colors"
                >
                    Delete link
                </button>
            </div>
        </div>
    </main>
</div>
