import React, { useEffect } from "react";
import { motion } from "framer-motion";
import Tilt from "react-parallax-tilt";
import AOS from "aos";
import "aos/dist/aos.css";

import hero2 from "../assets/hero2.png";
import impact from "../assets/impact.png";

import ThreeScene from "../components/ThreeScene.jsx"; // ✅ 3D animated globe

const LandingPage = () => {
  useEffect(() => {
    AOS.init({ duration: 1200, once: true, offset: 100 });
  }, []);

  return (
    <section className="relative z-10 bg-black text-white light:bg-white light:text-gray-900 overflow-x-hidden">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 py-24 grid md:grid-cols-2 items-center gap-12">
        <motion.div
          initial={{ opacity: 0, y: -40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-5xl font-bold mb-6 text-green-400 light:text-green-600 glow">
            AI-Powered Eco Intelligence 🌍
          </h1>
          <p className="text-lg text-gray-300 light:text-gray-700 mb-6">
            Sustainability meets machine learning. Our app tracks CO₂,
            optimizes patterns, and sends alerts — in real-time, with style.
          </p>
          <a
            href="/dashboard"
            className="bg-green-500 hover:bg-green-600 text-white light:text-white px-6 py-3 rounded-md text-lg font-medium shadow-lg glow transition-all duration-300"
          >
            🚀 Launch Dashboard
          </a>
        </motion.div>

        <Tilt
          tiltMaxAngleX={25}
          tiltMaxAngleY={25}
          perspective={1000}
          scale={1.05}
          transitionSpeed={1000}
          gyroscope={true}
        >
          <motion.img
            src={hero2}
            alt="Hero AI"
            className="rounded-xl shadow-lg transition duration-500"
            initial={{ opacity: 0, x: 60 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1 }}
          />
        </Tilt>
      </div>

      {/* Impact Section */}
      <div className="bg-gray-900 light:bg-gray-100 py-24 px-6">
        <div className="max-w-6xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6 text-green-300 light:text-green-600 glow">
            🌿 Impact We’ve Made
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 mt-10">
            {[
              "💧 1.2M L Water Saved",
              "🧵 180K m² Fabric Optimized",
              "🌬️ 350K Tons CO₂ Reduced",
            ].map((stat, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.2 }}
                viewport={{ once: true }}
                whileHover={{ scale: 1.08, boxShadow: "0 0 20px #00FFAA" }}
                className="bg-gray-800 light:bg-white p-6 rounded-xl border border-green-500 text-green-300 light:text-green-600 shadow-md transition-all duration-300 hover:glow"
              >
                <h3 className="text-xl font-semibold">{stat}</h3>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Mission Section */}
      <div className="max-w-7xl mx-auto py-28 px-6 grid md:grid-cols-2 items-center gap-16">
  <motion.div
    initial={{ x: -50, opacity: 0 }}
    whileInView={{ x: 0, opacity: 1 }}
    transition={{ duration: 1 }}
    viewport={{ once: true }}
  >
    <ThreeScene />
  </motion.div>

  <motion.div
    initial={{ x: 50, opacity: 0 }}
    whileInView={{ x: 0, opacity: 1 }}
    transition={{ duration: 1 }}
    viewport={{ once: true }}
  >
    <h2 className="text-3xl font-bold text-green-400 mb-4 glow">🎯 Our Mission</h2>
    <p className="text-lg text-gray-300 mb-4">
      Reducing environmental harm in textiles through AI-powered insight. Pattern optimization, real-time alerts, and predictive sustainability.
    </p>
    <p className="text-sm text-green-200 italic">
      "Driven by research — Inspired by ISO 14001 & EU Green Deal"
    </p>
  </motion.div>
</div>

      {/* Contact CTA */}
      <div className="text-center py-24 px-6 bg-gray-900 light:bg-gray-100">
        <motion.h2
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-3xl font-bold text-green-300 light:text-green-600 mb-4 glow"
        >
          📩 Let’s Talk Sustainability
        </motion.h2>
        <p className="text-gray-400 light:text-gray-700 mb-6">
          We’re here to empower your brand. Just reach out.
        </p>
        <a
          href="/contact"
          className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-md glow transition-all duration-300"
        >
          Contact Us
        </a>
      </div>

      {/* Footer */}
      <footer className="bg-black light:bg-white text-center py-10 text-gray-400 light:text-gray-700 border-t border-gray-700 light:border-gray-300">
        <div className="text-green-400 light:text-green-600 font-semibold glow mb-2">
          🌿 EcoTrack | Final Year Project
        </div>
        <div className="text-sm">© 2025 — IUB Software Engineering</div>
        <div className="mt-4 flex justify-center gap-6 text-sm text-gray-500">
          <a href="https://www.linkedin.com/in/sabasaleemitpro/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
          <a href="https://github.com/CodePokemon-p"target="_blank" rel="noopener noreferrer">GitHub</a>
          <a href="https://www.instagram.com/theiubwp"target="_blank" rel="noopener noreferrer">Instagram</a>
        </div>
      </footer>
    </section>
  );
};

export default LandingPage;



