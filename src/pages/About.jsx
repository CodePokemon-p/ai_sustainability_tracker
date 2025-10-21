import React from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";

const About = () => {
  return (
    <div className="relative min-h-screen bg-black text-white py-20 px-6 overflow-hidden">
      {/* Background Orbs */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-10 left-10 w-72 h-72 bg-green-500/20 blur-3xl rounded-full animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-60 h-60 bg-purple-500/10 blur-2xl rounded-full animate-ping"></div>
      </div>

      {/* Title */}
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-4xl font-bold text-center text-green-400 mb-12"
      >
        About EcoTrack 🌿
      </motion.h1>

      {/* Mission */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="max-w-4xl mx-auto mb-12 bg-[#111]/80 border border-green-400/50 animate-pulse shadow-[0_0_40px_4px_rgba(34,197,94,0.2)] rounded-2xl p-6 backdrop-blur-md"
      >
        <h2 className="text-2xl font-semibold text-green-300 mb-2">🌍 Our Mission</h2>
        <p className="text-sm text-gray-300 leading-relaxed">
          EcoTrack is on a mission to revolutionize the textile industry by reducing environmental impact using AI and real-time data. We aim to help factories and brands track their carbon footprint, water usage and material waste — and act on it with intelligence.
        </p>
      </motion.div>

      {/* Vision */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="max-w-4xl mx-auto mb-12 bg-[#111]/80 border border-blue-400/50 animate-pulse shadow-[0_0_40px_4px_rgba(96,165,250,0.2)] rounded-2xl p-6 backdrop-blur-md"
      >
        <h2 className="text-2xl font-semibold text-blue-300 mb-2">🔮 Our Vision</h2>
        <p className="text-sm text-gray-300 leading-relaxed">
          We see a future where AI helps fashion brands become fully sustainable. A future where every decision in the production process is data-driven, ethical, and clean. Our goal: Make sustainability easy, accessible, and powerful — globally.
        </p>
      </motion.div>

      {/* Who We Are — IUB Edition */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="max-w-4xl mx-auto mb-12 bg-[#111]/80 border border-yellow-400/50 animate-pulse shadow-[0_0_40px_4px_rgba(253,224,71,0.2)] rounded-2xl p-6 backdrop-blur-md"
      >
        <h2 className="text-2xl font-semibold text-yellow-300 mb-2">👤 Who We Are</h2>
        <p className="text-sm text-gray-300 leading-relaxed">
          This project was proudly built by a passionate final-year software engineering student from the <strong>Islamia University of Bahawalpur (IUB)</strong>. EcoTrack reflects the vision of transforming local innovation into global impact — combining AI, sustainability, and purpose into a product that can stand alongside the best in the world.
          <span className="block mt-3 text-yellow-400 font-medium">
            This is more than a degree project. It’s a statement.
          </span>
        </p>
      </motion.div>

      {/* CTA */}
      <div className="text-center mt-16">
        <Link
          to="/features"
          className="inline-block bg-green-500 hover:bg-green-600 text-black font-bold px-6 py-3 rounded-xl shadow-lg shadow-green-400/30 transition-all duration-300"
        >
          Explore Features →
        </Link>
      </div>
    </div>
  );
};

export default About;

