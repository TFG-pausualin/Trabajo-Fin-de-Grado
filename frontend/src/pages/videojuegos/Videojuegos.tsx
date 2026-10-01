import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  obtenerVideojuegos,
  type Videojuego,
} from "../../services/videojuegosService";

import "../../styles/videojuegos.css";

const VIDEOJUEGOS_POR_PAGINA = 20;

export default function Videojuegos() {
  const navigate = useNavigate();

  const [videojuegos, setVideojuegos] = useState<Videojuego[]>([]);
  const [pagina, setPagina] = useState(1);
  const [total, setTotal] = useState(0);
  const [totalPaginas, setTotalPaginas] = useState(0);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [filtroAplicado, setFiltroAplicado] = useState("");

  useEffect(() => {
    const temporizador = window.setTimeout(() => {
      setPagina(1);
      setFiltroAplicado(busqueda.trim());
    }, 300);

    return () => window.clearTimeout(temporizador);
  }, [busqueda]);

  useEffect(() => {
    let activa = true;

    async function cargarVideojuegos() {
      setCargando(true);
      setError("");

      try {
        const respuesta = await obtenerVideojuegos(
          pagina,
          VIDEOJUEGOS_POR_PAGINA,
          filtroAplicado,
        );

        if (!activa) return;
        setVideojuegos(respuesta.resultados);
        setTotal(respuesta.total);
        setTotalPaginas(respuesta.total_paginas);
      } catch {
        if (activa) {
          setError("No se pudieron cargar los videojuegos");
        }
      } finally {
        if (activa) {
          setCargando(false);
        }
      }
    }

    cargarVideojuegos();

    return () => {
      activa = false;
    };
  }, [pagina, filtroAplicado]);

  function seleccionarVideojuego(videojuego: Videojuego) {
    navigate(`/videojuegos/${videojuego.id}/reseñas`, {
      state: {
        titulo: videojuego.titulo,
      },
    });
  }

  return (
    <main className="pagina-videojuegos">
      <section className="contenido-videojuegos">
        <button
          type="button"
          className="boton-volver-videojuegos"
          onClick={() => navigate("/")}
        >
          ← Volver al inicio
        </button>

        <header className="cabecera-videojuegos">
          <h1>Elige un videojuego</h1>

          <p>
            Selecciona un videojuego para consultar sus reseñas.
          </p>

          <div className="buscador-videojuegos">
            <label htmlFor="busqueda-videojuego">Buscar por título</label>
            <input
              id="busqueda-videojuego"
              type="search"
              value={busqueda}
              onChange={(evento) => setBusqueda(evento.target.value)}
              placeholder="Título, categoría o etiqueta"
            />
          </div>
        </header>

        {cargando && (
          <p className="mensaje-videojuegos">
            Cargando videojuegos...
          </p>
        )}

        {error && (
          <p className="mensaje-videojuegos mensaje-error">
            {error}
          </p>
        )}

        {!cargando && !error && videojuegos.length > 0 && (
          <div className="lista-videojuegos">
            {videojuegos.map((videojuego) => (
              <button
                key={videojuego.id}
                type="button"
                className="tarjeta-videojuego"
                onClick={() =>
                  seleccionarVideojuego(videojuego)
                }
              >
                <span
                  className="icono-videojuego"
                  aria-hidden="true"
                >
                  🎮
                </span>

                <span className="informacion-videojuego">
                  <span className="nombre-videojuego">
                    {videojuego.titulo}
                  </span>

                  <span className="metricas-destacadas-videojuego">
                    <span className="media-destacada-videojuego">
                      {videojuego.puntuacion_media === null
                        ? "Sin media"
                        : `${videojuego.puntuacion_media.toFixed(1)} / 5`}
                    </span>
                    {videojuego.puntuacion_media !== null && (
                      <span className="etiqueta-calificacion-videojuego">
                        {obtenerEtiquetaCalificacion(videojuego.puntuacion_media)}
                      </span>
                    )}
                    <span className="conteo-destacado-videojuego">
                      {videojuego.numero_valoraciones.toLocaleString("es-ES")} valoraciones
                    </span>
                  </span>

                  <span className="datos-videojuego">
                    {videojuego.categoria_principal && (
                      <span>
                        Categoría: {videojuego.categoria_principal}
                      </span>
                    )}

                    {videojuego.tienda && (
                      <span>Tienda: {videojuego.tienda}</span>
                    )}

                  </span>
                </span>

                <span
                  className="flecha-videojuego"
                  aria-hidden="true"
                >
                  →
                </span>
              </button>
            ))}
          </div>
        )}

        {!cargando && !error && videojuegos.length === 0 && (
          <p className="sin-resultados">
            No se encontraron videojuegos{filtroAplicado ? ` para "${filtroAplicado}"` : ""}.
          </p>
        )}

        {!cargando && !error && total > 0 && (
          <nav
            className="paginacion-videojuegos"
            aria-label="Paginación de videojuegos"
          >
            <button
              type="button"
              className="control-paginacion"
              onClick={() => setPagina((paginaActual) => paginaActual - 1)}
              disabled={pagina <= 1}
            >
              Anterior
            </button>

            <span className="estado-paginacion" aria-live="polite">
              Mostrando {(pagina - 1) * VIDEOJUEGOS_POR_PAGINA + 1}–
              {Math.min(pagina * VIDEOJUEGOS_POR_PAGINA, total)} de {total}
              <span>
                Página {pagina} de {totalPaginas}
              </span>
            </span>

            <button
              type="button"
              className="control-paginacion"
              onClick={() => setPagina((paginaActual) => paginaActual + 1)}
              disabled={pagina >= totalPaginas}
            >
              Siguiente
            </button>
          </nav>
        )}
      </section>
    </main>
  );
}

function obtenerEtiquetaCalificacion(puntuacion: number): string {
  if (puntuacion < 2.5) return "Negativa";
  if (puntuacion < 3.5) return "Neutral";
  return "Positiva";
}