"use client"

import { useState , useEffect } from "react"
import { MusicPlayer } from "@/components/MusicPlayer/MusicPlayer";
import { ChatDock } from "@/components/ChatDock/ChatDock";
import { ThemeToggler } from "@/components/ThemeToggler/ThemeToggler";
import { AnimatePresence, motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { SpotifyModal } from "@/components/SpotifyLogger/SpotifyLogger";
import { EmotionGuide } from "@/components/EmotionsGuide/EmotionsGuide";
import { toast } from "sonner"
import api from "@/lib/api";

export default function VibeFM() {

  const BACKEND = process.env.NEXT_PUBLIC_API_BASE;

  const [theme, setTheme] = useState("light");
  const [token, setToken] = useState('');
  const [queue, setQueue] = useState('');
  const [agentMessage, setAgentMessage] = useState('');
  const [validTracks, setValidTracks] = useState(0);
  const [device, setDevice] = useState('');
  const [gradientColors, setGradientColors] = useState(["#51a2ff", "#ad46ff", "#f6339a", "#51a2ff", "#ad46ff"]);
  const [showWelcomeMessage, setShowWelcomeMessage] = useState(true);
  const [showEmotionGuide, setShowEmotionGuide] = useState(true);
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
  };

  const handleDevice = async (device) => {
    setDevice(device);
    // Transfer playback session to the web browser
    await api.post("/spotify/transfer_playback", { "device_id": device })
    .catch((error) => {
      console.log(error);
    });
  };

  const handleUpdateQueue = async () => {
    await loadQueue(validTracks-1);
    setValidTracks(validTracks-1);
  }

  const loadQueue = async (tracks) => {
    // Get actual queue
    await api.get("/spotify/queue")
      .then((res) => {
        setQueue(res.data.queue.slice(0,tracks));
      })
      .catch((error) => {
        console.log(error);
      });
  }

  const handleMessage = async (message) => {
 
    // newGradientColor();
    if (showEmotionGuide) {
      setShowEmotionGuide(false);
    }

    const id = toast.loading("Generating your vibe playlist…");
    
    try {

      // Generate songs queue
      await api.post('/chat', { message })
      .then((res) => {
        setAgentMessage(res.data.message);
        setValidTracks(res.data.valid_tracks + 1 + validTracks);
        loadQueue(res.data.valid_tracks + 1 + validTracks);
      })
      .catch((error) => {
        console.log(error);
        setAgentMessage("An error has occurred with our service. Please try again.");
      });

      toast.success(`Thats it! I hope you like it c:`, { id });

    }
    catch (error){
      console.log(error);
      toast.error("An error have just happened :c Pls try again", { id });
    }
    
  };

  const handleSpotifyLogin = () => {
    window.location.href = `${BACKEND}/login`;
  };

  const toggleTheme = () => {
    setTheme(theme === "light" ? "dark" : "light");
  };

  const saveVisited = () => {
    setShowWelcomeMessage(false);
    localStorage.setItem("hasVisited", "true");
  };

  useEffect(() => {

    const hasVisited = localStorage.getItem("hasVisited")
    if (hasVisited) {
      setShowWelcomeMessage(false);
    }

    // Check if token is in URL (from OAuth callback)
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('token');

    if (tokenFromUrl) {
      // Save token and clean URL
      localStorage.setItem('spotify_token', tokenFromUrl);
      setToken(tokenFromUrl);
      setShowSpotifyModal(false);
      window.history.replaceState({}, document.title, window.location.pathname);
    } else {
      // Try to get token from localStorage
      const savedToken = localStorage.getItem('spotify_token');
      if (savedToken) {
        setToken(savedToken);
        setShowSpotifyModal(false);
      } else {
        // Fallback: try session-based auth
        api.get("/token")
          .then((res) => {
            setShowSpotifyModal(false);
            setToken(res.data.access_token);
            localStorage.setItem('spotify_token', res.data.access_token);
          })
          .catch(() => setShowSpotifyModal(true));
      }
    }
  }, []);

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
              className="mt-8 bg-white/20 text-white hover:bg-white/30 cursor-pointer"
              onClick={saveVisited}
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
              <SpotifyModal onLogin={handleSpotifyLogin} key="spotify-modal"/>
            </motion.div>
            :
            <AnimatePresence>
              {
                showEmotionGuide?
                  <motion.div
                    key="emotion-guide"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1, transition: { duration: 1, delay: 1.5, ease: "easeInOut" } }}
                    exit={{ opacity: 0 , transition: { duration: 1, ease: "easeInOut" } }}
                  >
                    <EmotionGuide />
                  </motion.div>
                :
                  <MusicPlayer updateDevice={handleDevice} updateQueue={handleUpdateQueue} token={token} queue={queue} key="music-player"/>
              }
              <ChatDock messageHandler={handleMessage} key="docked-chat"/>
            </AnimatePresence>
        }
      </AnimatePresence>
    </div>
  );
}
