import React, { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { FaRobot, FaUser } from "react-icons/fa";
import { BsSend } from "react-icons/bs";

const ChatbotPage = () => {
  const [messages, setMessages] = useState([
    { from: "bot", text: "Hi there! I'm EcoBot 🌿. Ask me anything about sustainability." },
  ]);
  const [input, setInput] = useState("");
  const chatEndRef = useRef(null);

  const sendMessage = async (e) => {
  e.preventDefault();
  if (!input.trim()) return;

  const userMsg = { from: "user", text: input };
  setMessages((prev) => [...prev, userMsg]);

  try {
    const res = await fetch("http://localhost:8000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: input }),
    });
    const data = await res.json();
    const botMsg = { from: "bot", text: data.reply };
    setMessages((prev) => [...prev, botMsg]);
  } catch (err) {
    setMessages((prev) => [
      ...prev,
      { from: "bot", text: "❌ EcoBot: Failed to reach server." },
    ]);
  }

  setInput("");
};


  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="relative min-h-screen bg-black text-white px-6 py-10 overflow-hidden">
      {/* 3D Glow Orbs */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-5 left-5 w-72 h-72 bg-green-500/20 blur-3xl rounded-full animate-pulse" />
        <div className="absolute top-1/2 right-0 w-60 h-60 bg-teal-400/10 blur-2xl rounded-full animate-ping" />
      </div>

      {/* Page Title */}
      <motion.h1
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-4xl font-bold text-green-400 text-center mb-10"
      >
        🤖 EcoBot AI Chat Interface
      </motion.h1>

      {/* Chat Box */}
      <div className="max-w-3xl mx-auto bg-[#0f0f0f] border border-green-700/50 rounded-2xl p-6 shadow-lg shadow-green-500/20">
        <div className="h-96 overflow-y-auto space-y-4 pr-2">
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex items-start gap-3 ${msg.from === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.from === "bot" && <FaRobot className="text-green-400 mt-1" />}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`max-w-xs px-4 py-2 rounded-xl text-sm whitespace-pre-line
                  ${msg.from === "user" ? "bg-green-500 text-black" : "bg-[#1a1a1a] border border-green-400 text-green-200"}`}
              >
                {msg.text}
              </motion.div>
              {msg.from === "user" && <FaUser className="text-green-300 mt-1" />}
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        {/* Input Bar */}
        <form onSubmit={sendMessage} className="flex mt-6">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 px-4 py-3 rounded-l-xl bg-black text-white border border-green-500 focus:outline-none focus:ring-2 focus:ring-green-400"
          />
          <button
            type="submit"
            className="px-5 py-3 bg-green-400 text-black font-semibold rounded-r-xl hover:scale-105 transition-transform"
          >
            <BsSend />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatbotPage;
