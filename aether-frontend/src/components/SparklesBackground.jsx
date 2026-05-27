import React, { useId, useMemo } from "react";
import Particles, { ParticlesProvider } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import { motion, useAnimation } from "framer-motion";

// Custom lightweight class merger to replace `cn` without extra libraries
const cn = (...classes) => classes.filter(Boolean).join(" ");

const particlesInit = async (engine) => {
  await loadSlim(engine);
};

export const SparklesCore = (props) => {
  const {
    id,
    className,
    background,
    minSize,
    maxSize,
    speed,
    particleColor,
    particleDensity,
  } = props;

  const controls = useAnimation();

  const particlesLoaded = async (container) => {
    if (container) {
      controls.start({
        opacity: 1,
        transition: {
          duration: 1,
        },
      });
    }
  };

  const generatedId = useId();

  const options = useMemo(
    () => ({
      background: {
        color: {
          value: background || "transparent",
        },
      },
      fullScreen: {
        enable: false,
        zIndex: 1,
      },
      fpsLimit: 120,
      interactivity: {
        events: {
          onClick: {
            enable: true,
            mode: "push",
          },
          onHover: {
            enable: false,
            mode: "repulse",
          },
          resize: true,
        },
        modes: {
          push: {
            quantity: 4,
          },
          repulse: {
            distance: 200,
            duration: 0.4,
          },
        },
      },
      particles: {
        bounce: {
          horizontal: {
            value: 1,
          },
          vertical: {
            value: 1,
          },
        },
        collisions: {
          enable: false,
        },
        color: {
          value: particleColor || "#ffffff",
        },
        move: {
          direction: "none",
          enable: true,
          outModes: {
            default: "out",
          },
          random: false,
          speed: {
            min: 0.1,
            max: 0.5,
          },
          straight: false,
        },
        number: {
          density: {
            enable: true,
            width: 400,
            height: 400,
          },
          value: particleDensity || 40,
        },
        opacity: {
          value: {
            min: 0.1,
            max: 0.8,
          },
          animation: {
            enable: true,
            speed: speed || 1,
            sync: false,
            startValue: "random",
          },
        },
        shape: {
          type: "circle",
        },
        size: {
          value: {
            min: minSize || 0.6,
            max: maxSize || 1.8,
          },
        },
      },
      detectRetina: true,
    }),
    [background, minSize, maxSize, speed, particleColor, particleDensity]
  );

  return (
    <motion.div animate={controls} className={cn("opacity-0", className)}>
      <ParticlesProvider init={particlesInit}>
        <Particles
          id={id || generatedId}
          className="h-full w-full"
          particlesLoaded={particlesLoaded}
          options={options}
        />
      </ParticlesProvider>
    </motion.div>
  );
};

export default function SparklesBackground() {
  return (
    <div className="fixed inset-0 w-screen h-screen pointer-events-none -z-10 bg-[#02050a] overflow-hidden">
      {/* 1. Deep Atmospheric Glows (The 'Premium' Layer) */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-cyan-500/10 blur-[120px] rounded-full animate-atmospheric" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] bg-indigo-600/10 blur-[150px] rounded-full animate-atmospheric [animation-delay:-5s]" />
      <div className="absolute top-[20%] right-[10%] w-[40%] h-[40%] bg-emerald-500/5 blur-[100px] rounded-full animate-atmospheric [animation-delay:-12s]" />

      {/* 2. Sparkles Core Layer */}
      <div className="absolute inset-0 opacity-[0.8] mix-blend-screen">
        <SparklesCore
          id="tsparticlesbg"
          background="transparent"
          minSize={0.6}
          maxSize={1.8}
          particleDensity={60}
          particleColor="#ffffff"
          className="w-full h-full"
        />
      </div>
    </div>
  );
}
