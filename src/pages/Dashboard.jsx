import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Link, useNavigate } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import axios from "axios";

const Dashboard = () => {
  const navigate = useNavigate();

  const [metrics, setMetrics] = useState({
    carbonEmission: "--",
    waterUsage: "--",
    fabricWaste: "--",
  });

  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  // ✅ Fetch live dashboard stats from backend
  const fetchDashboardData = async () => {
    try {
      const res = await axios.get("http://localhost:5000/api/dashboard/stats");
      console.log("📊 Dashboard fetched:", res.data);

      const carbonVal = res.data.co2 ?? "--";
      const waterVal = res.data.water ?? "--";
      const wasteVal = res.data.waste ?? "--";

      setMetrics({
        carbonEmission: carbonVal,
        waterUsage: waterVal,
        fabricWaste: wasteVal,
      });

      // Update live chart data
      setChartData((prev) => {
        const newEntry = {
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          CO2: parseFloat(carbonVal),
          Water: parseFloat(waterVal),
        };
        const updated = [...prev, newEntry];
        return updated.slice(-5); // Keep latest 5
      });
    } catch (error) {
      console.error("❌ Dashboard fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const stats = [
    {
      title: "CO₂ Emissions",
      value: metrics.carbonEmission !== "--" ? `${metrics.carbonEmission} Tons` : "--",
      unit: "Today",
      glow: "shadow-green-500",
      border: "border-green-400",
    },
    {
      title: "Water Usage",
      value: metrics.waterUsage !== "--" ? `${metrics.waterUsage} L` : "--",
      unit: "Per Batch",
      glow: "shadow-blue-500",
      border: "border-blue-400",
    },
    {
      title: "Fabric Waste",
      value: metrics.fabricWaste !== "--" ? `${metrics.fabricWaste} %` : "--",
      unit: "Utilization",
      glow: "shadow-purple-500",
      border: "border-purple-400",
    },
  ];

  return (
    <div className="relative min-h-screen bg-black text-white px-6 py-10 overflow-hidden">
      {/* Glowing Background */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-10 left-10 w-72 h-72 bg-green-500/20 blur-3xl rounded-full animate-pulse" />
        <div className="absolute bottom-0 right-0 w-56 h-56 bg-blue-400/10 blur-2xl rounded-full animate-ping" />
        <div className="absolute top-1/3 left-1/2 w-64 h-64 bg-purple-500/10 blur-2xl rounded-full animate-spin-slow" />
      </div>

      {/* Heading */}
      <motion.h1
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-4xl font-bold text-green-400 text-center mb-12"
      >
        Sustainability Dashboard 🌍
      </motion.h1>

      {/* Stat Cards */}
      <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto mb-16">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.2, duration: 0.6 }}
            className={`bg-[#111]/70 border ${stat.border} rounded-2xl p-6 shadow-xl hover:scale-105 transition-all duration-300 ${stat.glow}`}
          >
            <h2 className="text-xl text-gray-300 mb-2">{stat.title}</h2>
            <p className="text-4xl font-bold text-white">
              {loading ? "Loading..." : stat.value}
            </p>
            <p className="text-sm text-green-400 mt-1">{stat.unit}</p>
          </motion.div>
        ))}
      </div>

      {/* Live Emission Chart */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-4xl mx-auto bg-[#111]/80 border border-green-500/20 rounded-2xl p-8 shadow-xl"
      >
        <h3 className="text-xl text-green-400 font-semibold mb-4">Live Emission Chart</h3>
        <div className="w-full h-64 bg-black/30 border border-dashed border-green-400 rounded-xl p-3">
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2f2f2f" />
                <XAxis dataKey="time" stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#111",
                    border: "1px solid #333",
                    color: "#fff",
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="CO2" stroke="#00FF7F" strokeWidth={2} />
                <Line type="monotone" dataKey="Water" stroke="#1E90FF" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400 text-sm">
              Waiting for live data...
            </div>
          )}
        </div>
      </motion.div>

      {/* Tool Links */}
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
        className="mt-20 max-w-6xl mx-auto grid md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        <Link to="/pattern">
          <div className="bg-[#111]/80 border border-purple-400 rounded-2xl p-6 hover:shadow-purple-500 hover:scale-105 transition-all duration-300 cursor-pointer text-center">
            <h3 className="text-xl font-semibold text-purple-400 mb-2">🧵 Pattern Optimizer</h3>
            <p className="text-sm text-gray-300">Reduce fabric waste with AI-optimized layouts</p>
          </div>
        </Link>

        <Link to="/tracker">
          <div className="bg-[#111]/80 border border-blue-400 rounded-2xl p-6 hover:shadow-blue-500 hover:scale-105 transition-all duration-300 cursor-pointer text-center">
            <h3 className="text-2xl font-semibold text-blue-400 mb-2">🌿 Track Emissions</h3>
            <p className="text-sm text-gray-300">Log and track your CO₂ & water usage in real-time</p>
          </div>
        </Link>

        <Link to="/reports">
          <div className="bg-[#111]/80 border border-yellow-400 rounded-2xl p-6 hover:shadow-yellow-500 hover:scale-105 transition-all duration-300 cursor-pointer text-center">
            <h3 className="text-2xl font-semibold text-yellow-300 mb-2">📥 Report Analyzer</h3>
            <p className="text-sm text-gray-300">Upload & download sustainability reports easily</p>
          </div>
        </Link>

        <Link to="/alerts">
          <div className="bg-[#111]/80 border border-red-500 rounded-2xl p-6 hover:shadow-red-500 hover:scale-105 transition-all duration-300 cursor-pointer text-center">
            <h3 className="text-2xl font-semibold text-red-400 mb-2">🔔 Message Alerts</h3>
            <p className="text-sm text-gray-300">Notify workers or managers about emissions instantly</p>
          </div>
        </Link>
      </motion.div>

      {/* Chatbot Button */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 1 }}
        className="mt-16 max-w-xl mx-auto text-center"
      >
        <button
          onClick={() => navigate("/chatbot")}
          className="px-8 py-4 bg-green-500 text-black font-bold text-lg rounded-2xl shadow-green-400/40 shadow-lg hover:scale-105 transition-all duration-300"
        >
          🤖 Talk to EcoBot – AI Chat
        </button>
      </motion.div>
    </div>
  );
};

export default Dashboard;


