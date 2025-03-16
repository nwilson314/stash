<script lang="ts">
    import type { PageProps } from './$types';
    import type { Link, Category } from '$lib/types';
    import { LinkStatusTab } from '$lib/types';
    import Header from '$lib/Header.svelte';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    let { data }: PageProps = $props();
    let links: Link[] = $state(data.links);
    let categories: Category[] = $state(data.categories);
    let newUrl = $state('');
    let newNote = $state('');
    let activeTab: LinkStatusTab = $state(LinkStatusTab.Unread);
    let pendingDeleteId = $state('');
    
    // Active category filter (null means "All Categories")
    let activeCategory: number | null = $state(null);
    
    // New category name for adding
    let newCategoryName = $state('');
    
    // Category being edited (null means not editing any)
    let editingCategoryId = $state<number | null>(null);
    let editCategoryName = $state('');
    
    // Category dropdown state
    let isCategoryDropdownOpen = $state(false);
    let isAddingCategory = $state(false);
    
    // Reference to the dropdown container
    let dropdownContainer: HTMLElement;

    // Handle clicks outside the dropdown to close it
    onMount(() => {
        function handleClickOutside(event: MouseEvent) {
            if (dropdownContainer && !dropdownContainer.contains(event.target as Node) && isCategoryDropdownOpen) {
                isCategoryDropdownOpen = false;
                isAddingCategory = false;
            }
        }
        
        document.addEventListener('click', handleClickOutside);
        
        return () => {
            document.removeEventListener('click', handleClickOutside);
        };
    });

    async function addLink(event: SubmitEvent) {
        event.preventDefault();
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
              title: parsedData[linkDataKeys.title],
              note: parsedData[linkDataKeys.note],
              read: parsedData[linkDataKeys.read],
              content_type: parsedData[linkDataKeys.content_type],
              processing_status: parsedData[linkDataKeys.processing_status],
              // Dummy category assignment - in real implementation, this would come from the API
              category_id: Math.floor(Math.random() * categories.length) + 1
            };
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
    
    // Function to add a new category
    async function addCategory(event: SubmitEvent) {
        event.preventDefault();
        if (!newCategoryName.trim()) return;
        
        const formData = new FormData();
        formData.append('name', newCategoryName);

        const res = await fetch('?/addCategory', {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            const result = await res.json();
            const newCategory: Category = {
                id: result.id,
                name: newCategoryName
            };
            categories = [...categories, newCategory];
            newCategoryName = '';
            isAddingCategory = false;
        } else {
            console.error('failed to add category:', await res.text());
        }
    }
    
    // Function to start editing a category
    function startEditCategory(category: Category, event: MouseEvent) {
        event.stopPropagation(); // Prevent triggering category selection
        editingCategoryId = category.id;
        editCategoryName = category.name;
    }
    
    // Function to save category edit
    async function saveEditCategory(event: SubmitEvent) {
        event.preventDefault();
        event.stopPropagation(); // Prevent triggering category selection
        if (!editingCategoryId || !editCategoryName.trim()) return;

        const formData = new FormData();
        formData.append('id', editingCategoryId.toString());
        formData.append('name', editCategoryName);

        const res = await fetch('?/editCategory', {
            method: 'POST',
            body: formData
        });

        if (!res.ok) {
            console.error('failed to edit category:', await res.text());
            return;
        }
        
        categories = categories.map(c => 
            c.id === editingCategoryId 
                ? { ...c, name: editCategoryName } 
                : c
        );
        
        editingCategoryId = null;
        editCategoryName = '';
    }
    
    // Function to delete a category
    async function deleteCategory(id: string, event: MouseEvent) {
        event.stopPropagation(); // Prevent triggering category selection
        
        const formData = new FormData();
        formData.append('id', id);

        const res = await fetch('?/removeCategory', {
            method: 'POST',
            body: formData
        });

        if (!res.ok) {
            console.error('failed to delete category:', await res.text());
            return;
        }

        categories = categories.filter((c: Category) => c.id !== parseInt(id));
        
        // Reset active category if the deleted one was selected
        if (activeCategory === parseInt(id)) {
            activeCategory = null;
        }
        
        // Update links that were in this category to be uncategorized
        links = links.map(l => 
            l.category_id === parseInt(id) 
                ? { ...l, category_id: undefined } 
                : l
        );
    }
    
    // Function to assign a category to a link
    function assignCategory(linkId: string, categoryId: number | null) {
        // In a real implementation, this would be an API call
        links = links.map(l => 
            l.id === linkId 
                ? { ...l, category_id: categoryId || undefined } 
                : l
        );
    }
    
    // Function to get category name by id
    function getCategoryName(categoryId: number | undefined): string {
        if (!categoryId) return 'Uncategorized';
        const category = categories.find(c => c.id === categoryId);
        return category ? category.name : 'Uncategorized';
    }
    
    // Handle category selection change for a link
    function handleCategoryChange(event: Event, linkId: string) {
        const select = event.target as HTMLSelectElement;
        const value = select.value;
        assignCategory(linkId, value ? parseInt(value) : null);
    }
    
    // Toggle category dropdown
    function toggleCategoryDropdown(event: MouseEvent) {
        event.stopPropagation(); // Prevent document click from immediately closing it
        isCategoryDropdownOpen = !isCategoryDropdownOpen;
        if (!isCategoryDropdownOpen) {
            isAddingCategory = false;
        }
    }
    
    // Select a category and close dropdown
    function selectCategory(id: number | null) {
        activeCategory = id;
        isCategoryDropdownOpen = false; // Close dropdown after selection
        isAddingCategory = false;
    }
    
    // Toggle add category form
    function toggleAddCategoryForm(event: MouseEvent) {
        event.stopPropagation(); // Prevent document click from immediately closing it
        isAddingCategory = !isAddingCategory;
        if (isAddingCategory && !isCategoryDropdownOpen) {
            isCategoryDropdownOpen = true;
        }
    }
    
    // Get active category name
    function getActiveCategoryName(): string {
        if (activeCategory === null) return 'All';
        const category = categories.find(c => c.id === activeCategory);
        return category ? category.name : 'All';
    }
    
    // Filter links based on active category and tab
    let filteredLinks: Link[] = $derived.by(() => {
        return links.filter((link: Link) => {
            const matchesCategory = activeCategory === null || link.category_id === activeCategory;
            const matchesReadStatus = activeTab === LinkStatusTab.Read ? link.read : !link.read;
            return matchesCategory && matchesReadStatus;
        });
    })

    // Function to view link details
    function viewLinkDetails(id: string) {
        goto(`/stash/link/${id}`);
    }
  </script>
  
<div class="min-h-screen bg-gray-900 text-gray-200">
    <Header showLogout={true} />
  
    <main class="max-w-2xl mx-auto p-4 space-y-4">
        <!-- add new link form -->
        <form class="flex flex-col space-y-2" onsubmit={addLink}>
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
        
        <!-- category management - hybrid approach -->
        <div class="space-y-3">
            <div class="flex justify-between items-center">
                <div class="relative w-full" bind:this={dropdownContainer}>
                    <div class="flex justify-between items-center">
                        <div class="flex items-center gap-2">
                            <h3 class="text-sm font-medium text-gray-400">Categories:</h3>
                            <button 
                                onclick={toggleCategoryDropdown} 
                                class="flex items-center gap-1 px-3 py-1 rounded-full text-sm bg-gray-800 hover:bg-gray-700 transition-colors"
                            >
                                {getActiveCategoryName()}
                                <span class="text-xs">{isCategoryDropdownOpen ? '▲' : '▼'}</span>
                            </button>
                        </div>
                        <button
                            onclick={toggleAddCategoryForm}
                            class="text-sm bg-gray-800 hover:bg-gray-700 px-2 py-1 rounded transition-colors"
                            title="Add new category"
                        >
                            + Add
                        </button>
                    </div>
                    
                    <!-- Dropdown content -->
                    {#if isCategoryDropdownOpen}
                        <div class="absolute z-10 mt-1 w-full bg-gray-800 border border-gray-700 rounded shadow-lg">
                            <div class="p-2 space-y-2">
                                <!-- All option -->
                                <div class="flex justify-between items-center px-2 py-1 rounded hover:bg-gray-700">
                                    <button 
                                        class="flex items-center gap-2 w-full text-left"
                                        onclick={() => selectCategory(null)}
                                    >
                                        <span class="inline-block w-4 h-4 rounded-full border border-gray-500 flex-shrink-0" class:bg-blue-500={activeCategory === null}></span>
                                        <span>All</span>
                                    </button>
                                </div>
                                
                                <!-- Category options -->
                                {#each categories as category}
                                    {#if editingCategoryId === category.id}
                                        <form class="flex gap-1 px-2 py-1" onsubmit={saveEditCategory}>
                                            <input
                                                type="text"
                                                bind:value={editCategoryName}
                                                class="flex-grow px-2 py-1 text-sm rounded bg-gray-700 text-white border border-gray-600 focus:outline-none"
                                                onclick={(e) => e.stopPropagation()}
                                            />
                                            <button
                                                type="submit"
                                                class="bg-green-700 hover:bg-green-600 text-white px-2 py-1 rounded text-sm"
                                            >
                                                Save
                                            </button>
                                        </form>
                                    {:else}
                                        <div class="flex justify-between items-center px-2 py-1 rounded hover:bg-gray-700">
                                            <button 
                                                class="flex items-center gap-2 flex-grow text-left"
                                                onclick={() => selectCategory(category.id)}
                                            >
                                                <span class="inline-block w-4 h-4 rounded-full border border-gray-500 flex-shrink-0" class:bg-blue-500={activeCategory === category.id}></span>
                                                <span>{category.name}</span>
                                            </button>
                                            <div class="flex gap-1">
                                                <button
                                                    onclick={(e) => startEditCategory(category, e)}
                                                    class="text-gray-500 hover:text-gray-300 text-xs"
                                                    title="Edit category"
                                                >
                                                    ✎
                                                </button>
                                                <button
                                                    onclick={(e) => deleteCategory(category.id.toString(), e)}
                                                    class="text-gray-500 hover:text-red-400 text-xs"
                                                    title="Delete category"
                                                >
                                                    ×
                                                </button>
                                            </div>
                                        </div>
                                    {/if}
                                {/each}
                                
                                <!-- Add category form -->
                                {#if isAddingCategory}
                                    <form class="flex gap-1 p-2 border-t border-gray-700" onsubmit={addCategory}>
                                        <input
                                            type="text"
                                            placeholder="New category name"
                                            bind:value={newCategoryName}
                                            class="flex-grow px-2 py-1 text-sm rounded bg-gray-700 text-white border border-gray-600 focus:outline-none"
                                            onclick={(e) => e.stopPropagation()}
                                        />
                                        <button
                                            type="submit"
                                            class="bg-gray-700 hover:bg-gray-600 text-gray-100 px-2 py-1 rounded text-sm transition-colors"
                                        >
                                            Add
                                        </button>
                                    </form>
                                {/if}
                            </div>
                        </div>
                    {/if}
                </div>
            </div>
        </div>
        
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
        {:else if filteredLinks.length === 0}
            <div class="text-center py-8">
                <p class="text-gray-400">no links in this category/tab combination</p>
            </div>
        {:else}
            <!-- links with categories -->
            {#each filteredLinks as link (link.id)}
                <div class="bg-gray-800 rounded p-4 flex flex-col sm:flex-row justify-between gap-3 sm:items-center">
                    <div class="flex flex-col min-w-0">
                        <div class="flex items-center gap-2 mb-1">
                            <a href={link.url} target="_blank" rel="noreferrer" class="text-blue-400 hover:underline truncate max-w-full font-medium">
                                {link.title || link.url}
                            </a>
                            <span class="text-xs px-2 py-0.5 rounded-full bg-gray-700 text-gray-300">
                                {getCategoryName(link.category_id)}
                            </span>
                        </div>
                        {#if link.title}
                            <span class="text-xs text-gray-500 truncate">{link.url}</span>
                        {/if}
                        {#if link.note}
                            <span class="text-sm text-gray-400 italic truncate">{link.note}</span>
                        {/if}
                    </div>
                    <div class="flex gap-2 shrink-0 items-center">
                        <!-- Details button -->
                        <button
                            class="border border-gray-600 hover:bg-gray-700 px-2 py-1 rounded text-sm text-gray-300"
                            title="View link details"
                            onclick={() => viewLinkDetails(link.id)}
                        >
                            details
                        </button>
                        
                        <button
                            onclick={() => toggleRead(link.id)}
                            class="border border-gray-600 hover:bg-gray-700 px-2 py-1 rounded text-sm text-gray-300"
                        >
                            {link.read ? 'mark unread' : 'mark read'}
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
        {/if}
    </main>
</div>