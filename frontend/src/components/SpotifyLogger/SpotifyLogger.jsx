"use client"

export function SpotifyModal({ onLogin }) {

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl bg-linear-to-br from-gray-900 to-black p-8 shadow-2xl">
        {/* Spotify Icon */}
        <img
            src="/spotify_logo.png"
            alt="Spotify Logo"
            className="mx-auto mb-6 h-16 w-16"
        />
        {/* Title */}
        <h2 className="mb-2 text-center font-bold text-2xl text-white">Welcome to <span className="vibe-font">Vibe.FM</span></h2>
        <p className="mb-8 text-center font-bold text-gray-400">Connect your Spotify account to get started</p>

        {/* Login Button */}
        <button 
          className="w-full rounded-full bg-green-500 py-3 font-bold text-black transition-all duration-200 hover:bg-green-400 hover:scale-105"
          onClick={onLogin}  
        >
          Login with Spotify
        </button>

        {/* Close Button 
        <button
          onClick={onClose}
          className="mt-4 w-full rounded-full border border-gray-600 py-3 font-bold text-gray-300 transition-all duration-200 hover:border-gray-400 hover:text-white"
        >
          Skip for now
        </button>
        */}
      </div>
    </div>
  )
}