"use client"

export function EmotionGuide() {

  const emotionTips = [
    {
      title: "Be Clear",
      description: "Share your feelings with more precise words — instead of sad or happy, try melancholic, hopeful, or full of energy",
    },
    {
      title: "Use Descriptions",
      description: "Add some color with adjectives like calm and peaceful, intense and powerful, or nostalgic and dreamy",
    },
    {
      title: "Mention Genres or Artists",
      description: "For example: lo-fi hip-hop vibes, alt-pop energy, or indie rock feel",
    },
    {
      title: "Give Some Context",
      description: "Tell me what you’re up to: studying, relaxing, working out, or on a road trip",
    },
    {
      title: "Mix Emotions",
      description: "Combine feelings like uplifting yet introspective, chill but focused, or relaxed with a hint of nostalgia",
    },
  ]

  return (
    <div className="fixed inset-0 flex items-center justify-center z-9 px-4">
      <div className="backdrop-blur-md bg-white/20 dark:bg-black/30 border border-white/30 rounded-2xl p-8 max-w-2xl w-full shadow-2xl">
        <h2 className="text-3xl font-bold text-white mb-2 text-center">Tell Me How You Feel</h2>
        <p className="text-white/80 text-center mb-8 font-semibold">
          Find songs that truly match your mood
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {emotionTips.map((tip, index) => (
            <div
              key={index}
              className="bg-white/10 hover:bg-white/15 transition-all rounded-lg p-4 border border-white/20"
            >
              <h3 className="font-bold text-white mb-2 text-lg">{tip.title}</h3>
              <p className="text-white/70 font-semibold text-sm leading-relaxed">{tip.description}</p>
            </div>
          ))}
        </div>

        <div className="mt-8 text-center">
          <p className="text-white/90 font-semibold text-sm">
            🎧 Start chatting to get music that fits your moment 🎧
          </p>
        </div>
      </div>
    </div>
  )
}