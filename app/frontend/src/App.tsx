import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import { Toaster } from "sonner";

import "./index.css";

import Inicio from "./pages/inicio/Inicio";
import Prediccion from "./pages/prediccion/PrediccionForm";
import Videojuegos from "./pages/videojuegos/Videojuegos";
import Reseñas from "./pages/reseñas/Reseñas";

export default function App() {
  return (
    <Router>
      <Toaster position="top-center" richColors />

      <Routes>
        <Route path="/" element={<Inicio />} />
        <Route path="/videojuegos/:videojuegoId/nueva-reseña" element={<Prediccion />} />
        <Route path="/videojuegos" element={<Videojuegos />} />
        <Route path="/videojuegos/:videojuego/resenas" element={<Reseñas />} />
        <Route path="/videojuegos/:videojuego/reseñas" element={<Reseñas />} />
      </Routes>
    </Router>
  );
}