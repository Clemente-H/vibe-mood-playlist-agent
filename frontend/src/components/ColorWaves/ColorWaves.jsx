import './ColorWaves.css';
import { AnimatePresence, motion } from "framer-motion";

export function ColorWaves({ waves }) {

  return (
    <>
      <motion.div
        className="waves-container"
        key="waves"
        whileHover={{
          scale: 1.25,
        }}
        initial={{
          scale: 0,
        }}
        animate={{
          scale: 1,
          transition: {
            duration: 0.7,
            delay: 2
          }
        }}
      >
        <AnimatePresence>
        {waves.map((wave, index) => (
          <motion.div
            key={wave.id}
            className="wave"
            style={{
              borderRadius: `${wave.borderRadius}%`,
              background: `${wave.color}`,
              zIndex: 999-wave.id,
            }}
            initial={{
              top: "100%",
              opacity: 0,
              animationDuration: `${wave.duration}s`,
            }}
            animate={{
              top: `${wave.verticalPosition}%`,
              opacity: 0.5,
            }}
            exit={{
              top: "150%",
            }}
            transition={{
              duration: 3,
              ease: "easeInOut",
            }}
          />
        ))}
        </AnimatePresence>
      </motion.div>
    </>
  );
}