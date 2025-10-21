import React, { useState } from "react";
import { motion } from "framer-motion";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import axios from "axios";
import { toast } from "react-hot-toast";

const Signup = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://localhost:5000/api/auth/signup", {
        name: username,
        email: email.toLowerCase(),
        password,
      });

      toast.success("🎉 Account created! Redirecting to login...", {
        duration: 2500,
        style: {
          background: "#1e293b",
          color: "#d1fae5",
          border: "1px solid #22c55e",
          padding: "14px",
          fontSize: "15px",
          borderRadius: "10px",
        },
        iconTheme: {
          primary: "#22c55e",
          secondary: "#1e293b",
        },
      });

      setTimeout(() => navigate("/login"), 2500);
    } catch (err) {
      const msg = err.response?.data?.message || "Signup failed!";
      toast.error(`❌ ${msg}`, {
        duration: 3000,
        style: {
          background: "#1f2937",
          color: "#fecaca",
          border: "1px solid #ef4444",
          padding: "14px",
          fontSize: "14px",
          borderRadius: "10px",
        },
      });
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-gray-900 overflow-hidden">
        {/* Animated Glow Orbs */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
        <div className="absolute bg-green-400/60 blur-3xl w-60 h-60 rounded-full animate-pulse top-20 left-10"></div>
        <div className="absolute bg-green-500/60 blur-2xl w-40 h-40 rounded-full animate-pulse bottom-10 right-10"></div>
        <div className="absolute bg-green-400/60 blur-3xl w-60 h-60 rounded-full animate-pulse top-20 right-10"></div>
        <div className="absolute bg-green-500/60 blur-2xl w-40 h-40 rounded-full animate-pulse bottom-10 left-10"></div>
        <div className="absolute bg-green-300/90 blur-2xl w-72 h-72 square-full animate-pulse top-40 right-1/2"></div>
        <div className="absolute bg-green-300/90 blur-2xl w-72 h-72 square-full animate-pulse top-40 left-1/2"></div>
      </div>
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="z-10 w-full max-w-md bg-[#111111]/80 backdrop-blur-md border border-green-500/20 rounded-3xl p-8 shadow-2xl text-white"
      >
        <h2 className="text-3xl font-bold text-green-400 text-center mb-6">
          Sign Up 🌱
        </h2>

        <form onSubmit={handleSignup} className="space-y-5">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-2 bg-transparent border border-green-500/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-400"
            required
          />

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 bg-transparent border border-green-500/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-400"
            required
          />

          <div className="relative">
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 pr-10 bg-transparent border border-green-500/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-400"
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute top-2 right-3 text-green-400"
            >
              {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          </div>

          <button
            type="submit"
            className="w-full py-2 bg-green-500 hover:bg-green-600 text-black font-semibold rounded-xl shadow-lg"
          >
            Create Account
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-400">
          Already have an account?{" "}
          <Link to="/login" className="text-green-400 hover:underline">
            Login
          </Link>
        </p>
      </motion.div>
    </div>
  );
};

export default Signup;



