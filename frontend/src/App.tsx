import { BrowserRouter as Router, NavLink, Route, Routes } from "react-router-dom";
import { Toaster } from "sonner";

import "./index.css";

import Inicio from "./pages/inicio/Inicio";
import Prediccion from "./pages/prediccion/PrediccionForm";
import Estadisticas from "./pages/estadisticas/Estadisticas";
import Videojuegos from "./pages/videojuegos/Videojuegos";
import Reseñas from "./pages/reseñas/Reseñas";

export default function App() {
  return (
    <Router>
      <Toaster position="top-center" richColors />

      <header className="barra-navegacion">
        <nav className="enlaces-navegacion" aria-label="Navegación principal">
          <NavLink to="/" end>
            Inicio
          </NavLink>
          <NavLink to="/videojuegos">
            Videojuegos
          </NavLink>
          <NavLink to="/estadisticas">
            Estadísticas
          </NavLink>
        </nav>
      </header>

      <Routes>
        <Route path="/" element={<Inicio />} />
        <Route path="/estadisticas" element={<Estadisticas />} />
        <Route path="/videojuegos/:videojuegoId/nueva-reseña" element={<Prediccion />} />
        <Route path="/videojuegos" element={<Videojuegos />} />
        <Route path="/videojuegos/:videojuego/reseñas" element={<Reseñas />} />
      </Routes>
    </Router>
  );
}