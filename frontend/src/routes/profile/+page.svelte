<script lang="ts">
    import Header from '$lib/Header.svelte';
    import { enhance } from '$app/forms';
    import type { LinkActivity } from '$lib/types';
    
    let { data } = $props();
    let user = $state(data.user);
    let linkActivity = $state(data.linkActivity || {} as LinkActivity);
    
    // Form states
    let showPasswordForm = $state(false);
    let showDeleteForm = $state(false);
    let profileUpdateSuccess = $state(false);
    let passwordUpdateSuccess = $state(false);
    let errorMessage = $state('');
    
    // Password form
    let currentPassword = $state('');
    let newPassword = $state('');
    let confirmPassword = $state('');
    
    // Delete confirmation
    let deleteConfirmation = $state('');
    
    // Handle profile update
    const handleProfileUpdate = () => {
        profileUpdateSuccess = false;
        errorMessage = '';
        
        return async ({ result }: any) => {
            if (result.type === 'success') {
                if (result.data.success) {
                    profileUpdateSuccess = true;
                    user = result.data.user;
                } else {
                    errorMessage = result.data.error || 'Failed to update profile';
                }
            }
        };
    };
    
    // Handle password update
    const handlePasswordUpdate = () => {
        passwordUpdateSuccess = false;
        errorMessage = '';
        
        if (newPassword !== confirmPassword) {
            errorMessage = 'New passwords do not match';
            return () => {};
        }
        
        return async ({ result }: any) => {
            if (result.type === 'success') {
                if (result.data.success) {
                    passwordUpdateSuccess = true;
                    currentPassword = '';
                    newPassword = '';
                    confirmPassword = '';
                } else {
                    errorMessage = result.data.error || 'Failed to update password';
                }
            }
        };
    };
    
    // Format date for display
    function formatDate(dateString: string): string {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            timeZone: 'UTC'
        }).format(date);
    }
    
    // Toggle password form visibility
    function togglePasswordForm(): void {
        showPasswordForm = !showPasswordForm;
        if (!showPasswordForm) {
            currentPassword = '';
            newPassword = '';
            confirmPassword = '';
            passwordUpdateSuccess = false;
        }
        showDeleteForm = false;
    }
    
    // Toggle delete account form visibility
    function toggleDeleteForm(): void {
        showDeleteForm = !showDeleteForm;
        if (!showDeleteForm) {
            deleteConfirmation = '';
        }
        showPasswordForm = false;
    }
    
    // Types for contribution graph
    type ContributionDay = {
        date: string;
        count: number;
        level: number;
    };
    
    // Generate contribution graph data
    function getContributionLevels(activity: LinkActivity): ContributionDay[] {
        if (!activity || !activity.days) return [];
        
        // Find the max count to determine intensity levels
        const maxCount = Math.max(...Object.values(activity.days).map(count => Number(count)), 0);
        
        // Generate last 365 days (or available days)
        const today = new Date();
        const days: ContributionDay[] = [];
        
        for (let i = 364; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            const dateStr = date.toISOString().split('T')[0];
            
            const count = activity.days[dateStr] || 0;
            let level = 0;
            
            if (count > 0) {
                if (maxCount <= 4) {
                    level = count;
                } else {
                    // Calculate level based on percentage of max
                    const percentage = count / maxCount;
                    if (percentage <= 0.25) level = 1;
                    else if (percentage <= 0.5) level = 2;
                    else if (percentage <= 0.75) level = 3;
                    else level = 4;
                }
            }
            
            days.push({
                date: dateStr,
                count,
                level
            });
        }
        
        return days;
    }
    
    // Group days into weeks for the grid
    function getWeeks(days: ContributionDay[]): ContributionDay[][] {
        const weeks: ContributionDay[][] = [];
        for (let i = 0; i < days.length; i += 7) {
            weeks.push(days.slice(i, i + 7));
        }
        return weeks;
    }
    
    // Get month labels with their positions
    function getMonthLabels(days: ContributionDay[]): { label: string, position: number }[] {
        const months: { label: string, position: number }[] = [];
        let currentMonth = -1;
        
        days.forEach((day, index) => {
            // Parse date with UTC
            const [year, month, dayOfMonth] = day.date.split('-').map(Number);
            const date = new Date(Date.UTC(year, month - 1, dayOfMonth));
            const monthIndex = date.getUTCMonth();
            
            // If we encounter a new month, add it to our list
            if (monthIndex !== currentMonth) {
                currentMonth = monthIndex;
                const weekIndex = Math.floor(index / 7);
                const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                months.push({
                    label: monthNames[monthIndex],
                    position: weekIndex
                });
            }
        });
        
        return months;
    }
    
    // Types for contribution stats
    type ContributionStats = {
        total: number;
        streak: number;
        bestDay: {
            date: string;
            count: number;
        };
    };
    
    // Calculate contribution stats
    function getContributionStats(activity: LinkActivity): ContributionStats {
        if (!activity || !activity.days) {
            return { total: 0, streak: 0, bestDay: { date: '', count: 0 } };
        }
        
        const days = Object.entries(activity.days);
        const total = days.reduce((sum, [_, count]) => sum + Number(count), 0);
        
        // Find best day
        let bestDay = { date: '', count: 0 };
        for (const [date, count] of days) {
            if (Number(count) > bestDay.count) {
                bestDay = { date, count: Number(count) };
            }
        }
        
        // Calculate current streak
        let streak = 0;
        const today = new Date().toISOString().split('T')[0];
        let currentDate = new Date(today);
        
        while (true) {
            const dateStr = currentDate.toISOString().split('T')[0];
            if (activity.days[dateStr]) {
                streak++;
                currentDate.setDate(currentDate.getDate() - 1);
            } else {
                break;
            }
        }
        
        return { total, streak, bestDay };
    }
    
    // For real-time slider value display
    const initialThreshold = user.ai_confidence_threshold;
    let sliderValue = $state(initialThreshold);
    
    // Calculate if any preferences have changed
    const hasChanges = $derived(
        Math.round(initialThreshold * 100) !== Math.round(sliderValue * 100)
    );
    
    // This will update whenever sliderValue changes
    function handleThresholdInput(event: Event) {
        const input = event.target as HTMLInputElement;
        sliderValue = parseFloat(input.value);
    }
    
    // Contribution graph data
    const contributionDays = getContributionLevels(linkActivity);
    const contributionWeeks = getWeeks(contributionDays);
    const contributionStats = getContributionStats(linkActivity);
    const monthLabels = getMonthLabels(contributionDays);
    
    // Scroll to the end when the component is mounted
    function scrollToLatestActivity(node: HTMLElement) {
        // Set scroll position to the far right to show latest activity
        setTimeout(() => {
            node.scrollLeft = node.scrollWidth;
        }, 100);
        
        return {};
    }
