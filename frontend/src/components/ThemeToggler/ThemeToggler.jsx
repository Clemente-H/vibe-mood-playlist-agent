"use client"

import { Moon, Sun } from "lucide-react"
import { Button } from "@/components/ui/button"

export function ThemeToggler({ theme, onToggle }) {
  return (
    <Button
      onClick={onToggle}
      size="icon"
      variant="ghost"
      className="bg-white/20 text-white hover:bg-white/30 backdrop-blur-sm"
    >
      {theme === "light" ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}