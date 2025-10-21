// frontend/src/components/AlertCenter.jsx
import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { FaPaperPlane } from "react-icons/fa";

const AlertsPage = () => {
  const [messages, setMessages] = useState([]);
  const [manualMsg, setManualMsg] = useState("");
  const [loading, setLoading] = useState(true);

  // 🔹 Fetch both auto and manual alerts from backend
  const fetchAlerts = async () => {
    try {
      // Fetch auto alerts
      const autoRes = await fetch("http://localhost:5000/api/alerts/auto");
      const autoData = await autoRes.json();

      // Fetch manual alerts
      const manualRes = await fetch("http://localhost:5000/api/alerts/manual"); // if needed for existing manual saved
      const manualData = await manualRes.json().catch(() => ({ alerts: [] }));

      // Combine alerts (latest first)
      const combined = [...manualData.alerts, ...autoData.alerts].sort(
        (a, b) => new Date(b.createdAt || Date.now()) - new Date(a.createdAt || Date.now())
      );

      setMessages(combined);
    } catch (error) {
      console.error("Error fetching alerts:", error);
    } finally {
      setLoading(false);
    }
  };

  // 🔹 Send manual message to backend
  const handleSend = async () => {
    if (manualMsg.trim() === "") return;
    try {
      const res = await fetch("http://localhost:5000/api/alerts/manual", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: manualMsg }),
      });

      const data = await res.json();

      if (data.success) {
        setMessages([data.newAlert, ...messages]);
        setManualMsg("");
      } else {
        console.error("Manual alert failed:", data.message);
      }
    } catch (error) {
      console.error("Error sending manual message:", error);
    }
  };

  // 🔹 Load alerts on mount
  useEffect(() => {
    fetchAlerts();

    // Optional: refresh every 15 seconds
    const interval = setInterval(fetchAlerts, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative min-h-screen bg-black text-white px-6 py-10 overflow-hidden">
      {/* Glow effect */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-0 left-0 w-72 h-72 bg-green-400/20 blur-2xl rounded-full animate-pulse" />
        <div className="absolute bottom-0 right-0 w-56 h-56 bg-red-400/10 blur-3xl rounded-full animate-ping" />
      </div>

      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-3xl font-bold text-green-400 text-center mb-10"
      >
        🔔 Sustainability Alerts Center
      </motion.h1>

      {/* Manual Message Composer */}
      <div className="max-w-3xl mx-auto mb-12">
        <textarea
          rows="3"
          value={manualMsg}
          onChange={(e) => setManualMsg(e.target.value)}
          placeholder="Send manual message to team or workers..."
          className="w-full p-4 rounded-xl bg-[#111] border border-green-500 text-white focus:ring-2 focus:ring-green-400 outline-none"
        />
        <button
          onClick={handleSend}
          className="mt-4 px-6 py-2 flex items-center gap-2 bg-green-500 text-black font-bold rounded-xl hover:bg-green-600 transition-all"
        >
          <FaPaperPlane /> Send Message
        </button>
      </div>

      {/* Alerts Feed */}
      <div className="grid gap-6 max-w-5xl mx-auto">
        {loading ? (
          <p className="text-gray-400 text-center">Loading alerts...</p>
        ) : messages.length === 0 ? (
          <p className="text-gray-500 text-center">No alerts available</p>
        ) : (
          messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1, duration: 0.5 }}
              className={`bg-[#111]/80 border-l-4 ${msg.color || "border-green-500 shadow-green-500/30"} rounded-xl p-6 shadow-md hover:scale-[1.01] transition-all`}
            >
              <h3 className="text-xl font-semibold mb-1">{msg.title || "🔔 Alert"}</h3>
              <p className="text-sm text-gray-300">{msg.body}</p>
              <p className="text-xs text-gray-500 mt-2">{msg.time}</p>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
};

export default AlertsPage;
