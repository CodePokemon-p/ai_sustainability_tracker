// src/App.jsx
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import LandingPage from "./pages/LandingPage";
import Signup from "./pages/Auth/Signup";
import Login from "./pages/Auth/Login";
import Dashboard from "./pages/Dashboard";
import About from "./pages/About";
import Features from "./pages/Features";
import PatternPage from './pages/PatternPage';
import TrackerPage from './pages/TrackerPage';
import ReportsPage from './pages/ReportsPage';
import ChatbotPage from "./pages/ChatbotPage"; 
import AlertsPage from "./pages/AlertsPage";
import PrivateRoute from "./components/PrivateRoute";
import PatternResult from "./pages/PatternResult";
import ContactUs from "./pages/contact";
import "./index.css";
import { Toaster } from "react-hot-toast"; // ✅ Using only hot-toast

const App = () => {
  return (
    <>
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          
          <Route path="/dashboard" element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          } />

          <Route path="/about" element={
            <PrivateRoute>
              <About />
            </PrivateRoute>
          } />

          <Route path="/features" element={
            <PrivateRoute>
              <Features />
            </PrivateRoute>
          } />

          <Route path="/signup" element={<Signup />} />
          <Route path="/contact" element={<ContactUs />} />
          <Route path="/login" element={<Login />} />
          <Route path="/pattern" element={<PatternPage />} />
           <Route path="/pattern/result" element={<PatternResult />} />
          <Route path="/tracker" element={<TrackerPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/chatbot" element={<ChatbotPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
        </Routes>

        {/* ✅ Only hot-toast being used */}
        <Toaster position="top-right" reverseOrder={false} />
      </Router>
    </>
  );
};

export default App;


