import { useEffect, useState, type FormEvent } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";

import {
  analizarSentimiento,
  predecirSentimiento,
  type SolicitudPrediccion,
  type ResultadoAnalisis,
} from "../../services/prediccionService";
import { obtenerDetalleVideojuego } from "../../services/videojuegosService";

import "../../styles/prediccion.css";

export default function Prediccion() {
  const navigate = useNavigate();
  const location = useLocation();
  const { videojuegoId } = useParams();
  const tituloInicial =
    (location.state as { titulo?: string } | null)?.titulo ?? videojuegoId ?? "Videojuego";
  const [tituloVideojuego, setTituloVideojuego] = useState(tituloInicial);

  const [tituloResena, setTituloResena] = useState("");
  const [textoResena, setTextoResena] = useState("");
  const [puntuacion, setPuntuacion] = useState("");
  const [compraVerificada, setCompraVerificada] = useState(false);
  const [urlImagen, setUrlImagen] = useState("");
  const [imagenes, setImagenes] = useState<string[]>([]);
  const [cargando, setCargando] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [guardada, setGuardada] = useState(false);
  const [error, setError] = useState("");
  const [resultado, setResultado] = useState<ResultadoAnalisis | null>(null);

  const solicitudResena: SolicitudPrediccion | null = videojuegoId
    ? {
        videojuego_id: videojuegoId,
        title: tituloResena.trim(),
        text: textoResena.trim(),
        rating: puntuacion ? Number(puntuacion) : null,
        verified_purchase: compraVerificada,
        images: imagenes,
      }
    : null;

  useEffect(() => {
    if (!videojuegoId) return;

    let activa = true;

    obtenerDetalleVideojuego(videojuegoId)
      .then((videojuego) => {
        if (activa) setTituloVideojuego(videojuego.titulo);
      })
      .catch(() => {
        if (activa && !tituloInicial) {
          setTituloVideojuego("Videojuego no disponible");
        }
      });

    return () => {
      activa = false;
    };
  }, [videojuegoId, tituloInicial]);

  useEffect(() => {
    if (!guardada || !videojuegoId) return;

    const temporizador = window.setTimeout(() => {
      navigate(`/videojuegos/${encodeURIComponent(videojuegoId)}/reseñas`, {
        replace: true,
        state: { titulo: tituloVideojuego },
      });
    }, 10_000);

    return () => window.clearTimeout(temporizador);
  }, [guardada, navigate, videojuegoId, tituloVideojuego]);

  const analizarResena = async (evento: FormEvent<HTMLFormElement>) => {
    evento.preventDefault();

    if (!videojuegoId) {
      toast.error("No se ha indicado el videojuego de la reseña");
      return;
    }

    if (!tituloResena.trim()) {
      toast.error("Introduce el título de la reseña");
      return;
    }

    if (!textoResena.trim()) {
      toast.error("Escribe una reseña para poder analizarla");
      return;
    }

    setCargando(true);
    setError("");
    setResultado(null);

    try {
      const respuesta = await analizarSentimiento(solicitudResena!);

      setResultado(respuesta);
      toast.success("Reseña analizada correctamente");
    } catch (errorDePeticion) {
      const mensaje = errorDePeticion instanceof Error
        ? errorDePeticion.message
        : "No se pudo analizar la reseña";
      setError(mensaje);
      toast.error(mensaje);
    } finally {
      setCargando(false);
    }
  };

  const guardarResena = async () => {
    if (!solicitudResena || !resultado || guardada) return;

    setGuardando(true);
    setError("");

    try {
      await predecirSentimiento(solicitudResena);
      setGuardada(true);
      toast.success("Reseña guardada. Volverás a las reseñas en 10 segundos.");
    } catch (errorDePeticion) {
      const mensaje = errorDePeticion instanceof Error
        ? errorDePeticion.message
        : "No se pudo guardar la reseña";
      setError(mensaje);
      toast.error(mensaje);
    } finally {
      setGuardando(false);
    }
  };

  const invalidarAnalisis = () => {
    setResultado(null);
    setError("");
  };

  const agregarImagen = () => {
    const url = urlImagen.trim();
    if (!url) return;

    try {
      const imagenValidada = new URL(url);
      if (!["http:", "https:"].includes(imagenValidada.protocol)) {
        toast.error("La imagen debe usar una URL HTTP o HTTPS");
        return;
      }

      setImagenes((actuales) => [...actuales, url]);
      setUrlImagen("");
      invalidarAnalisis();
    } catch {
      toast.error("Introduce una URL de imagen válida");
    }
  };

  return (
    <main className="prediccion">
      <section className="prediccion-contenido">
        <button
          type="button"
          className="boton-volver"
          onClick={() =>
            navigate(videojuegoId ? `/videojuegos/${videojuegoId}/reseñas` : "/videojuegos")
          }
        >
          Volver al videojuego
        </button>

        <header className="prediccion-cabecera">
          <h1>¿Qué te ha parecido el videojuego?</h1>

          <p>
            Escribe tu opinión y analizaremos el sentimiento de la reseña.
          </p>
        </header>

        <form className="formulario-prediccion" onSubmit={analizarResena}>
          <div className="videojuego-seleccionado-formulario">
            <span>Videojuego</span>
            <strong>{tituloVideojuego}</strong>
            <span>parent_asin: {videojuegoId ?? "No disponible"}</span>
          </div>

          <div className="campo-formulario">
            <label htmlFor="title">Título de la reseña</label>

            <input
              id="title"
              name="title"
              type="text"
              value={tituloResena}
              onChange={(evento) => {
                setTituloResena(evento.target.value);
                invalidarAnalisis();
              }}
              placeholder="Resume tu opinión"
              maxLength={300}
              required
            />
          </div>

          <div className="campo-formulario">
            <label htmlFor="text">Texto de la reseña</label>

            <textarea
              id="text"
              name="text"
              value={textoResena}
              onChange={(evento) => {
                setTextoResena(evento.target.value);
                invalidarAnalisis();
              }}
              placeholder="Escribe aquí tu opinión..."
              rows={7}
              maxLength={10_000}
              required
            />
          </div>

          <div className="campo-formulario">
            <label htmlFor="rating">Puntuación
              <span className="campo-opcional"> (opcional)</span>
            </label>

            <select
              id="rating"
              name="rating"
              value={puntuacion}
              onChange={(evento) => {
                setPuntuacion(evento.target.value);
                invalidarAnalisis();
              }}
            >
              <option value="">Sin puntuación</option>
              <option value="1">1 estrella</option>
              <option value="2">2 estrellas</option>
              <option value="3">3 estrellas</option>
              <option value="4">4 estrellas</option>
              <option value="5">5 estrellas</option>
            </select>
          </div>

          <div className="campo-formulario">
            <label htmlFor="images">
              Imágenes
              <span className="campo-opcional"> (opcional)</span>
            </label>

            <div className="entrada-imagenes-formulario">
              <input
                id="images"
                name="images"
                type="url"
                value={urlImagen}
                onChange={(evento) => {
                  setUrlImagen(evento.target.value);
                  invalidarAnalisis();
                }}
                placeholder="https://..."
              />
              <button type="button" onClick={agregarImagen}>
                Añadir imagen
              </button>
            </div>

            {imagenes.length > 0 && (
              <ul className="lista-imagenes-formulario">
                {imagenes.map((imagen, indice) => (
                  <li key={`${imagen}-${indice}`}>
                    <img src={imagen} alt={`Vista previa ${indice + 1}`} />
                    <span>{imagen}</span>
                    <button
                      type="button"
                      onClick={() =>
                        {
                          setImagenes((actuales) => actuales.filter((_, i) => i !== indice));
                          invalidarAnalisis();
                        }
                      }
                      aria-label={`Quitar imagen ${indice + 1}`}
                    >
                      Quitar
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <label className="opcion-compra-verificada" htmlFor="verified_purchase">
            <input
              id="verified_purchase"
              name="verified_purchase"
              type="checkbox"
              checked={compraVerificada}
              onChange={(evento) => {
                setCompraVerificada(evento.target.checked);
                invalidarAnalisis();
              }}
            >
            </input>
            Compra verificada <span className="campo-opcional"> (opcional)</span>
          </label>

          <button
            type="submit"
            className="boton-analizar"
            disabled={cargando || guardando || guardada}
          >
            {cargando ? "ANALIZANDO..." : "ANALIZAR RESEÑA"}
          </button>
        </form>

        {error && (
          <p className="resultado-prediccion resultado-error" role="alert">
            {error}
          </p>
        )}

        {resultado && (
          <section className="resultado-prediccion" aria-live="polite">
            <span className="resultado-etiqueta">Resultado del análisis</span>
            <strong className={`sentimiento sentimiento-${resultado.sentiment}`}>
              {resultado.sentiment}
            </strong>
            <p>{resultado.review_text_processed}</p>
            <button
              type="button"
              className="boton-analizar"
              onClick={guardarResena}
              disabled={guardando || guardada}
            >
              {guardando ? "GUARDANDO..." : guardada ? "RESEÑA GUARDADA" : "GUARDAR RESEÑA"}
            </button>
            {guardada && (
              <p role="status">
                Reseña guardada. Volverás a las reseñas en 10 segundos.
              </p>
            )}
          </section>
        )}
      </section>
    </main>
  );
}