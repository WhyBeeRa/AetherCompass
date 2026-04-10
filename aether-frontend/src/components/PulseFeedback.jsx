import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const FEEDBACK_MESSAGES = [
    // Scout
    "Deep scanning technical repositories for execution proofs...",
    "Analyzing codebases for core capability verification...",
    // Auditor
    "Detecting marketing noise patterns and filtering community bias...",
    "Performing Integrity Check against ground truth data...",
    // Classifier
    "Mapping User Intent and calculating objective performance metrics...",
    "Refining functionality from raw data to build performance profile...",
    // Curator
    "Curating the most reliable visual execution proofs...",
    "Processing execution 'Recipe' for the Truth Gallery..."
];

export function PulseFeedback() {
    const [index, setIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setIndex((prev) => (prev + 1) % FEEDBACK_MESSAGES.length);
        }, 2500); // Change message every 2.5 seconds

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex items-center justify-center p-4">
            <AnimatePresence mode="wait">
                <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -5 }}
                    transition={{ duration: 0.5 }}
                    className="font-mono text-xs text-white/40 tracking-wider text-center"
                >
                    <span className="mr-2 text-white/50">AETHER_KERNEL:</span>
                    {FEEDBACK_MESSAGES[index]}
                    <span className="animate-pulse ml-1 text-white">_</span>
                </motion.div>
            </AnimatePresence>
        </div>
    );
}
