<script lang="ts">
    export let showLogout = false;
</script>

<header class="bg-gray-800 py-4 px-6 flex justify-between items-center">
    <div class="flex items-center gap-6">
        <a href="/stash" class="text-2xl font-bold hover:text-gray-300">stash</a>
        <a href="/docs" class="text-gray-400 hover:text-white">docs</a>
    </div>
    {#if showLogout}
        <div class="flex items-center gap-4">
            <a href="/profile" class="text-gray-400 hover:text-white">profile</a>
            <form action="?/logout" method="POST">
                <button type="submit" class="text-gray-400 hover:text-white">
                    logout
                </button>
            </form>
        </div>
    {/if}
</header>