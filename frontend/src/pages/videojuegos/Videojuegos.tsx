import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  obtenerVideojuegos,
  type Videojuego,
} from "../../services/videojuegosService";

import "../../styles/videojuegos.css";

const VIDEOJUEGOS_POR_PAGINA = 20;
const ETIQUETAS_CALIFICACION = ["Negativa", "Neutral", "Positiva"] as const;
const ETIQUETAS_SENTIMIENTO = {
  negativo: { clase: "negativa", texto: "Negativa" },
  neutral: { clase: "neutral", texto: "Neutral" },
  positivo: { clase: "positiva", texto: "Positiva" },
} as const;

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
  const [etiqueta, setEtiqueta] = useState("");
  const [etiquetaAplicada, setEtiquetaAplicada] = useState("");
  const [mostrarOpcionesEtiqueta, setMostrarOpcionesEtiqueta] = useState(false);
  const [opcionEtiquetaActiva, setOpcionEtiquetaActiva] = useState(-1);

  useEffect(() => {
    const temporizador = window.setTimeout(() => {
      setPagina(1);
      setFiltroAplicado(busqueda.trim());
      setEtiquetaAplicada(etiqueta.trim());
    }, 300);

    return () => window.clearTimeout(temporizador);
  }, [busqueda, etiqueta]);

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
          etiquetaAplicada,
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
  }, [pagina, filtroAplicado, etiquetaAplicada]);

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
{/*         <button
          type="button"
          className="boton-volver-videojuegos"
          onClick={() => navigate("/")}
        >
          ← Volver al inicio
        </button> */}

        <header className="cabecera-videojuegos">
          <h1>Elige un videojuego</h1>

          <p>
            Selecciona un videojuego para consultar sus reseñas.
          </p>
          <div className="filtros-videojuegos">
            <div className="campo-filtro-videojuegos">
              <label htmlFor="busqueda-videojuego">Buscar por título o categoría</label>
              <input
                id="busqueda-videojuego"
                type="search"
                value={busqueda}
                onChange={(evento) => setBusqueda(evento.target.value)}
                placeholder="Título o categoría"
              />
            </div>
            <div className="campo-filtro-videojuegos">
              <label htmlFor="etiqueta-videojuego">Filtrar por etiqueta</label>
              <div className="control-etiqueta-videojuego">
                <input
                  id="etiqueta-videojuego"
                  type="search"
                  value={etiqueta}
                  role="combobox"
                  aria-autocomplete="list"
                  aria-expanded={mostrarOpcionesEtiqueta}
                  aria-controls="opciones-etiqueta-videojuego"
                  aria-activedescendant={
                    opcionEtiquetaActiva >= 0
                      ? `opcion-etiqueta-${opcionEtiquetaActiva}`
                      : undefined
                  }
                  onFocus={() => setMostrarOpcionesEtiqueta(true)}
                  onBlur={() => setMostrarOpcionesEtiqueta(false)}
                  onChange={(evento) => {
                    setEtiqueta(evento.target.value);
                    setMostrarOpcionesEtiqueta(true);
                    setOpcionEtiquetaActiva(-1);
                  }}
                  onKeyDown={(evento) => {
                    if (evento.key === "ArrowDown") {
                      evento.preventDefault();
                      setMostrarOpcionesEtiqueta(true);
                      setOpcionEtiquetaActiva((actual) =>
                        (actual + 1) % ETIQUETAS_CALIFICACION.length,
                      );
                    } else if (evento.key === "ArrowUp") {
                      evento.preventDefault();
                      setMostrarOpcionesEtiqueta(true);
                      setOpcionEtiquetaActiva((actual) =>
                        actual <= 0
                          ? ETIQUETAS_CALIFICACION.length - 1
                          : actual - 1,
                      );
                    } else if (
                      evento.key === "Enter" &&
                      mostrarOpcionesEtiqueta &&
                      opcionEtiquetaActiva >= 0
                    ) {
                      evento.preventDefault();
                      setEtiqueta(ETIQUETAS_CALIFICACION[opcionEtiquetaActiva]);
                      setMostrarOpcionesEtiqueta(false);
                      setOpcionEtiquetaActiva(-1);
                    } else if (evento.key === "Escape") {
                      setMostrarOpcionesEtiqueta(false);
                      setOpcionEtiquetaActiva(-1);
                    }
                  }}
                  placeholder="Escribe o elige una etiqueta"
                />
                {mostrarOpcionesEtiqueta && (
                  <div
                    className="opciones-etiqueta-videojuego"
                    id="opciones-etiqueta-videojuego"
                    role="listbox"
                    aria-label="Etiquetas de calificación"
                  >
                    {ETIQUETAS_CALIFICACION.map((opcion, indice) => (
                      <button
                        key={opcion}
                        id={`opcion-etiqueta-${indice}`}
                        type="button"
                        role="option"
                        aria-selected={etiqueta === opcion}
                        className={
                          indice === opcionEtiquetaActiva
                            ? "opcion-etiqueta-videojuego opcion-etiqueta-activa"
                            : "opcion-etiqueta-videojuego"
                        }
                        onMouseDown={(evento) => evento.preventDefault()}
                        onClick={() => {
                          setEtiqueta(opcion);
                          setMostrarOpcionesEtiqueta(false);
                          setOpcionEtiquetaActiva(-1);
                        }}
                      >
                        {opcion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
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
                {videojuego.etiqueta_sentimiento && (
                  <span
                    className={`etiqueta-calificacion-videojuego etiqueta-${ETIQUETAS_SENTIMIENTO[videojuego.etiqueta_sentimiento].clase}`}
                    aria-label={`Sentimiento predominante: ${ETIQUETAS_SENTIMIENTO[videojuego.etiqueta_sentimiento].texto}`}
                  >
                    {ETIQUETAS_SENTIMIENTO[videojuego.etiqueta_sentimiento].texto}
                  </span>
                )}

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
                    <span className="conteo-destacado-videojuego">
                      {videojuego.numero_resenas.toLocaleString("es-ES")} reseñas
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
            No se encontraron videojuegos con esos filtros.
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