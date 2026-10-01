import { useNavigate } from "react-router-dom";

import fotoInicio from "../../assets/fotoInicio.png";
import "../../styles/inicio.css";

export default function Inicio() {
  const navigate = useNavigate();

  const irAVideojuegos = () => {
    navigate("/videojuegos");
  };

  return (
    <main className="inicio">
      <section className="hero">
        <h1>¿Juegas a videojuegos?</h1>

        <p>¡Mira si tiene buenas reseñas!</p>

        <img className="hero-imagen" src={fotoInicio} alt="Videojuegos" />

        <button
          type="button"
          className="hero-boton"
          onClick={irAVideojuegos}
        >
          ALLÁ VAMOS
        </button>
      </section>
    </main>
  );
}