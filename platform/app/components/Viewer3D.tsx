"use client";

// PoC de visor 3D — ver CAD_FORMAT_MATRIX.md: solo STL/3MF tienen preview
// en el MVP. rotate/pan/zoom via OrbitControls, sin edicion.

import { Suspense, useMemo } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Stage } from "@react-three/drei";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";
import { useLoader } from "@react-three/fiber";
import * as THREE from "three";

function StlMesh({ url }: { url: string }) {
  const geometry = useLoader(STLLoader, url);
  return (
    <mesh geometry={geometry as THREE.BufferGeometry} rotation={[-Math.PI / 2, 0, 0]}>
      <meshStandardMaterial color="#9aa5b1" />
    </mesh>
  );
}

export function Viewer3D({ artifactUrl, fileType }: { artifactUrl: string; fileType: string }) {
  const supported = useMemo(() => ["stl"].includes(fileType.toLowerCase()), [fileType]);

  if (!supported) {
    return (
      <div className="card">
        <p>
          Preview no disponible para archivos <code>.{fileType}</code> en el MVP (ver
          platform/CAD_FORMAT_MATRIX.md). Formatos soportados hoy: STL. Descargá el archivo
          directamente.
        </p>
      </div>
    );
  }

  return (
    <div style={{ height: 360, background: "#05060a", borderRadius: 8 }}>
      <Canvas camera={{ position: [50, 50, 50], fov: 45 }}>
        <Suspense fallback={null}>
          <Stage environment={null} intensity={0.6}>
            <StlMesh url={artifactUrl} />
          </Stage>
        </Suspense>
        <OrbitControls makeDefault />
      </Canvas>
    </div>
  );
}
