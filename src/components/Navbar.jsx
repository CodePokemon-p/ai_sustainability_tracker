import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { HiMenu, HiX } from "react-icons/hi";

const Navbar = () => {
  const [darkMode, setDarkMode] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const toggleTheme = () => {
    document.documentElement.classList.toggle("light-mode");
    setDarkMode(!darkMode);
  };

  const toggleMenu = () => setMenuOpen(!menuOpen);
  const isActive = (path) => location.pathname === path;

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const isLoggedIn = !!localStorage.getItem("token");

  return (
    <header className="sticky top-0 z-50 bg-black text-white shadow-md">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex justify-between items-center relative">
        {/* Logo */}
        <Link to="/" className="text-2xl font-bold text-green-400 hover:text-green-300 transition-all duration-300">
          🌿 EcoTrack
        </Link>

        {/* Desktop Nav */}
        <ul className="hidden md:flex gap-6 text-sm font-medium items-center">
          <li><Link to="/" className={`${isActive("/") ? "text-green-400" : "hover:text-green-300"}`}>Home</Link></li>
          <li><Link to="/about" className={`${isActive("/about") ? "text-green-400" : "hover:text-green-300"}`}>About</Link></li>
          <li><Link to="/features" className={`${isActive("/features") ? "text-green-400" : "hover:text-green-300"}`}>Features</Link></li>
          <li><Link to="/dashboard" className={`${isActive("/dashboard") ? "text-green-400" : "hover:text-green-300"}`}>Dashboard</Link></li>

          {!isLoggedIn && (
            <>
              <li>
                <Link to="/signup" className={`px-4 py-2 rounded-xl font-semibold border-2 transition duration-300 ${isActive("/signup")
                  ? "bg-green-500 text-black border-green-500 shadow-lg shadow-green-500/40"
                  : "text-green-400 border-green-400 hover:bg-green-500 hover:text-black"
                }`}>
                  Sign Up
                </Link>
              </li>
              <li>
                <Link to="/login" className={`px-4 py-2 rounded-xl font-semibold border-2 transition duration-300 ${isActive("/login")
                  ? "bg-green-500 text-black border-green-500 shadow-lg shadow-green-500/40"
                  : "text-green-400 border-green-400 hover:bg-green-500 hover:text-black"
                }`}>
                  Log In
                </Link>
              </li>
            </>
          )}

          {isLoggedIn && (
            <li>
              <button onClick={handleLogout} className="px-4 py-2 rounded-xl font-semibold bg-red-500 text-black hover:bg-red-600 transition">
                Logout
              </button>
            </li>
          )}

          <li>
            <button onClick={toggleTheme} className="ml-2 text-xl">{darkMode ? "🌞" : "🌙"}</button>
          </li>
        </ul>

        {/* Mobile Menu Button */}
        <div className="md:hidden flex items-center gap-4">
          <button onClick={toggleTheme} className="text-xl">
            {darkMode ? "🌞" : "🌙"}
          </button>
          <button onClick={toggleMenu} className="text-2xl text-green-400">
            {menuOpen ? <HiX /> : <HiMenu />}
          </button>
        </div>

        {/* Mobile Dropdown */}
        {menuOpen && (
          <div className="absolute top-16 left-0 w-full bg-[#111] border-t border-green-500 shadow-lg md:hidden flex flex-col px-6 py-4 space-y-4 z-50">
            <Link to="/" onClick={toggleMenu} className={`${isActive("/") ? "text-green-400" : "text-white hover:text-green-300"}`}>Home</Link>
            <Link to="/about" onClick={toggleMenu} className={`${isActive("/about") ? "text-green-400" : "text-white hover:text-green-300"}`}>About</Link>
            <Link to="/features" onClick={toggleMenu} className={`${isActive("/features") ? "text-green-400" : "text-white hover:text-green-300"}`}>Features</Link>
            <Link to="/dashboard" onClick={toggleMenu} className={`${isActive("/dashboard") ? "text-green-400" : "text-white hover:text-green-300"}`}>Dashboard</Link>

            {!isLoggedIn && (
              <>
                <Link to="/signup" onClick={toggleMenu} className={`px-4 py-2 rounded-xl font-semibold border-2 transition duration-300 text-center ${isActive("/signup")
                  ? "bg-green-500 text-black border-green-500 shadow-green-500/40 shadow"
                  : "text-green-400 border-green-400 hover:bg-green-500 hover:text-black"
                }`}>Sign Up</Link>

                <Link to="/login" onClick={toggleMenu} className={`px-4 py-2 rounded-xl font-semibold border-2 transition duration-300 text-center ${isActive("/login")
                  ? "bg-green-500 text-black border-green-500 shadow-green-500/40 shadow"
                  : "text-green-400 border-green-400 hover:bg-green-500 hover:text-black"
                }`}>Log In</Link>
              </>
            )}

            {isLoggedIn && (
              <button
                onClick={() => {
                  toggleMenu();
                  handleLogout();
                }}
                className="w-full px-4 py-2 rounded-xl font-semibold bg-red-500 text-black hover:bg-red-600 transition"
              >
                Logout
              </button>
            )}
          </div>
        )}
      </nav>
    </header>
  );
};

export default Navbar;
