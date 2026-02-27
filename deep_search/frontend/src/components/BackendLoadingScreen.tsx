export const BackendLoadingScreen = () => (
    <div className="flex-1 flex flex-col items-center justify-center p-4 overflow-hidden relative">
        <div className="w-full max-w-2xl z-10
                    bg-neutral-900/50 backdrop-blur-md 
                    p-8 rounded-2xl border border-neutral-700 
                    shadow-2xl shadow-black/60">

            <div className="text-center space-y-6">
                <h1 className="text-4xl font-bold text-white flex items-center justify-center gap-3">
                    ✨ Deep Search - ADK 🚀
                </h1>

                <div className="flex flex-col items-center space-y-4">
                    {/* Spinning animation */}
                    <div className="relative">
                        <div className="w-16 h-16 border-4 border-neutral-600 border-t-blue-500 rounded-full animate-spin"></div>
                        <div className="absolute inset-0 w-16 h-16 border-4 border-transparent border-r-purple-500 rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
                    </div>

                    <div className="space-y-2">
                        <p className="text-xl text-neutral-300">
                            Waiting for backend to be ready...
                        </p>
                        <p className="text-sm text-neutral-400">
                            This may take a moment on first startup
                        </p>
                    </div>

                    {/* Animated dots */}
                    <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-pink-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
);
