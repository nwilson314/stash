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
  
<div class="min-h-screen bg-gray-900 text-gray-100">
    <!-- Hero Section -->
    <section class="py-16 px-4 sm:px-6 lg:px-8 flex flex-col items-center">
        <h1 class="text-4xl sm:text-5xl font-bold tracking-tight text-center">
            Capture now. Read smarter later.
        </h1>
        <p class="mt-4 max-w-2xl text-center text-gray-400 text-lg">
            Effortlessly save links from anywhere and let AI organize your digital knowledge.
        </p>
        
        <!-- Hero Image -->
        <div class="mt-8 w-full max-w-xs mx-auto rounded-lg overflow-hidden shadow-lg">
            <img src="/stash.webp" alt="Stash App Interface" class="w-full h-auto object-cover opacity-90"  />
        </div>
        
        <!-- CTA Buttons -->
        <div class="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
            <button class="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-md text-lg font-medium transition-colors" on:click={goToRegister}>
                Get Started
            </button>
            <button class="px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-md text-lg font-medium transition-colors" on:click={goToLogin}>
                Log In
            </button>
        </div>
        
        <!-- <p class="mt-4 text-sm text-gray-500">
            No credit card required • Set up in 30 seconds
        </p> -->
    </section>
    
    <!-- Features Section -->
    <section class="py-16 px-4 sm:px-6 lg:px-8 bg-gray-800">
        <div class="max-w-7xl mx-auto">
            <h2 class="text-3xl font-bold text-center mb-12">Why Stash?</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                <!-- Feature 1 -->
                <div class="bg-gray-900 p-6 rounded-lg">
                    <div class="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold mb-2">Frictionless Capture</h3>
                    <p class="text-gray-400">Save links in one click from any browser or device. No more open tabs or forgotten bookmarks.</p>
                </div>
                
                <!-- Feature 2 -->
                <div class="bg-gray-900 p-6 rounded-lg">
                    <div class="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold mb-2">AI-Powered Organization</h3>
                    <p class="text-gray-400">Links automatically categorized by content. Find what you need when you need it.</p>
                </div>
                
                <!-- Feature 3 -->
                <div class="bg-gray-900 p-6 rounded-lg">
                    <div class="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold mb-2">Smart Summaries</h3>
                    <p class="text-gray-400">Get AI-generated summaries of any link on demand. Know what's important without reading everything.</p>
                </div>
                
                <!-- Feature 4 -->
                <div class="bg-gray-900 p-6 rounded-lg">
                    <div class="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold mb-2">Weekly Digests</h3>
                    <p class="text-gray-400">Receive personalized newsletters summarizing your unread content. Stay on top of what matters to you.</p>
                </div>
            </div>
        </div>
    </section>
    
    <!-- How It Works Section -->
    <section class="py-16 px-4 sm:px-6 lg:px-8">
        <div class="max-w-7xl mx-auto">
            <h2 class="text-3xl font-bold text-center mb-12">Simple by Design</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <!-- Step 1 -->
                <div class="flex flex-col items-center text-center">
                    <div class="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-4 text-2xl font-bold">1</div>
                    <h3 class="text-xl font-semibold mb-2">Save</h3>
                    <p class="text-gray-400">One-click saving from browser extensions, iOS shortcuts, or web interface.</p>
                </div>
                
                <!-- Step 2 -->
                <div class="flex flex-col items-center text-center">
                    <div class="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-4 text-2xl font-bold">2</div>
                    <h3 class="text-xl font-semibold mb-2">Organize</h3>
                    <p class="text-gray-400">AI automatically categorizes links and generates summaries.</p>
                </div>
                
                <!-- Step 3 -->
                <div class="flex flex-col items-center text-center">
                    <div class="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-4 text-2xl font-bold">3</div>
                    <h3 class="text-xl font-semibold mb-2">Read</h3>
                    <p class="text-gray-400">Access your links anytime, anywhere, with a clean, distraction-free interface.</p>
                </div>
            </div>
        </div>
    </section>
    
    <!-- AI Features Spotlight -->
    <section class="py-16 px-4 sm:px-6 lg:px-8 bg-gray-800">
        <div class="max-w-7xl mx-auto">
            <h2 class="text-3xl font-bold text-center mb-12">AI-Powered Features</h2>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <div class="space-y-8">
                    <div>
                        <h3 class="text-xl font-semibold mb-2">Automatic Categorization</h3>
                        <p class="text-gray-400">Stash analyzes your links and assigns relevant categories, saving you the hassle of manual organization.</p>
                    </div>
                    
                    <div>
                        <h3 class="text-xl font-semibold mb-2">On-Demand Summaries</h3>
                        <p class="text-gray-400">Get the gist of any article with one click. Perfect for deciding what to read next or refreshing your memory.</p>
                    </div>
                    
                    <div>
                        <h3 class="text-xl font-semibold mb-2">Weekly Digest Emails</h3>
                        <p class="text-gray-400">Receive personalized newsletters with summaries of your unread content, curated by AI to match your interests.</p>
                    </div>
                </div>
                
                <!-- AI Demo Visualization -->
                <div class="bg-gray-900 p-6 rounded-lg shadow-lg">
                    <div class="aspect-w-16 aspect-h-9 rounded-md overflow-hidden">
                        <div class="w-full h-full bg-gray-700 flex items-center justify-center">
                            <!-- Placeholder for demo animation/image -->
                            <div class="text-center p-4">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-blue-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                </svg>
                                <p class="text-gray-300 text-lg">AI analyzes your content to provide smart organization and insights</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- Integration Showcase -->
    <section class="py-16 px-4 sm:px-6 lg:px-8">
        <div class="max-w-7xl mx-auto">
            <h2 class="text-3xl font-bold text-center mb-12">Fits Into Your Life</h2>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
                <!-- Browser Extensions -->
                <div class="bg-gray-800 p-6 rounded-lg text-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                    </svg>
                    <h3 class="text-lg font-semibold mb-2">Browser Extensions</h3>
                    <p class="text-gray-400">Save directly from your browser with our extensions.</p>
                </div>
                
                <!-- Mobile -->
                <div class="bg-gray-800 p-6 rounded-lg text-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    <h3 class="text-lg font-semibold mb-2">Mobile</h3>
                    <p class="text-gray-400">Use iOS Shortcuts to save from any app with the share menu.</p>
                </div>
                
                <!-- Email -->
                <div class="bg-gray-800 p-6 rounded-lg text-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <h3 class="text-lg font-semibold mb-2">Email</h3>
                    <p class="text-gray-400">Forward links to your personal Stash email address.</p>
                    <span class="inline-block mt-2 px-2 py-1 bg-blue-900 text-xs text-blue-300 rounded-full">Coming Soon</span>
                </div>
                
                <!-- API -->
                <div class="bg-gray-800 p-6 rounded-lg text-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                    </svg>
                    <h3 class="text-lg font-semibold mb-2">API</h3>
                    <p class="text-gray-400">Integrate with your own tools using our developer API.</p>
                    <span class="inline-block mt-2 px-2 py-1 bg-blue-900 text-xs text-blue-300 rounded-full">Coming Soon</span>
                </div>
            </div>
        </div>
    </section>
    
    <!-- Testimonials -->
    <section class="py-16 px-4 sm:px-6 lg:px-8 bg-gray-800">
        <div class="max-w-7xl mx-auto">
            <h2 class="text-3xl font-bold text-center mb-12">What Users Say</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <!-- Testimonial 1 -->
                <div class="bg-gray-900 p-6 rounded-lg">
                    <p class="text-gray-300 italic mb-4">"Stash has replaced my chaotic bookmarks and open tabs. The AI categorization is surprisingly accurate."</p>
                    <p class="text-gray-400 font-medium">- Alex K., Researcher</p>
                </div>
                
                <!-- Testimonial 2 -->
                <div class="bg-gray-900 p-6 rounded-lg">
                    <p class="text-gray-300 italic mb-4">"The weekly digest emails help me stay on top of industry news without getting overwhelmed."</p>
                    <p class="text-gray-400 font-medium">- Jamie T., Product Manager</p>
                </div>
                
                <!-- Testimonial 3 -->
                <div class="bg-gray-900 p-6 rounded-lg">
                    <p class="text-gray-300 italic mb-4">"I use Stash to collect research for my writing. The AI summaries save me hours of reading time."</p>
                    <p class="text-gray-400 font-medium">- Morgan L., Content Creator</p>
                </div>
            </div>
        </div>
    </section>
    
    <!-- Final CTA -->
    <section class="py-16 px-4 sm:px-6 lg:px-8">
        <div class="max-w-3xl mx-auto text-center">
            <h2 class="text-3xl font-bold mb-6">Start stashing today</h2>
            <p class="text-gray-400 text-lg mb-8">Join thousands of users who have simplified their digital reading experience.</p>
            
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
                <button class="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-md text-lg font-medium transition-colors" on:click={goToRegister}>
                    Create Your Stash
                </button>
                <button class="px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-md text-lg font-medium transition-colors" on:click={goToLogin}>
                    Log In
                </button>
            </div>
        </div>
    </section>
    
    <!-- Footer -->
    <footer class="py-8 px-4 sm:px-6 lg:px-8 bg-gray-800">
        <div class="max-w-7xl mx-auto text-center">
            <p class="text-sm text-gray-500">
                2025 Stash. All rights reserved.
            </p>
        </div>
    </footer>
</div>