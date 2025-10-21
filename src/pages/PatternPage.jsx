import React, { useState } from "react";
import { motion } from "framer-motion";
import { FaCloudUploadAlt } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

const PatternPage = () => {
  const navigate = useNavigate();

  const [patternFile, setPatternFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const [productType, setProductType] = useState("");
  const [fabricWidth, setFabricWidth] = useState("");
  const [fabricType, setFabricType] = useState("woven");
  const [seamAllowance, setSeamAllowance] = useState("2");
  const [allowRotation, setAllowRotation] = useState(true);
  const [strategy, setStrategy] = useState("genetic");

  const handlePatternChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith(".dxf")) {
        alert("Please upload a DXF file");
        return;
      }
      setPatternFile(file);
    }
  };

  const handleOptimize = async () => {
    if (!patternFile) {
      alert("Please upload a pattern DXF file.");
      return;
    }
    if (!fabricWidth) {
      alert("Please specify fabric width.");
      return;
    }

    setLoading(true);

    const formData = new FormData();
    formData.append("dxf_file", patternFile); // 🔥 CHANGED THIS LINE
    formData.append("fabric_width", fabricWidth);
    formData.append("fabric_type", fabricType);
    formData.append("seam_allowance", seamAllowance);
    formData.append("allow_rotation", allowRotation ? "true" : "false");
    formData.append("strategy", strategy);

    try {
      const res = await fetch("http://127.0.0.1:5001/optimize", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || "Optimization failed");
      }

      const data = await res.json();
      console.log("Optimization result from backend:", data);

      navigate("/pattern/result", { state: { result: data } });
    } catch (err) {
      console.error("Error during optimization:", err);
      alert(`Error during optimization: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-black text-white px-6 py-16 overflow-hidden">
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-4xl font-bold text-purple-400 text-center mb-10"
      >
        🧵 AI Pattern Optimizer
      </motion.h1>

      {/* Upload box */}
      <div className="max-w-2xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="bg-[#111]/80 border border-purple-500 rounded-3xl p-8 shadow-lg text-center"
        >
          <label
            htmlFor="pattern-upload"
            className="cursor-pointer flex flex-col items-center justify-center gap-4 p-6 border-2 border-dashed border-purple-400 rounded-xl hover:bg-purple-900/20 transition duration-300"
          >
            <FaCloudUploadAlt size={40} className="text-purple-400 animate-bounce" />
            <span className="text-lg">Upload Pattern DXF File</span>
            <span className="text-sm text-gray-400">(CAD pattern file)</span>
            <input
              type="file"
              id="pattern-upload"
              onChange={handlePatternChange}
              accept=".dxf"
              className="hidden"
            />
          </label>
          {patternFile && (
            <p className="mt-4 text-green-400 animate-pulse">
              ✅ {patternFile.name} uploaded
            </p>
          )}
        </motion.div>
      </div>

      {/* Input form */}
      <div className="max-w-3xl mx-auto mt-10 grid grid-cols-1 md:grid-cols-2 gap-6 bg-[#111]/80 border border-purple-500 rounded-3xl p-8 shadow-lg">
        <div>
          <label className="block mb-2 text-purple-300">Product Type</label>
          <select
            value={productType}
            onChange={(e) => setProductType(e.target.value)}
            className="w-full p-2 rounded-lg bg-black border border-purple-400"
          >
            <option value="">Select...</option>
            <option value="shirt">Shirt</option>
            <option value="tshirt">T-Shirt</option>
            <option value="jacket">Jacket</option>
            <option value="jersey">Jersey</option>
            <option value="dress">Dress</option>
            <option value="skirt">Skirt</option>
            <option value="shorts">Shorts</option>
            <option value="hoodie">Hoodie</option>
            <option value="coat">Coat</option>
            <option value="scarf">Scarf</option>
            <option value="bag">Bag / Tote</option>
          </select>
        </div>

        <div>
          <label className="block mb-2 text-purple-300">Fabric Type</label>
          <select
            value={fabricType}
            onChange={(e) => setFabricType(e.target.value)}
            className="w-full p-2 rounded-lg bg-black border border-purple-400"
          >
            <option value="woven">Woven (No Nap)</option>
            <option value="woven_nap">Woven (With Nap)</option>
            <option value="knit">Knit</option>
          </select>
        </div>

        <div>
          <label className="block mb-2 text-purple-300">Fabric Width (mm)</label>
          <input
            type="number"
            value={fabricWidth}
            onChange={(e) => setFabricWidth(e.target.value)}
            placeholder="e.g., 1500"
            className="w-full p-2 rounded-lg bg-black border border-purple-400"
          />
        </div>

        <div>
          <label className="block mb-2 text-purple-300">Seam Allowance (mm)</label>
          <input
            type="number"
            value={seamAllowance}
            onChange={(e) => setSeamAllowance(e.target.value)}
            className="w-full p-2 rounded-lg bg-black border border-purple-400"
          />
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={allowRotation}
            onChange={(e) => setAllowRotation(e.target.checked)}
            className="w-4 h-4"
          />
          <label className="text-purple-300">Allow Rotation</label>
        </div>

        <div>
          <label className="block mb-2 text-purple-300">Optimization Algorithm</label>
          <select
            value={strategy}
            onChange={(e) => setStrategy(e.target.value)}
            className="w-full p-2 rounded-lg bg-black border border-purple-400"
          >
            <option value="genetic">Genetic Algorithm</option>
            <option value="reinforcement">Reinforcement Learning (Future)</option>
          </select>
        </div>
      </div>

      {/* Info box */}
      <div className="max-w-3xl mx-auto mt-6 bg-blue-900/20 border border-blue-500 rounded-xl p-4">
        <h3 className="text-blue-300 font-bold mb-2">ℹ️ How it works:</h3>
        <ul className="text-sm text-gray-300 list-disc pl-5 space-y-1">
          <li>Upload a DXF file containing your pattern pieces</li>
          <li>Specify your fabric width and type</li>
          <li>Our AI will find the most efficient layout to minimize waste</li>
          <li>Download the optimized pattern layout as an SVG file</li>
        </ul>
      </div>

      <div className="text-center mt-10">
        <button
          onClick={handleOptimize}
          disabled={loading}
          className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl shadow-lg disabled:opacity-50 transition-colors"
        >
          {loading ? "🧬 Optimizing with AI..." : "⚡ Run Optimization"}
        </button>
      </div>
    </div>
  );
};

export default PatternPage;