</script>

<div class="min-h-screen bg-gray-900 text-gray-200">
    <Header showLogout={true} />
    
    <main class="max-w-2xl mx-auto p-4 space-y-8">
        <h1 class="text-2xl font-bold">Your Profile</h1>
        
        <!-- User Info Card -->
        <div class="bg-gray-800 rounded-lg p-6 space-y-6">
            <!-- Profile Information -->
            <div>
                <h2 class="text-xl font-medium mb-4">Account Information</h2>
                
                <form action="?/updateProfile" method="POST" use:enhance={handleProfileUpdate} class="space-y-4">
                    <div class="space-y-2">
                        <label for="email" class="block text-sm font-medium text-gray-400">Email</label>
                        <input 
                            type="email" 
                            id="email" 
                            name="email" 
                            value={user.email} 
                            class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                        />
                    </div>
                    
                    <div class="space-y-2">
                        <label for="username" class="block text-sm font-medium text-gray-400">Username</label>
                        <input 
                            type="text" 
                            id="username" 
                            name="username" 
                            value={user.username} 
                            class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                        />
                    </div>
                    
                    <!-- AI Preferences Section -->
                    <div class="mt-6 pt-4 border-t border-gray-700">
                        <h3 class="text-lg font-medium mb-3">AI Preferences</h3>
                        
                        <div class="space-y-4">
                            <div class="flex items-center">
                                <input 
                                    type="checkbox" 
                                    id="allow_ai_categorization" 
                                    name="allow_ai_categorization" 
                                    checked={user.allow_ai_categorization} 
                                    class="h-4 w-4 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
                                />
                                <label for="allow_ai_categorization" class="ml-2 block text-sm text-gray-300">
                                    Allow AI to categorize my links
                                </label>
                            </div>
                            
                            <div class="flex items-center">
                                <input 
                                    type="checkbox" 
                                    id="allow_ai_create_categories" 
                                    name="allow_ai_create_categories" 
                                    checked={user.allow_ai_create_categories} 
                                    class="h-4 w-4 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
                                />
                                <label for="allow_ai_create_categories" class="ml-2 block text-sm text-gray-300">
                                    Allow AI to create new categories
                                </label>
                            </div>
                            
                            <div class="space-y-2">
                                <div class="flex justify-between items-center">
                                    <label for="ai_confidence_threshold" class="block text-sm font-medium text-gray-400">
                                        AI Confidence
                                    </label>
                                    <div class="flex items-center space-x-2 text-sm">
                                        {#if hasChanges}
                                            <span class="text-gray-400">{Math.round(initialThreshold * 100)}%</span>
                                            <span class="text-gray-400">→</span>
                                        {/if}
                                        <span class="font-medium {hasChanges ? 'text-blue-400' : 'text-gray-300'} w-12 text-center">
                                            {Math.round(sliderValue * 100)}%
                                        </span>
                                    </div>
                                </div>
                                <input 
                                    type="range" 
                                    id="ai_confidence_threshold" 
                                    name="ai_confidence_threshold" 
                                    min="0" 
                                    max="1" 
                                    step="0.05" 
                                    value={sliderValue}
                                    oninput={handleThresholdInput}
                                    class="w-full bg-gray-700"
                                />
                                <div class="flex justify-between text-xs text-gray-400">
                                    <span>Low (more suggestions)</span>
                                    <span>High (fewer suggestions)</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Newsletter Preferences -->
                    <div class="mt-4 space-y-4">
                        <h3 class="text-lg font-medium mb-3">Newsletter</h3>
                        
                        <div class="flex items-center">
                            <input 
                                type="checkbox" 
                                id="newsletter_enabled" 
                                name="newsletter_enabled" 
                                checked={user.newsletter_enabled} 
                                class="h-4 w-4 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
                            />
                            <label for="newsletter_enabled" class="ml-2 block text-sm text-gray-300">
                                Receive weekly newsletter summarizing your saved links
                            </label>
                        </div>
                    </div>
                    
                    <div class="flex justify-end">
                        <button 
                            type="submit" 
                            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors"
                        >
                            Save Changes
                        </button>
                    </div>
                    
                    {#if profileUpdateSuccess}
                        <div class="bg-green-900/50 border border-green-800 text-green-200 px-4 py-2 rounded">
                            Profile updated successfully
                        </div>
                    {/if}
                </form>
            </div>
            
            <!-- Contribution Graph Section -->
            <div class="pt-6 border-t border-gray-700">
                <h2 class="text-xl font-medium mb-4">Your Link Activity</h2>
                
                <!-- Contribution Stats -->
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                    <div class="bg-gray-700 p-4 rounded">
                        <p class="text-sm text-gray-400">Total Links</p>
                        <p class="text-2xl font-bold">{contributionStats.total}</p>
                    </div>
                    
                    <div class="bg-gray-700 p-4 rounded">
                        <p class="text-sm text-gray-400">Current Streak</p>
                        <p class="text-2xl font-bold">{contributionStats.streak} {contributionStats.streak === 1 ? 'day' : 'days'}</p>
                    </div>
                    
                    <div class="bg-gray-700 p-4 rounded">
                        <p class="text-sm text-gray-400">Member Since</p>
                        <p class="text-xl font-bold">{user.created_at ? formatDate(user.created_at) : 'N/A'}</p>
                    </div>
                </div>
                
                <!-- Contribution Graph -->
                <div class="mb-4">
                    <div class="overflow-x-auto pb-2 mb-3 pt-6" use:scrollToLatestActivity>
                        <div class="contribution-graph" style="width: min(100%, 900px)">
                            <div class="flex">
                                <div class="w-8"></div>
                                <div class="relative text-xs text-gray-500 w-full h-4 mb-1">
                                    {#each monthLabels as { label, position }}
                                        <span class="absolute bottom-0" style="left: {position * 16}px">{label}</span>
                                    {/each}
                                </div>
                            </div>
                            
                            <div class="flex text-xs text-gray-500">
                                <div class="w-8 grid grid-rows-7 h-[112px] pr-2 text-right">
                                    <span class="self-center">Sun</span>
                                    <span class="self-center">Mon</span>
                                    <span class="self-center">Tue</span>
                                    <span class="self-center">Wed</span>
                                    <span class="self-center">Thu</span>
                                    <span class="self-center">Fri</span>
                                    <span class="self-center">Sat</span>
                                </div>
                                
                                <div class="grid grid-flow-col gap-1 w-full">
                                    {#each contributionWeeks as week}
                                        <div class="grid grid-rows-7 gap-1">
                                            {#each week as day}
                                                <div 
                                                    class="w-3 h-3 rounded-sm relative group cursor-pointer" 
                                                    class:bg-gray-700={day.level === 0}
                                                    class:bg-blue-900={day.level === 1}
                                                    class:bg-blue-700={day.level === 2}
                                                    class:bg-blue-600={day.level === 3}
                                                    class:bg-blue-500={day.level === 4}
                                                >
                                                    <div class="absolute transform -translate-x-1/2 bg-gray-800 text-xs text-gray-200 px-2 py-1 rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150 pointer-events-none whitespace-nowrap z-10"
                                                         style="left: 50%; {parseInt(day.date.split('-')[2]) < 15 ? 'top: -25px;' : 'bottom: 5px;'}">
                                                        {formatDate(day.date)}: {day.count} {day.count === 1 ? 'link' : 'links'}
                                                    </div>
                                                </div>
                                            {/each}
                                        </div>
                                    {/each}
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Legend - Separated from graph -->
                    <div class="flex justify-end items-center text-xs text-gray-500">
                        <span class="mr-1">Less</span>
                        <div class="w-3 h-3 rounded-sm bg-gray-700 mx-1"></div>
                        <div class="w-3 h-3 rounded-sm bg-blue-900 mx-1"></div>
                        <div class="w-3 h-3 rounded-sm bg-blue-700 mx-1"></div>
                        <div class="w-3 h-3 rounded-sm bg-blue-600 mx-1"></div>
                        <div class="w-3 h-3 rounded-sm bg-blue-500 mx-1"></div>
                        <span class="ml-1">More</span>
                    </div>
                </div>
                
                {#if contributionStats.bestDay.count > 0}
                    <p class="text-sm text-gray-400 mt-4">
                        Best day: <span class="text-gray-200">{formatDate(contributionStats.bestDay.date)}</span> with <span class="text-gray-200">{contributionStats.bestDay.count}</span> links
                    </p>
                {/if}
            </div>
            
            <!-- Security Section -->
            <div class="pt-6 border-t border-gray-700">
                <h2 class="text-xl font-medium mb-4">Security</h2>
                
                <button 
                    class="bg-gray-700 hover:bg-gray-600 text-gray-200 px-4 py-2 rounded transition-colors mb-4"
                    onclick={() => togglePasswordForm()}
                >
                    {showPasswordForm ? 'Cancel' : 'Change Password'}
                </button>
                
                {#if showPasswordForm}
                    <form action="?/changePassword" method="POST" use:enhance={handlePasswordUpdate} class="space-y-4 bg-gray-700 p-4 rounded">
                        <div class="space-y-2">
                            <label for="currentPassword" class="block text-sm font-medium text-gray-400">Current Password</label>
                            <input 
                                type="password" 
                                id="currentPassword" 
                                name="currentPassword" 
                                bind:value={currentPassword}
                                class="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                required
                            />
                        </div>
                        
                        <div class="space-y-2">
                            <label for="newPassword" class="block text-sm font-medium text-gray-400">New Password</label>
                            <input 
                                type="password" 
                                id="newPassword" 
                                name="newPassword" 
                                bind:value={newPassword}
                                class="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                required
                            />
                        </div>
                        
                        <div class="space-y-2">
                            <label for="confirmPassword" class="block text-sm font-medium text-gray-400">Confirm New Password</label>
                            <input 
                                type="password" 
                                id="confirmPassword" 
                                bind:value={confirmPassword}
                                class="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                required
                            />
                        </div>
                        
                        <div class="flex justify-end">
                            <button 
                                type="submit" 
                                class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition-colors"
                            >
                                Update Password
                            </button>
                        </div>
                        
                        {#if passwordUpdateSuccess}
                            <div class="bg-green-900/50 border border-green-800 text-green-200 px-4 py-2 rounded">
                                Password updated successfully
                            </div>
                        {/if}
                    </form>
                {/if}
            </div>
            
            <!-- Danger Zone -->
            <div class="pt-6 border-t border-gray-700">
                <h2 class="text-xl font-medium text-red-400 mb-4">Danger Zone</h2>
                
                <button 
                    class="bg-red-900 hover:bg-red-800 text-gray-200 px-4 py-2 rounded transition-colors"
                    onclick={() => toggleDeleteForm()}
                >
                    {showDeleteForm ? 'Cancel' : 'Delete Account'}
                </button>
                
                {#if showDeleteForm}
                    <form action="?/deleteAccount" method="POST" class="mt-4 space-y-4 bg-red-900/20 border border-red-800 p-4 rounded">
                        <p class="text-gray-300">This action cannot be undone. All your data will be permanently deleted.</p>
                        
                        <div class="space-y-2">
                            <label for="confirmDelete" class="block text-sm font-medium text-gray-400">
                                Type <span class="font-mono bg-gray-800 px-1 py-0.5 rounded">DELETE</span> to confirm
                            </label>
                            <input 
                                type="text" 
                                id="confirmDelete" 
                                name="confirmDelete" 
                                bind:value={deleteConfirmation}
                                class="w-full bg-gray-700 border border-red-800 rounded px-3 py-2 text-gray-200 focus:outline-none focus:ring-1 focus:ring-red-500"
                            />
                        </div>
                        
                        <div class="flex justify-end">
                            <button 
                                type="submit" 
                                class="bg-red-700 hover:bg-red-600 text-white px-4 py-2 rounded transition-colors"
                                disabled={deleteConfirmation !== 'DELETE'}
                            >
                                Permanently Delete Account
                            </button>
                        </div>
                    </form>
                {/if}
            </div>
            
            <!-- Error Messages -->
            {#if errorMessage}
                <div class="bg-red-900/50 border border-red-800 text-red-200 px-4 py-2 rounded">
                    {errorMessage}
                </div>
            {/if}
        </div>
    </main>
</div>

<style>
    /* Fix for grid layout */
    .grid-rows-7 {
        grid-template-rows: repeat(7, minmax(0, 1fr));
    }
</style>
