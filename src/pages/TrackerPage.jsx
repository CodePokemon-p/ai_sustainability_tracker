import React, { useState } from "react";
import { motion } from "framer-motion";
import { FaCloud, FaTint, FaLeaf, FaBolt, FaTrash } from "react-icons/fa";
import { MdWarning } from "react-icons/md";
import { toast } from "react-hot-toast";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

const defaultProducts = [
  "Cotton", "Polyester", "Nylon", "Linen", "Silk", "Rayon", "Wool",
  "Denim", "Lawn", "Viscose", "Recycled_Poly", "Synthetic_Blend", "Microfiber", "Organic_Cotton"
];

const TrackerPage = () => {
  const [productType, setProductType] = useState("");
  const [co2, setCo2] = useState("");
  const [water, setWater] = useState("");
  const [energy, setEnergy] = useState("");
  const [pollutant, setPollutant] = useState("");
  const [waste, setWaste] = useState("");
  const [result, setResult] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [tone, setTone] = useState("professional");
  const [apiError, setApiError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (setter) => (e) => {
    setter(e.target.value);
    setApiError(null);
    setResult(null);
  };

  const handleTrack = async () => {
    setApiError(null);
    setLoading(true);

    if (!productType || !co2 || !water || !energy || !pollutant || !waste) {
      toast.error("⚠️ All fields are required.");
      setLoading(false);
      return;
    }

    try {
      const ghg = parseFloat(co2) || 0;
      const waterC = parseFloat(water) || 0;
      const energyC = parseFloat(energy) || 0;
      const wasteC = parseFloat(waste) || 0;
      const pollutantsC = parseFloat(pollutant) || 0;

      // Call /predict endpoint
      const predictRes = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_type: productType,
          greenhouse_gas_emissions: ghg,
          water_consumption: waterC,
          energy_consumption: energyC,
          pollutants_emitted: pollutantsC,
          waste_generation: wasteC,
          tone: tone
        }),
      });

      const data = await predictRes.json();
      if (!predictRes.ok) throw new Error(data.error || "Prediction failed");

      // Set result with data from the API
      setResult({
        eco_level: data.eco_level,
        eco_score: data.eco_score,
        co2: ghg,
        water: waterC,
        analysis: data.analysis // This should contain the Gemini response
      });

      // Add to chart data
      setChartData((prev) => [
        ...prev,
        { name: productType, CO2: ghg, Water: waterC }
      ]);

      setLoading(false);
    } catch (err) {
      setApiError(`❌ ${err.message}`);
      setLoading(false);
    }
  };

  const fieldVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i) => ({ opacity: 1, y: 0, transition: { delay: i * 0.1 } })
  };

  return (
    <div className="relative min-h-screen bg-black text-white px-6 py-12 overflow-hidden">
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-0 left-0 w-72 h-72 bg-green-500/30 blur-3xl rounded-full animate-pulse" />
        <div className="absolute bottom-0 right-0 w-72 h-72 bg-blue-400/30 blur-3xl rounded-full animate-pulse" />
        <div className="absolute top-1/2 left-1/3 w-96 h-96 bg-purple-500/20 blur-2xl rounded-full animate-pulse" />
      </div>

      <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 mb-6">
        <motion.h1
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-4xl font-bold text-green-400 text-center md:text-left"
        >
          🌍 EcoTracker – Emission Intelligence
        </motion.h1>

        <div className="flex items-center gap-3">
          <label className="text-sm text-green-300">Tone:</label>
          <select
            value={tone}
            onChange={(e) => setTone(e.target.value)}
            className="bg-[#111111] border border-green-500/30 rounded-xl px-3 py-2 text-white"
          >
            <option value="professional">Professional</option>
            <option value="friendly">Friendly</option>
          </select>
        </div>
      </div>

      {apiError && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="max-w-5xl mx-auto mb-4 p-4 rounded-lg bg-red-800/60 border border-red-500 text-red-200 flex items-center gap-2"
        >
          <MdWarning className="text-red-400 text-xl" />
          {apiError}
        </motion.div>
      )}

      <motion.div
        initial="hidden"
        animate="visible"
        className="max-w-5xl mx-auto bg-[#1a1a1a] border border-green-500/20 rounded-3xl p-10 shadow-xl shadow-green-400/10 space-y-6"
      >
        <div className="grid md:grid-cols-2 gap-8">
          {/* Product Type */}
          <motion.div custom={0} variants={fieldVariants}>
            <label className="text-green-300 text-sm mb-1 block">Product Type</label>
            <div className="flex items-center gap-2">
              <FaLeaf className="text-green-400 text-xl" />
              <input
                list="productTypes"
                value={productType}
                onChange={handleInputChange(setProductType)}
                placeholder="Select or type product"
                className="w-full bg-black border border-green-500/30 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-green-400 transition"
              />
              <datalist id="productTypes">
                {defaultProducts.map((type, idx) => (
                  <option key={idx} value={type} />
                ))}
              </datalist>
            </div>
          </motion.div>

          {/* CO2 */}
          <motion.div custom={1} variants={fieldVariants}>
            <label className="text-green-300 text-sm mb-1 block">CO₂ Emissions (tons)</label>
            <div className="flex items-center gap-2">
              <FaCloud className="text-green-400 text-xl" />
              <input
                type="number"
                value={co2}
                onChange={handleInputChange(setCo2)}
                placeholder="e.g., 2.5"
                className="w-full bg-black border border-green-500/30 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-green-400 transition"
              />
            </div>
          </motion.div>

          {/* Water */}
          <motion.div custom={2} variants={fieldVariants}>
            <label className="text-blue-300 text-sm mb-1 block">Water Consumption (liters)</label>
            <div className="flex items-center gap-2">
              <FaTint className="text-blue-400 text-xl" />
              <input
                type="number"
                value={water}
                onChange={handleInputChange(setWater)}
                placeholder="e.g., 850"
                className="w-full bg-black border border-blue-500/30 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
              />
            </div>
          </motion.div>

          {/* Energy */}
          <motion.div custom={3} variants={fieldVariants}>
            <label className="text-yellow-300 text-sm mb-1 block">Energy Consumption (kWh)</label>
            <div className="flex items-center gap-2">
              <FaBolt className="text-yellow-400 text-xl" />
              <input
                type="number"
                value={energy}
                onChange={handleInputChange(setEnergy)}
                placeholder="e.g., 120"
                className="w-full bg-black border border-yellow-500/30 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-yellow-400 transition"
              />
            </div>
          </motion.div>

          {/* Pollutants */}
          <motion.div custom={4} variants={fieldVariants}>
            <label className="text-red-300 text-sm mb-1 block">Pollutants Emitted (grams)</label>
            <div className="flex items-center gap-2">
              <MdWarning className="text-red-400 text-xl" />
              <input
                type="number"
                value={pollutant}
                onChange={handleInputChange(setPollutant)}
                placeholder="e.g., 10"
                className="w-full bg-black border border-red-500/30 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-red-400 transition"
              />
            </div>
          </motion.div>

          {/* Waste */}
          <motion.div custom={5} variants={fieldVariants}>
            <label className="text-gray-300 text-sm mb-1 block">Waste Generation (kg)</label>
            <div className="flex items-center gap-2">
              <FaTrash className="text-gray-400 text-xl" />
              <input
                type="number"
                value={waste}
                onChange={handleInputChange(setWaste)}
                placeholder="e.g., 200"
                className="w-full bg-black border border-gray-500/30 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-gray-400 transition"
              />
            </div>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="text-center mt-10"
        >
          <button
            onClick={handleTrack}
            disabled={loading}
            className={`px-10 py-4 bg-green-500 hover:bg-green-600 text-black font-bold text-lg rounded-2xl shadow-xl shadow-green-400/40 hover:scale-105 transition-all duration-300 ${loading ? "opacity-60 cursor-not-allowed" : ""}`}
          >
            {loading ? "⏳ Tracking..." : "✅ Track Now"}
          </button>
        </motion.div>
      </motion.div>

      {/* --- Result Section --- */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-5xl mx-auto mt-10 bg-[#111111]/90 border border-green-500 rounded-3xl p-8 text-green-200 shadow-lg space-y-6"
        >
          {/* Debug: Check what's in the result object */}
          {console.log("API Result:", result)}
          
          {/* 🌿 Eco Level + Update Date */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
            <h3 className="text-2xl font-bold text-green-400 flex items-center gap-2">
              🌿 Eco Level: <span className="text-white">{result.eco_level}</span>
            </h3>
            <p className="text-sm text-gray-400">Updated: {new Date().toLocaleDateString()}</p>
          </div>

          {/* CO₂ and Water Consumption */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-green-900/30 p-4 rounded-xl shadow-inner flex flex-col items-center">
              <p className="text-green-300 font-semibold text-center">CO₂ Emissions</p>
              <p className="text-white text-lg font-bold">{result.co2} tons</p>
            </div>
            <div className="bg-blue-900/30 p-4 rounded-xl shadow-inner flex flex-col items-center">
              <p className="text-blue-300 font-semibold text-center">Water Consumption</p>
              <p className="text-white text-lg font-bold">{result.water} liters</p>
            </div>
          </div>

          {/* Gemini Analysis */}
          {result.analysis && (
            <div className="space-y-4">
              {/* Handle object format with reason, suggestions, prediction */}
              {typeof result.analysis === 'object' && result.analysis !== null && (
                <>
                  {result.analysis.reason && (
                    <div className="bg-[#222]/50 p-4 rounded-xl border-l-4 border-green-400">
                      <h4 className="font-semibold text-green-300 mb-2">📌 Reason:</h4>
                      <p className="text-white text-sm leading-relaxed">
                        {result.analysis.reason}
                      </p>
                    </div>
                  )}

                  {result.analysis.suggestions && (
                    <div className="bg-[#222]/50 p-4 rounded-xl border-l-4 border-yellow-400">
                      <h4 className="font-semibold text-yellow-300 mb-2">💡 Suggestions:</h4>
                      <ul className="list-disc list-inside text-white text-sm space-y-1">
                        {result.analysis.suggestions.map((s, idx) => (
                          <li key={idx}>{s}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {result.analysis.prediction && (
                    <div className="bg-[#222]/50 p-4 rounded-xl border-l-4 border-blue-400">
                      <h4 className="font-semibold text-blue-300 mb-2">🔮 Prediction:</h4>
                      <p className="text-white text-sm leading-relaxed">
                        {result.analysis.prediction}
                      </p>
                    </div>
                  )}
                </>
              )}
              
              {/* Handle string format (fallback) */}
              {typeof result.analysis === 'string' && (
                <div className="bg-[#222]/50 p-4 rounded-xl border-l-4 border-green-400">
                  <h4 className="font-semibold text-green-300 mb-2">📌 Analysis:</h4>
                  <p className="text-white text-sm leading-relaxed whitespace-pre-line">
                    {result.analysis}
                  </p>
                </div>
              )}
            </div>
          )}
        </motion.div>
      )}
    {/* --- Chart --- */}
      <motion.div className="mt-16 max-w-5xl mx-auto bg-[#111111]/80 border border-green-500 rounded-2xl p-8 text-center text-green-400 shadow-lg">
        <h3 className="text-xl mb-6">📊 Live Emission Chart</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#444" />
            <XAxis dataKey="name" stroke="#aaa" />
            <YAxis stroke="#aaa" />
            <Tooltip />
            <Line type="monotone" dataKey="CO2" stroke="#82ca9d" strokeWidth={2} />
            <Line type="monotone" dataKey="Water" stroke="#8884d8" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </motion.div>
    </div>
  );
};
export default TrackerPage;