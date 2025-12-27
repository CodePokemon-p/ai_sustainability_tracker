import React, { useState } from "react";
import { motion } from "framer-motion";
import { FaCloudUploadAlt, FaDownload, FaFileAlt } from "react-icons/fa";

const ReportPage = () => {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileUpload = (e) => {
    setFile(e.target.files[0]);
    setAnalysis(null);
    setError("");
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    setAnalysis(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("http://127.0.0.1:5002/upload-report", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (data.error) throw new Error(data.error);

      setAnalysis(data);
    } catch (err) {
      setError(err.message || "Error analyzing report");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-black text-white px-6 py-12 overflow-hidden">
      {/* 🔮 Background Glow */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-0 left-10 w-72 h-72 bg-yellow-500/20 blur-3xl rounded-full animate-ping" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-green-500/10 blur-[120px] rounded-full animate-spin-slow" />
        <div className="absolute top-1/3 left-1/2 w-72 h-72 bg-blue-600/10 blur-2xl rounded-full animate-pulse" />
      </div>

      {/* Title */}
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-4xl font-bold text-center text-yellow-400 mb-10"
      >
        📥 Sustainability Report Analyzer
      </motion.h1>

      {/* Upload Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="max-w-3xl mx-auto bg-gradient-to-br from-[#111] to-[#1e1e1e] border border-yellow-400/30 p-8 rounded-3xl shadow-lg shadow-yellow-500/10 backdrop-blur"
      >
        <div className="flex flex-col items-center justify-center gap-6">
          <label className="flex flex-col items-center cursor-pointer">
            <FaCloudUploadAlt className="text-5xl text-yellow-400 mb-2 animate-bounce" />
            <input
              type="file"
              accept=".pdf,.csv,.json"
              onChange={handleFileUpload}
              className="hidden"
            />
            <span className="text-gray-300">Click to Upload .pdf, .json or .csv </span>
          </label>

          {file && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="bg-black/40 border border-yellow-500/30 p-4 rounded-xl flex items-center gap-3 shadow-yellow-500/10 shadow-md"
            >
              <FaFileAlt className="text-yellow-300" />
              <span className="text-sm">{file.name}</span>
            </motion.div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={!file || loading}
            className="px-8 py-3 mt-4 bg-yellow-400 text-black font-semibold rounded-full hover:scale-105 transition-all shadow-md shadow-yellow-500/20 disabled:opacity-30"
          >
            {loading ? "🔍 Analyzing..." : "🚀 Analyze Report"}
          </button>

          {error && <p className="text-red-400 text-sm">{error}</p>}

          {analysis && (
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="mt-6 w-full bg-black/50 border border-green-500/40 rounded-xl p-6 shadow-green-500/20"
            >
              <h2 className="text-lg font-semibold text-green-400 mb-3">
                🧾 Analysis Summary
              </h2>
              <p className="text-gray-300 text-sm mb-2">
                <strong>File:</strong> {analysis.file_analyzed}
              </p>

              <div className="text-sm mb-3">
                <h3 className="text-yellow-300 font-medium mb-1">Metrics:</h3>
                <pre className="bg-[#111] p-3 rounded-lg text-gray-400 overflow-x-auto">
                  {JSON.stringify(analysis.metrics_found, null, 2)}
                </pre>
              </div>

              <h3 className="text-yellow-300 font-medium mb-1">Summary:</h3>
              <p className="text-gray-300 text-sm mb-2">
                {analysis.summary.summary_text}
              </p>
              <p className="text-sm text-gray-400">
                Sentiment:{" "}
                <span className="text-green-400 font-semibold">
                  {analysis.summary.overall_assessment} (
                  {analysis.summary.sentiment_score})
                </span>
              </p>
            </motion.div>
          )}
        </div>
      </motion.div>

      
    </div>
  );
};

export default ReportPage;


