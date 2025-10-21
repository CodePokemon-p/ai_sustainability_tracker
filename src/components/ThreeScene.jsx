// src/components/ThreeScene.jsx
import React, { useRef } from "react";
import { Canvas, useFrame, useLoader } from "@react-three/fiber";
import { TextureLoader } from "three";
import { OrbitControls } from "@react-three/drei";

const RotatingGlobe = () => {
  const meshRef = useRef();
  const colorMap = useLoader(TextureLoader, "/earth.png"); // ✅ earth texture

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.01; // 🌍 Smooth spin
    }
  });

  return (
    <mesh ref={meshRef} scale={[2.5, 2.5, 2.5]}>
      <sphereGeometry args={[1, 64, 64]} />
      <meshStandardMaterial map={colorMap} />
    </mesh>
  );
};

const ThreeScene = () => {
  return (
    <div
      style={{
        width: "100%",
        height: "400px",
        position: "relative",
        background: "transparent", // ✅ FIXED: no more black bg box!
        zIndex: 1,
      }}
      className="bg-transparent dark:bg-transparent light:bg-transparent"
    >
      <Canvas
        camera={{ position: [0, 0, 4] }}
        gl={{ alpha: true }} // ✅ Transparent canvas background
        style={{ background: "transparent" }}
      >
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 5, 5]} intensity={1} />
        <OrbitControls enableZoom={false} autoRotate />
        <RotatingGlobe />
      </Canvas>
    </div>
  );
};

export default ThreeScene;

