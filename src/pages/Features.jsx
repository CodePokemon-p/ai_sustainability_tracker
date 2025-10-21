import React from "react";
import { motion } from "framer-motion";
import { Bot, FileText, LineChart, Scissors } from "lucide-react";
import { Link } from "react-router-dom";

const features = [
  {
    title: "Pattern Placement Optimizer",
    description:
      "AI-powered tool that arranges fabric patterns to reduce waste by up to 30%. Upload your dimensions or images and let the system optimize.",
    icon: <Scissors className="w-8 h-8 text-green-400" />,
    glow: "shadow-[0_0_40px_4px_rgba(34,197,94,0.5)] border-green-500",
  },
  {
    title: "Carbon & Water Footprint Tracker",
    description:
      "Track real-time emissions, water usage and energy per batch. Complies with ISO 14001 and helps you stay green certified.",
    icon: <LineChart className="w-8 h-8 text-blue-400" />,
    glow: "shadow-[0_0_40px_4px_rgba(96,165,250,0.4)] border-blue-500",
  },
  {
    title: "Report Upload & Download",
    description:
      "Easily upload sustainability data (CSV, PDF) and download automated impact reports ready for investors or audits.",
    icon: <FileText className="w-8 h-8 text-purple-400" />,
    glow: "shadow-[0_0_40px_4px_rgba(192,132,252,0.4)] border-purple-500",
  },
  {
    title: "Smart AI Chat Assistant",
    description:
      "Your 24/7 AI-powered assistant that responds to questions like 'How much water used today?' or 'Generate my report'.",
    icon: <Bot className="w-8 h-8 text-yellow-300" />,
    glow: "shadow-[0_0_40px_4px_rgba(253,224,71,0.4)] border-yellow-400",
  },
];

const Features = () => {
  return (
    <div className="relative min-h-screen bg-black text-white py-20 px-6 overflow-hidden">
      {/* Background Orbs */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-10 left-10 w-60 h-60 bg-green-500/20 blur-3xl rounded-full animate-pulse"></div>
        <div className="absolute bottom-0 right-0 w-72 h-72 bg-purple-500/10 blur-3xl rounded-full animate-ping"></div>
      </div>

      {/* Title */}
      <motion.h1
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-4xl font-bold text-center text-green-400 mb-12"
      >
        Platform Features ✨
      </motion.h1>

      {/* Feature Cards */}
      <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
        {features.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.2 }}
            className={`bg-[#0d0d0d]/70 backdrop-blur-lg border rounded-3xl p-6 hover:scale-105 transition-all duration-300 ${f.glow}`}
          >
            <div className="mb-4">{f.icon}</div>
            <h2 className="text-xl font-bold text-white mb-2">{f.title}</h2>
            <p className="text-sm text-gray-400">{f.description}</p>
          </motion.div>
        ))}
      </div>

      {/* Call to Action */}
      <div className="mt-16 text-center">
        <Link
          to="/dashboard"
          className="inline-block bg-green-500 hover:bg-green-600 text-black font-bold px-6 py-3 rounded-xl shadow-lg shadow-green-400/30 transition-all duration-300"
        >
          Go to Dashboard →
        </Link>
      </div>
    </div>
  );
};

export default Features;

