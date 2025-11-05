"use client"

import { useState, useEffect } from "react"
import { Play, Pause, SkipForward, SkipBack } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { motion } from "framer-motion"

export function MusicPlayer() {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const totalDuration = 243 // 4:03 in seconds

  useEffect(() => {
    let interval
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentTime((prev) => {
          if (prev >= totalDuration) {
            setIsPlaying(false)
            return 0
          }
          return prev + 1
        })
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [isPlaying])

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  const progressPercentage = (currentTime / totalDuration) * 100

  // Sample data - can be replaced with real data
  const currentSong = {
    title: "Playing God",
    artist: "Paramore",
    coverUrl: "/cat-slave.png",
  }

  const queue = [
    { id: 1, title: "Blue and Yellow", artist: "The Used", duration: "4:12" },
    { id: 2, title: "Torero", artist: "Chayanne", duration: "3:28" },
    { id: 3, title: "Beautiful lie", artist: "30 Seconds to Mars", duration: "5:01" },
    { id: 4, title: "Digital Waves", artist: "Synth Valley", duration: "3:55" },
  ]

  return (
    <motion.div
      className="fixed left-1/2 top-1/2 z-10 w-full max-w-sm -translate-x-1/2 -translate-y-1/2 px-4 sm:max-w-md sm:px-6"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1, transition: { duration: 1 , delay: 1.5 } }}
    >
      <div className="rounded-lg border border-white/20 bg-white/10 p-4 backdrop-blur-lg sm:p-6">
        <div className="mb-4 flex justify-center sm:mb-6">
          <img
            src={currentSong.coverUrl || "/placeholder.svg"}
            alt="Album cover"
            className="h-40 w-40 rounded-lg object-cover shadow-lg sm:h-48 sm:w-48"
          />
        </div>

        {/* Current Song */}
        <div className="mb-4 sm:mb-6">
          <div className="mb-3 text-center sm:mb-4">
            <h3 className="text-lg font-bold text-white sm:text-xl">{currentSong.title}</h3>
            <p className="text-xs font-semibold text-white/70 sm:text-sm">{currentSong.artist}</p>
          </div>

          <div className="mb-2 flex justify-between text-xs font-semibold text-white/70">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(totalDuration)}</span>
          </div>

          <div className="mb-3 h-1 w-full overflow-hidden rounded-full bg-white/20 sm:mb-4">
            <div
              className="h-full bg-white/60 transition-all duration-300"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>

          {/* Controls */}
          <div className="flex items-center justify-center gap-3 sm:gap-4">
            <Button
              size="icon"
              variant="ghost"
              className="h-10 w-10 text-white hover:bg-white/20 hover:text-white sm:h-auto sm:w-auto"
            >
              <SkipBack className="h-4 w-4 sm:h-5 sm:w-5" />
            </Button>
            <Button
              size="icon"
              className="h-10 w-10 bg-white/20 text-white hover:bg-white/30 sm:h-12 sm:w-12"
              onClick={() => setIsPlaying(!isPlaying)}
            >
              {isPlaying ? <Pause className="h-5 w-5 sm:h-6 sm:w-6" /> : <Play className="h-5 w-5 sm:h-6 sm:w-6" />}
            </Button>
            <Button
              size="icon"
              variant="ghost"
              className="h-10 w-10 text-white hover:bg-white/20 hover:text-white sm:h-auto sm:w-auto"
            >
              <SkipForward className="h-4 w-4 sm:h-5 sm:w-5" />
            </Button>
          </div>
        </div>

        {/* Queue */}
        <div className="border-t border-white/20 pt-3 sm:pt-4">
          <h4 className="mb-2 text-xs font-bold uppercase tracking-wide text-white/70 sm:mb-3 sm:text-sm">Up Next</h4>
          <ScrollArea className="h-40 sm:h-48">
            <div className="space-y-2">
              {queue.map((song) => (
                <div
                  key={song.id}
                  className="flex items-center justify-between rounded-md p-2 transition-colors hover:bg-white/10 sm:p-3"
                >
                  <div className="flex-1">
                    <p className="text-xs font-bold text-white sm:text-sm">{song.title}</p>
                    <p className="text-xs font-semibold text-white/60">{song.artist}</p>
                  </div>
                  <span className="text-xs font-semibold text-white/60">{song.duration}</span>
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>
      </div>
    </motion.div>
  )
}
