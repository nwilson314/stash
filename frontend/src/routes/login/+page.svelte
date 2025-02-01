<!-- src/routes/login/+page.svelte -->
<script lang="ts">
    import { enhance } from '$app/forms';
    import { goto } from '$app/navigation';
    import type { ActionResult } from '@sveltejs/kit';
  
    let email = '';
    let password = '';

    const handleSubmit = () => {
      console.log('submitting')
        return async ({ result }: { result: ActionResult }) => {
            if (result.type === 'redirect') {
              console.log("redirecting to ", result.location)
                goto(result.location);
            }
        };
    };
</script>

<div class="min-h-screen bg-gray-900 text-gray-200 flex flex-col justify-center items-center p-4">
    <h2 class="text-2xl mb-4 font-bold">login to your stash</h2>
    
    <form method="POST" use:enhance={handleSubmit} class="flex flex-col gap-4 w-64">
        <input
            class="bg-gray-800 border border-gray-700 p-2 rounded text-white"
            type="email"
            name="email"
            placeholder="email"
            bind:value={email}
            required
        />
        <input
            class="bg-gray-800 border border-gray-700 p-2 rounded text-white"
            type="password"
            name="password"
            placeholder="password"
            bind:value={password}
            required
        />
        <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded">
            login
        </button>
    </form>

    <p class="mt-4 text-gray-400">
        not stashing? <a href="/register" class="text-blue-400 hover:text-blue-300">register</a>
    </p>
</div>