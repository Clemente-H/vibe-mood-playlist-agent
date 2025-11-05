"use client"

import { useState , useEffect } from "react"
import { MusicPlayer } from "@/components/MusicPlayer/MusicPlayer";
import { ChatDock } from "@/components/ChatDock/ChatDock";
import { ThemeToggler } from "@/components/ThemeToggler/ThemeToggler";
import { AnimatePresence, motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { SpotifyModal } from "@/components/SpotifyLogger/SpotifyLogger";
import { EmotionGuide } from "@/components/EmotionsGuide/EmotionsGuide";

export default function MoodPlayer() {

  const [theme, setTheme] = useState("light");
  const [text, setText] = useState("");
  const [gradientColors, setGradientColors] = useState(["#51a2ff", "#ad46ff", "#f6339a", "#51a2ff", "#ad46ff"]);
  const [showWelcomeMessage, setShowWelcomeMessage] = useState(true);
  const [showEmotionGuide, setShowEmotionGuide] = useState(false);
  const [showSpotifyModal, setShowSpotifyModal] = useState(true);

  const newGradientColor = () => {
    
    const newColor = `#${Math.floor(Math.random()*16777215).toString(16).padStart(6, '0')}`;
    setGradientColors((prevColors) => {
      const updatedColors = [...prevColors, newColor];
      if (updatedColors.length > 5) {
        updatedColors.shift(); // Keep only the last 5 colors
      }
      return updatedColors;
    });
  }

  const handleSpotifyLoginSuccess = () => {
    setShowSpotifyModal(false);
    setShowEmotionGuide(true);
  }

  const handleMessage = (message) => {
    setText(message);
    newGradientColor();
    if (showEmotionGuide) {
      setShowEmotionGuide(false);
    }
  }

  const toggleTheme = () => {
    setTheme(theme === "light" ? "dark" : "light");
  }

  useEffect(() => {
    const hasVisited = localStorage.getItem("hasVisited")
    if (!hasVisited) {
      setShowSpotifyModal(true)
      localStorage.setItem("hasVisited", "true")
    }
  }, [])

  return (
    <div className="overflow-hidden h-dvh w-dvw">

      <AnimatePresence>
        <motion.div
          className="animate-gradient" 
          key="background"
          style={{
              "--gc1": gradientColors[0],
              "--gc2": gradientColors[1],
              "--gc3": gradientColors[2],
              "--gc4": gradientColors[3],
              "--gc5": gradientColors[4],
          }}
          animate={{
            filter: theme === "light" ? "brightness(100%)" : "brightness(60%)",
            "--gc1": gradientColors[0],
            "--gc2": gradientColors[1],
            "--gc3": gradientColors[2],
            "--gc4": gradientColors[3],
            "--gc5": gradientColors[4],
          }}
          transition={{ duration: 2, ease: "easeInOut" }}
        />
        <div className="fixed right-4 top-4 z-99" key="theme-toggler">
          <ThemeToggler theme={theme} onToggle={toggleTheme} />
        </div>

        {showWelcomeMessage?
          <motion.div
            className="relative z-10 flex min-h-screen flex-col items-center justify-center px-4"
            key="welcome-text"
            initial={{
              opacity: 0, 
              scale: 0.7
            }}
            animate={{ 
              opacity: 1,
              scale: 1,
              transition: {
                duration: 3,
                ease: "easeInOut"
              }
            }}
            exit={{
              opacity: 0,
              top: "-10%",
              transition:{
                duration: 1.5,
                ease: "easeInOut"
              } 
            }}
          >
            <div className="text-center">
              <h1 className="mb-4 text-balance text-5xl font-bold text-white md:text-7xl">
                Welcome to <span className="vibe-font text-5xl md:text-7xl">Vibe.FM</span> 
              </h1>
              <div className="text-pretty mt-10 font-medium text-white/90 md:text-xl">
                <p className="mb-2">Discover music that flows with your emotions.</p>
                <p className="mb-2">Tell me how you’re feeling today, and I’ll create a personalized Spotify queue</p>
                <p className="mb-2">that matches your mood 🎧</p>
              </div>
            </div>

            <Button
              size="lg"
              variant="default"
              className="mt-8 bg-white/20 text-white hover:bg-white/30"
              onClick={() => setShowWelcomeMessage(false)}
            >
              Start Chatting
            </Button>

          </motion.div>
          :
          showSpotifyModal?
            <motion.div
              key="modals"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 , transition: { duration: 1, delay: 1.5, ease: "easeInOut" } }}
              exit={{ opacity: 0 , transition: { duration: 1, ease: "easeInOut" } }}
            >
              <SpotifyModal onClose={() => handleSpotifyLoginSuccess()} key="spotify-modal"/>
            </motion.div>
            :
            <AnimatePresence>
              {
                showEmotionGuide?
                  <motion.div
                    key="emotion-guide"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 , transition: { duration: 1, delay: 1.5, ease: "easeInOut" } }}
                    exit={{ opacity: 0 , transition: { duration: 1, ease: "easeInOut" } }}
                  >
                    <EmotionGuide />
                  </motion.div>
                :
                  <MusicPlayer key="music-player"/>
              }
              <ChatDock messageHandler={handleMessage} key="docked-chat"/>
            </AnimatePresence>
        }
      </AnimatePresence>
    </div>
  );
}
