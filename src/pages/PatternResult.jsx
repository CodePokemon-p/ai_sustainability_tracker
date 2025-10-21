import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

const PatternResult = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const result = location.state?.result;
  const [zoomedImage, setZoomedImage] = useState(null);
  const [isReRunning, setIsReRunning] = useState(false);

  // Debug logging
  console.log("Backend Response:", result);

  if (!result) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-black text-white">
        <h2 className="text-2xl font-bold text-purple-400 mb-3">⚠️ No Result Found</h2>
        <p className="text-gray-400 mb-6">Please go back and run the optimization first.</p>
        <button
          onClick={() => navigate("/pattern")}
          className="px-5 py-2 bg-purple-600 hover:bg-purple-700 rounded-xl shadow-lg"
        >
          🔙 Back to Optimizer
        </button>
      </div>
    );
  }

  // EXACT property names from your backend
  const layoutImageUrl = result.layout_image
    ? `http://127.0.0.1:5001/download/${result.layout_image}`
    : null;

  // Use EXACT backend property names
  const fabricWidth = result.debug_info?.fabric_width || "N/A";
  const utilization = result.metrics?.utilization_percentage || 0;
  const fabricUsedLength = result.metrics?.fabric_used_length || "N/A";
  const fabricUsedArea = result.metrics?.fabric_used_area || "N/A";
  const totalPieceArea = result.metrics?.total_placed_area || "N/A";
  const polygonCount = result.debug_info?.polygon_count || "N/A";
  const processingTime = result.processing_time_seconds || "N/A";

  const handleDownloadReport = () => {
    const report = {
      status: result.status || "Completed",
      fabric_width: fabricWidth,
      metrics: result.metrics || {},
      cv_info: result.cv_info || {},
      debug_info: result.debug_info || {},
      timestamp: result.timestamp || new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "pattern_optimization_report.json";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleReRunSame = async () => {
    try {
      setIsReRunning(true);
      const res = await fetch("http://127.0.0.1:5001/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fabric_width: fabricWidth !== "N/A" ? fabricWidth : 1500,
          mode: "fast",
        }),
      });
      const data = await res.json();
      navigate("/pattern/result", { state: { result: data } });
    } catch (err) {
      console.error("Re-run failed", err);
      setIsReRunning(false);
    }
  };

  const showWarning = result.status === "warning";

  return (
    <div className="relative min-h-screen bg-black text-white px-6 py-16 overflow-hidden">
      {/* Background glow */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-20 left-10 w-72 h-72 bg-purple-500/30 blur-3xl rounded-full animate-pulse" />
        <div className="absolute bottom-0 right-0 w-56 h-56 bg-green-400/20 blur-2xl rounded-full animate-ping" />
      </div>

      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-4xl font-bold text-purple-400 text-center mb-10"
      >
        🎯 Pattern Optimization Result
      </motion.h1>

      <div className="max-w-6xl mx-auto bg-[#111]/80 border border-purple-500 rounded-3xl p-8 shadow-lg">
        {/* Basic info - UPDATED WITH BACKEND PROPERTIES */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div>
            <p className="mb-3">
              <strong className="text-purple-300">Status:</strong>{" "}
              <span className={`${
                result.status === 'warning' ? 'text-yellow-400' : 
                result.status === 'success' ? 'text-green-400' : 
                result.status === 'good' ? 'text-blue-400' : 'text-green-400'
              }`}>
                {result.status || "N/A"}
              </span>
            </p>
            <p className="mb-3">
              <strong className="text-purple-300">Fabric Width:</strong>{" "}
              {fabricWidth !== "N/A" ? `${fabricWidth} mm` : "N/A"}
            </p>
            <p className="mb-3">
              <strong className="text-purple-300">Polygon Count:</strong>{" "}
              {polygonCount}
            </p>
          </div>
          <div>
            <p className="mb-3">
              <strong className="text-purple-300">Processing Time:</strong>{" "}
              {processingTime !== "N/A" ? `${processingTime} seconds` : "N/A"}
            </p>
            <p className="mb-3">
              <strong className="text-purple-300">CV Used:</strong>{" "}
              {result.cv_info?.cv_used ? "✅ Yes" : "❌ No"}
            </p>
            <p className="mb-3">
              <strong className="text-purple-300">Timestamp:</strong>{" "}
              {result.timestamp ? new Date(result.timestamp).toLocaleString() : "N/A"}
            </p>
          </div>
        </div>

        {/* CV Info - NEW SECTION */}
        {result.cv_info && (
          <div className="mt-4 p-4 bg-blue-900/30 border border-blue-400 rounded-xl">
            <h4 className="text-lg font-semibold text-blue-300 mb-2">🤖 Computer Vision Analysis</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <strong>Model Loaded:</strong> {result.cv_info.cv_model_loaded ? "✅" : "❌"}
              </div>
              <div>
                <strong>Confidence:</strong> {result.cv_info.cv_confidence || "N/A"}
              </div>
              <div>
                <strong>Analysis Count:</strong> {result.cv_info.cv_analysis_count || "N/A"}
              </div>
              <div>
                <strong>Success Rate:</strong> {result.cv_info.cv_success_rate ? `${result.cv_info.cv_success_rate}%` : "N/A"}
              </div>
            </div>
          </div>
        )}

        {/* Metrics - UPDATED WITH BACKEND PROPERTIES */}
        {result.metrics && (
          <div className="mt-6 p-6 bg-gradient-to-r from-purple-900/40 to-blue-900/40 rounded-2xl border border-purple-400">
            <h3 className="text-2xl font-semibold text-green-300 mb-4 text-center">
              📊 Optimization Metrics
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="text-center p-4 bg-black/40 rounded-xl">
                <div className="text-4xl font-bold text-green-400 mb-2">
                  {utilization}%
                </div>
                <div className="text-purple-300">Fabric Utilization</div>
              </div>
              <div className="text-center p-4 bg-black/40 rounded-xl">
                <div className="text-3xl font-bold text-blue-400 mb-2">
                  {fabricUsedLength !== "N/A" ? `${fabricUsedLength} mm` : "N/A"}
                </div>
                <div className="text-purple-300">Fabric Used Length</div>
              </div>
              <div className="text-center p-4 bg-black/40 rounded-xl">
                <div className="text-xl font-bold text-yellow-400 mb-2">
                  {fabricUsedArea !== "N/A" ? `${fabricUsedArea} mm²` : "N/A"}
                </div>
                <div className="text-purple-300">Fabric Area Used</div>
              </div>
              <div className="text-center p-4 bg-black/40 rounded-xl">
                <div className="text-xl font-bold text-pink-400 mb-2">
                  {totalPieceArea !== "N/A" ? `${totalPieceArea} mm²` : "N/A"}
                </div>
                <div className="text-purple-300">Total Pattern Area</div>
              </div>
            </div>

            {/* Warning - UPDATED */}
            {showWarning && (
              <div className="mt-6 p-4 bg-yellow-900/40 border border-yellow-400 rounded-xl text-center">
                ⚠️ <span className="text-yellow-300 font-semibold">Warning:</span> Utilization{" "}
                <span className="font-bold">{utilization}%</span> is below optimal level.
                <br />
                Current fabric waste: <span className="text-red-400 font-bold">
                  {100 - utilization}%
                </span>
                <br />
                👉 Try adjusting fabric width or optimization parameters.
              </div>
            )}
          </div>
        )}

        {/* Notes from backend - NEW SECTION */}
        {result.notes && (
          <div className="mt-4 p-4 bg-green-900/20 border border-green-400 rounded-xl">
            <p className="text-green-300 text-center">💡 {result.notes}</p>
          </div>
        )}

        {/* Layout Image */}
        {layoutImageUrl && (
          <div className="mt-10">
            <h3 className="text-2xl font-semibold text-purple-300 mb-6 text-center">
              Optimized Layout
            </h3>
            <div className="bg-black/60 border border-purple-500 rounded-xl p-6 shadow-lg">
              <div className="relative bg-gray-900 rounded-lg p-2 min-h-[400px] flex items-center justify-center">
                <img
                  src={layoutImageUrl}
                  alt="Optimized Layout"
                  className="max-w-full max-h-[500px] mx-auto object-contain rounded-lg cursor-zoom-in"
                  onClick={() => setZoomedImage(layoutImageUrl)}
                />
              </div>

              <div className="flex flex-col sm:flex-row justify-center gap-4 mt-6">
                <a
                  href={layoutImageUrl}
                  download={`optimized_layout_${result.timestamp || Date.now()}.svg`}
                  className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-xl shadow-lg text-center transition-colors"
                >
                  ⬇️ Download SVG Layout
                </a>
                <button
                  onClick={handleDownloadReport}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow-lg transition-colors"
                >
                  📑 Download Report
                </button>
                <button
                  onClick={() => navigate("/pattern")}
                  className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl shadow-lg transition-colors"
                >
                  🔁 Run Again
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Zoom modal */}
      {zoomedImage && (
        <div
          className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4"
          onClick={() => setZoomedImage(null)}
        >
          <div className="relative max-w-4xl w-full">
            <button
              className="absolute -top-12 right-0 text-white text-3xl z-10"
              onClick={() => setZoomedImage(null)}
            >
              ✕
            </button>
            <img
              src={zoomedImage}
              alt="Zoomed Layout"
              className="w-full h-auto max-h-[80vh] object-contain rounded-xl border-2 border-purple-500"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default PatternResult;
