"use client"

import { useState } from "react"
import { ColorWaves } from "@/components/ColorWaves/ColorWaves";
import { ChatDock } from "@/components/ChatDock/ChatDock";
import { ThemeToggler } from "@/components/ThemeToggler/ThemeToggler";
import { AnimatePresence, motion } from "framer-motion";

export default function MoodPlayer() {

  const [theme, setTheme] = useState("light");
  const [text, setText] = useState("");
  const [waves, setWaves] = useState([])

  const createWave = () => {
    setWaves((prev) => {
      // id creciente aunque se eliminen elementos
      const nextId = (prev[prev.length - 1]?.id ?? -1) + 1;

      const newWave = {
        id: nextId,
        borderRadius: Math.random() * 5 + 40,
        color: `rgba(${Math.floor(Math.random() * 256)}, ${Math.floor(
          Math.random() * 256
        )}, ${Math.floor(Math.random() * 256)})`,
        duration: Math.random() * 2 + 5,
      };

      // Encolar y mantener solo los últimos MAX (cola FIFO)
      const trimmed = [...prev, newWave].slice(-5);

      console.log("Waves updated:", trimmed);

      // Recalcular verticalPosition para TODOS según su índice actual
      return trimmed.map((w, i) => ({
        ...w,
        verticalPosition: 80 - i * 20,
      }));
    });
  }

  const handleMessage = (message) => {
    setText(message);
    createWave();
    console.log("Received message in page:", message);
  }

  const toggleTheme = () => {
    setTheme(theme === "light" ? "dark" : "light");
  }

  const gradientClass =
    theme === "light"
      ? "bg-gradient-to-br from-blue-400 via-purple-500 to-pink-500"
      : "bg-gradient-to-br from-blue-900 via-purple-900 to-pink-900"

  return (
    <div className="overflow-hidden h-dvh w-dvw">
      {/* Animated gradient background */}
      <AnimatePresence>
        <div
          className={`fixed inset-0 animate-gradient ${gradientClass}`} 
          key="background"
        />
        <div className="fixed right-4 top-4 z-20" key="theme-toggler">
          <ThemeToggler theme={theme} onToggle={toggleTheme} />
        </div>

        {/* Content area */}

        {waves.length?
          <ColorWaves
            key="waves-component" 
            waves={waves}
          />
          :
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
                duration: 3
              }
            }}
            exit={{
              opacity: 0,
              top: "-10%",
              transition:{
                duration: 1.5
              } 
            }}
          >
            <div className="text-center">
              <h1 className="mb-4 text-balance text-5xl font-bold text-white md:text-7xl">Welcome</h1>
              <p className="text-pretty text-lg text-white/90 md:text-xl">Start a conversation below</p>
            </div>
          </motion.div>
        }

        {/* Chatbot input docked at bottom */}
        <ChatDock
          messageHandler={handleMessage}
          key="docked-chat"
        />
      </AnimatePresence>
    </div>
  );
}
