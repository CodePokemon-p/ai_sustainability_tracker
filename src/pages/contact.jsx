import React, { useState } from "react";
import { motion } from "framer-motion";

const ContactUs = () => {
  const [formData, setFormData] = useState({ name: "", email: "", message: "" });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://localhost:5000/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      if (data.success) setSubmitted(true);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <section className="max-w-3xl mx-auto px-6 py-24">
      <motion.h2
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-3xl font-bold text-green-400 mb-6 glow text-center"
      >
        📩 Contact Us
      </motion.h2>

      {submitted ? (
        <p className="text-green-300 text-center">
          Thank you! We will get back to you soon.
        </p>
      ) : (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="text"
            name="name"
            placeholder="Your Name"
            value={formData.name}
            onChange={handleChange}
            required
            className="p-3 rounded-md border border-gray-600 bg-gray-800 text-white light:bg-white light:text-gray-900"
          />
          <input
            type="email"
            name="email"
            placeholder="Your Email"
            value={formData.email}
            onChange={handleChange}
            required
            className="p-3 rounded-md border border-gray-600 bg-gray-800 text-white light:bg-white light:text-gray-900"
          />
          <textarea
            name="message"
            placeholder="Your Message"
            value={formData.message}
            onChange={handleChange}
            required
            rows={5}
            className="p-3 rounded-md border border-gray-600 bg-gray-800 text-white light:bg-white light:text-gray-900"
          />
          <button
            type="submit"
            className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-md glow transition-all duration-300"
          >
            Send Message
          </button>
        </form>
      )}
    </section>
  );
};

export default ContactUs;
