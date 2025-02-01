<script lang="ts">
    import Header from '$lib/Header.svelte';
</script>

<div class="min-h-screen bg-gray-900 text-gray-200">
    <Header showLogout={false} />
    <main class="max-w-3xl mx-auto p-4 space-y-8">
        <h1 class="text-2xl font-bold mb-4">Documentation</h1>
        
        <section class="space-y-4">
            <h2 class="text-xl font-semibold">iOS Shortcut Setup</h2>
            <p class="text-gray-300">Follow these steps to create an iOS Shortcut for quickly saving links to stash:</p>
            
            <ol class="list-decimal list-inside space-y-4 text-gray-300">
                <li>Open the <code class="bg-gray-700 px-1 py-0.5 rounded">Shortcuts</code> app and create a new shortcut</li>
                
                <li class="space-y-2">
                    Add a <code class="bg-gray-700 px-1 py-0.5 rounded">Get Contents of URL</code> action and configure it:
                    <ul class="list-disc list-inside ml-6 text-gray-400">
                        <li>URL: <code class="bg-gray-800 px-2 py-0.5 rounded">https://stash-link.fly.dev/users/login</code></li>
                        <li>Method: POST</li>
                        <li>Request Body: JSON with your username and password fields</li>
                    </ul>
                </li>
                
                <li>Add a <code class="bg-gray-700 px-1 py-0.5 rounded">Get Dictionary Value</code> action to extract the <code class="bg-gray-700 px-1 py-0.5 rounded">access_token</code> from the login response</li>
                
                <li class="space-y-2">
                    Add another <code class="bg-gray-700 px-1 py-0.5 rounded">Get Contents of URL</code> action:
                    <ul class="list-disc list-inside ml-6 text-gray-400">
                        <li>URL: <code class="bg-gray-800 px-2 py-0.5 rounded">https://stash-link.fly.dev/links/save</code></li>
                        <li>Method: POST</li>
                        <li>Headers: Add <code class="bg-gray-800 px-2 py-0.5 rounded">authorization</code> with value <code class="bg-gray-800 px-2 py-0.5 rounded">bearer &lbrace;access_token&rbrace;</code></li>
                        <li>Request Body: Add parameters:
                            <ul class="list-disc list-inside ml-6">
                                <li>url: "Shortcut Input"</li>
                                <li>note: "Ask Each Time"</li>
                            </ul>
                        </li>
                    </ul>
                </li>
            </ol>
            
            <br>
            <p class="text-gray-400 mt-4">Alternatively, you can download the shortcut from the link below and add it to your iOS share sheet.</p>
            <p class="text-gray-400">Just be sure to update the username and password fields with your own.</p>
            
            <div class="mt-8 text-center">
                <a href="https://www.icloud.com/shortcuts/aa3aa9f290cd463ab4e2016f3d7c3705" 
                   class="inline-block bg-gray-800 hover:bg-gray-700 text-gray-200 px-6 py-3 rounded-lg transition-colors">
                    ↓ Download the Shortcut
                </a>
            </div>
        </section>
    </main>
</div>