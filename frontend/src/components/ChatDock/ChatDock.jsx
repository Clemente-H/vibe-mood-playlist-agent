"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send } from "lucide-react"
import { motion } from "framer-motion"

export function ChatDock({ messageHandler }) {
  const [message, setMessage] = useState("")

  const handleSubmit = (e) => {
    e.preventDefault()
    if (message.trim()) {
      console.log("Message sent:", message);
      messageHandler(message);
      setMessage("");
    }
  }

  return (
    <motion.div 
      className="fixed bottom-0 left-0 right-0 z-20 border-t border-white/20 bg-white/10 p-4 backdrop-blur-lg"
      initial={{ y: "100%" }}
      animate={{
        y: 0,
        transition: {
          duration: 1,
          delay: 1.5,
          ease: "easeInOut"
        }
      }} 
      key="chat-dock"
    >
      <div className="mx-auto max-w-4xl">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            type="text"
            placeholder="Tell me your mood..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="flex-1 border-white/30 bg-white/20 text-white font-bold placeholder:text-white/60 focus-visible:ring-white/50"
          />
          <Button type="submit" size="icon" className="bg-white/20 text-white hover:bg-white/30">
            <Send className="h-4 w-4" />
            <span className="sr-only">Send message</span>
          </Button>
        </form>
      </div>
    </motion.div>
  )
}
