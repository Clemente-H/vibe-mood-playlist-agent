"use client"

import { useState, useEffect , useRef } from "react"
import { Play, Pause, SkipForward, SkipBack, Volume2, Volume1, VolumeX } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Slider } from "@/components/ui/slider"
import { motion , AnimatePresence } from "framer-motion"
import api from "@/lib/api";

// Track template
const TRACK_TEMPLATE = {
  name: "",
  album: { images: [{ url: "" }] },
  artists: [{ name: "" }],
};

export function MusicPlayer({ queue , token , updateDevice , updateQueue }) {

  const playerRef = useRef(null);
  const initializedRef = useRef(false); // prevent double useEffect execution in dev
  const scriptRef = useRef(null);
  const tickRef = useRef(null);
  const baseProgressRef = useRef(0);   // seconds in the last real sync
  const lastSyncTsRef = useRef(0);     // timestamp ms of the last real sync
  const lastTrackUriRef = useRef(null);


  const [isActive, setIsActive] = useState(false);
  const [isPaused, setIsPaused] = useState(true);
  const [currentTrack, setCurrentTrack] = useState(TRACK_TEMPLATE);

  const [currentTime, setCurrentTime] = useState(0);      // seconds
  const [totalDuration, setTotalDuration] = useState(0);  // seconds

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.trunc(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  const progressPercentage =
    totalDuration > 0 ? (currentTime / totalDuration) * 100 : 0;

  const playFromIndex = async (index) => {
    try{
      await api.post('/spotify/play_from_queue', { index });
      
    } catch (err) {
      console.error("Error playing from queue:", err);
    }
  }

  const shouldRefreshQueue = (state) => {
    if (!state) return false;

    const currentUri = state.track_window?.current_track?.uri;
    if (!currentUri) return false;

    // si la canción no cambió → no refrescar
    if (currentUri === lastTrackUriRef.current) return false;

    // actualizar referencia de última canción
    lastTrackUriRef.current = currentUri;

    return true;
  };

  useEffect(() => {

    if (initializedRef.current) return; // prevent double player initialization
    initializedRef.current = true;

    if (!window.Spotify) {
      scriptRef.current = document.createElement("script");
      scriptRef.current.src = "https://sdk.scdn.co/spotify-player.js";
      scriptRef.current.async = true;
      document.body.appendChild(scriptRef.current);
    }

    window.onSpotifyWebPlaybackSDKReady = async () => {

      if (playerRef.current) return; // ya existe

      const player = new window.Spotify.Player({
        name: "VibeFM",
        getOAuthToken: async (cb) => await cb(token),
        volume: 0.15,
      });

      playerRef.current = player;

      // Listeners
      const onReady = async ({ device_id }) => {
        console.log("Ready with Device ID", device_id);
        updateDevice(device_id);
      };

      const onNotReady = ({ device_id }) => {
        console.log("Device ID has gone offline", device_id);
        setIsActive(false);
      };

      const onState = async (state) => {
        if (!state) {
          setIsActive(false);
          return;
        }

        const durationSec = (state.duration || state.track_window.current_track?.duration_ms || 0) / 1000;
        const positionSec = (state.position || 0) / 1000;

        setCurrentTrack(state.track_window.current_track || TRACK_TEMPLATE);
        setTotalDuration(durationSec);
        setCurrentTime(positionSec);
        setIsPaused(state.paused);

        if(shouldRefreshQueue(state)){
          updateQueue();
        }

        // Initial reference for local tick
        baseProgressRef.current = positionSec;
        lastSyncTsRef.current = Date.now();

        // Active/inactive
        const currentState = await player.getCurrentState();
        setIsActive(!!currentState);

        // if(shouldRefreshQueue(state)){
        //   loadQueue();
        // }
        
        // Restart the tick when paused
        if (tickRef.current) {
          clearInterval(tickRef.current);
          tickRef.current = null;
        }
        if (!state.paused && durationSec > 0) {
          tickRef.current = setInterval(() => {
            const elapsed = (Date.now() - lastSyncTsRef.current) / 1000;
            const simulated = baseProgressRef.current + elapsed;
            setCurrentTime((prev) => {
              const next = Math.min(simulated, durationSec);
              return next;
            });
            if (simulated >= durationSec) {
              clearInterval(tickRef.current);
              tickRef.current = null;
            }
          }, 250); 
        }
      };

      player.addListener("ready", onReady);
      player.addListener("not_ready", onNotReady);
      player.addListener("player_state_changed", onState);

      // Connect
      player.connect();

      // Cleanup on unmount
      const cleanup = () => {
        try {
          if (tickRef.current) {
            clearInterval(tickRef.current);
            tickRef.current = null;
          }

          if (playerRef.current) {
            // Remove listener on unmount
            playerRef.current.removeListener("ready", onReady);
            playerRef.current.removeListener("not_ready", onNotReady);
            playerRef.current.removeListener("player_state_changed", onState);
            playerRef.current.disconnect();
            playerRef.current = null;
          }

          // Remove script on unmount if we added it
          if (scriptRef.current && scriptRef.current.parentNode) {
            scriptRef.current.parentNode.removeChild(scriptRef.current);
            scriptRef.current = null;
          }
        } catch (e) {
          console.warn("Cleanup failed", e);
        }
      };

      // Save cleanup in ref in order to call it on return
      playerRef.current.__cleanup = cleanup;

    };

    return () => {
      // Execute cleanup if there is player
      if (playerRef.current?.__cleanup) {
        playerRef.current.__cleanup();
      }
    };

  }, []);

  if(!isActive){
    return (
      <motion.div
        className="fixed left-1/2 top-1/2 z-10 w-full max-w-sm -translate-x-1/2 -translate-y-1/2 px-4 sm:max-w-md sm:px-6"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1, transition: { duration: 1 , delay: 1.5 } }}
      >
        <div className="mb-3 text-center sm:mb-4">
          <b className="text-xs font-semibold text-white/70 sm:text-sm"> Instance not active. Transfer your playback using your Spotify app </b>
        </div>
      </motion.div>
    )
  }
  
  const player = playerRef.current;

  return (
    <motion.div
      className="fixed left-1/2 top-1/2 z-10 w-full max-w-sm -translate-x-1/2 -translate-y-1/2 px-4 sm:max-w-md sm:px-6"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1, transition: { duration: 1 , delay: 1.5 } }}
    >
      <div className="rounded-lg border border-white/20 bg-white/10 p-4 backdrop-blur-lg sm:p-6 transition-all">

        <div className="mb-4 flex justify-center sm:mb-6">
          <img
            src={currentTrack.album.images[0].url || "/cat-slave.png"}
            alt="Album cover"
            className="h-40 w-40 rounded-lg object-cover shadow-lg sm:h-48 sm:w-48"
          />
        </div>

        {/* Current Song */}
        <div className="mb-4 sm:mb-6">
          <div className="mb-3 text-center sm:mb-4">
            <h3 className="text-lg font-bold text-white sm:text-xl">
              {currentTrack.name || "--"}
            </h3>
            <p className="text-xs font-semibold text-white/70 sm:text-sm">
              {currentTrack.artists[0].name || "--"}
            </p>
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
              className="h-10 w-10 text-white hover:bg-white/20 hover:text-white sm:h-12 sm:w-12 cursor-pointer"
              onClick={() => player.previousTrack()}
            >
              <SkipBack className="h-4 w-4 sm:h-5 sm:w-5" />
            </Button>
            <Button
              size="icon"
              className="h-10 w-10 bg-white/20 text-white hover:bg-white/30 sm:h-12 sm:w-12 cursor-pointer"
              onClick={() => player.togglePlay()}
            >
              {isPaused ? <Play className="h-5 w-5 sm:h-6 sm:w-6" />:<Pause className="h-5 w-5 sm:h-6 sm:w-6" />}
            </Button>
            <Button
              size="icon"
              variant="ghost"
              className="h-10 w-10 text-white hover:bg-white/20 hover:text-white sm:h-12 sm:w-12 cursor-pointer"
              onClick={() => player.nextTrack()}
            >
              <SkipForward className="h-4 w-4 sm:h-5 sm:w-5" />
            </Button>
          </div>
        </div>

        {/* Queue */}
        {queue.length > 0?
          <AnimatePresence>
            <motion.div
              className="border-t border-white/20 pt-3 sm:pt-4"
              initial={{opacity: 0.8}}
              animate={{opacity: 1.0}}
            >
              <h4 className="mb-2 text-xs font-bold uppercase tracking-wide text-white/70 sm:mb-3 sm:text-sm">Up Next</h4>
              <ScrollArea className="h-40 sm:h-48">
                <div className="space-y-2">
                  {queue.map((song, i) => (
                    <div
                      key={`${song.id}-${i}`}
                      className="flex items-center justify-between rounded-md p-2 transition-colors hover:bg-white/10 sm:p-3 cursor-pointer"
                      onClick={() => playFromIndex(i)}
                    >
                      <div className="flex-1">
                        <p className="text-xs font-bold text-white sm:text-sm">{song.name}</p>
                        <p className="text-xs font-semibold text-white/60">{song.artists.map(a => a.name).join(", ")}</p>
                      </div>
                      <span className="text-xs font-semibold text-white/60">{formatTime(song.duration_ms/1000)}</span>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </motion.div>
          </AnimatePresence>
        :
          <div className="border-t border-white/20 pt-3 sm:pt-4">
            <h4 className="mb-2 text-xs font-bold uppercase tracking-wide text-white/70 sm:mb-3 sm:text-sm">No active queue </h4>
          </div>
        }
        
      </div>
    </motion.div>
  )
}
