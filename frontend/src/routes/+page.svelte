<!-- src/routes/+page.svelte -->
<script>
    import { goto } from '$app/navigation';
  
    function goToLogin() {
      goto('/login');
    }
    function goToRegister() {
      goto('/register');
    }
  </script>
  
  <div class="min-h-screen bg-gray-900 text-gray-100 flex flex-col items-center justify-center p-6 gap-4">
    <h1 class="text-3xl font-bold tracking-wide">stash links</h1>
    <p class="max-w-md text-center text-gray-400">
      ephemeral capturing. frictionless reading. 
      <br />
      stash your links.
    </p>
    
    <div class="flex gap-4 mt-4">
      <button class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded" onclick={goToLogin}>
        login
      </button>
      <button class="px-4 py-2 bg-gray-700 hover:bg-gray-800 rounded" onclick={goToRegister}>
        register
      </button>
    </div>
  
    <div class="mt-8 text-sm text-gray-500">
      keep shipping
    </div>
  </div>
  