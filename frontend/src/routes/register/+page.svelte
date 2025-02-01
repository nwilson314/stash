<!-- src/routes/register/+page.svelte -->
<script lang="ts">
    import { enhance } from '$app/forms';
  
    let email = '';
    let password = '';
</script>

<div class="min-h-screen flex flex-col justify-center items-center p-4">
    <h2 class="text-2xl mb-4">create your stash</h2>
    
    <form method="POST" use:enhance class="flex flex-col gap-4 w-64">
        <input
            class="border p-2 rounded"
            type="email"
            name="email"
            placeholder="email"
            bind:value={email}
            required
        />
        <input
            class="border p-2 rounded"
            type="password"
            name="password"
            placeholder="password"
            bind:value={password}
            required
        />
        <button type="submit" class="bg-blue-500 text-white p-2 rounded">
            create account
        </button>
    </form>
</div>