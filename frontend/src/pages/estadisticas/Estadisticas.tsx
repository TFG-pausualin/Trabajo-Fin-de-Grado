import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  obtenerMetricasGlobales,
  obtenerMetricasVideojuego,
  obtenerPrediccionesRecientes,
  type ListaPrediccionesRecientes,
  type MetricasGlobales,
  type MetricasVideojuego,
} from "../../services/metricasService";
import {
  obtenerVideojuegos,
  type Videojuego,
} from "../../services/videojuegosService";

import "../../styles/estadisticas.css";

const SENTIMIENTOS = [
  { clave: "positivas", porcentaje: "porcentaje_positivas", texto: "Positivas", clase: "positivo" },
  { clave: "neutrales", porcentaje: "porcentaje_neutrales", texto: "Neutrales", clase: "neutral" },
  { clave: "negativas", porcentaje: "porcentaje_negativas", texto: "Negativas", clase: "negativo" },
] as const;

const ETIQUETAS_SENTIMIENTO = {
  positivo: "Positiva",
  neutral: "Neutral",
  negativo: "Negativa",
} as const;

function formatoNumero(valor: number): string {
  return valor.toLocaleString("es-ES");
}

function formatoFecha(valor: string): string {
  return new Date(valor).toLocaleString("es-ES", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function Estadisticas() {
  const navigate = useNavigate();
  const [metricas, setMetricas] = useState<MetricasGlobales | null>(null);
  const [predicciones, setPredicciones] =
    useState<ListaPrediccionesRecientes | null>(null);
  const [cargando, setCargando] = useState(true);
  const [intento, setIntento] = useState(0);
  const [error, setError] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [resultadosBusqueda, setResultadosBusqueda] = useState<Videojuego[]>([]);
  const [errorBusqueda, setErrorBusqueda] = useState("");
  const [videojuegoSeleccionado, setVideojuegoSeleccionado] =
    useState<Videojuego | null>(null);
  const [metricasVideojuego, setMetricasVideojuego] =
    useState<MetricasVideojuego | null>(null);
  const [cargandoVideojuego, setCargandoVideojuego] = useState(false);
  const [errorVideojuego, setErrorVideojuego] = useState("");

  useEffect(() => {
    let activa = true;

    async function cargarDatos() {
      setCargando(true);
      setError("");

      try {
        const [respuestaMetricas, respuestaPredicciones] = await Promise.all([
          obtenerMetricasGlobales(),
          obtenerPrediccionesRecientes(),
        ]);

        if (!activa) return;
        setMetricas(respuestaMetricas);
        setPredicciones(respuestaPredicciones);
      } catch {
        if (activa) setError("No se pudieron cargar las estadísticas.");
      } finally {
        if (activa) setCargando(false);
      }
    }

    cargarDatos();

    return () => {
      activa = false;
    };
  }, [intento]);

  useEffect(() => {
    const actualizarAlVolver = () => {
      if (document.visibilityState === "visible") {
        setIntento((actual) => actual + 1);
      }
    };

    window.addEventListener("focus", actualizarAlVolver);
    document.addEventListener("visibilitychange", actualizarAlVolver);

    return () => {
      window.removeEventListener("focus", actualizarAlVolver);
      document.removeEventListener("visibilitychange", actualizarAlVolver);
    };
  }, []);

  useEffect(() => {
    const termino = busqueda.trim();
    if (termino.length < 2) {
      setResultadosBusqueda([]);
      setErrorBusqueda("");
      return;
    }

    let activa = true;
    const temporizador = window.setTimeout(async () => {
      setErrorBusqueda("");
      try {
        const respuesta = await obtenerVideojuegos(1, 8, termino);
        if (activa) setResultadosBusqueda(respuesta.resultados);
      } catch {
        if (activa) setErrorBusqueda("No se pudieron buscar videojuegos.");
      }
    }, 250);

    return () => {
      activa = false;
      window.clearTimeout(temporizador);
    };
  }, [busqueda]);

  useEffect(() => {
    if (!videojuegoSeleccionado) {
      setMetricasVideojuego(null);
      return;
    }

    let activa = true;
    setCargandoVideojuego(true);
    setErrorVideojuego("");

    obtenerMetricasVideojuego(videojuegoSeleccionado.id)
      .then((respuesta) => {
        if (activa) setMetricasVideojuego(respuesta);
      })
      .catch(() => {
        if (activa) setErrorVideojuego("No se pudieron cargar sus estadísticas.");
      })
      .finally(() => {
        if (activa) setCargandoVideojuego(false);
      });

    return () => {
      activa = false;
    };
  }, [videojuegoSeleccionado, intento]);

  function seleccionarVideojuego(videojuego: Videojuego) {
    setVideojuegoSeleccionado(videojuego);
    setBusqueda("");
    setResultadosBusqueda([]);
  }

  return (
    <main className="pagina-estadisticas">
      <div className="contenido-estadisticas">
        <header className="cabecera-estadisticas">
          <div>
            <p className="eyebrow-estadisticas">CATÁLOGO Y RESEÑAS</p>
            <h1>Estadísticas</h1>
            <p>Una vista general de la valoración y el sentimiento del catálogo.</p>
          </div>
          <button
            type="button"
            className="boton-actualizar-estadisticas"
            onClick={() => setIntento((actual) => actual + 1)}
            disabled={cargando}
          >
            {cargando && metricas ? "Actualizando..." : "Actualizar"}
          </button>
        </header>

        {error && (
          <div className="estado-estadisticas estado-error-estadisticas" role="alert">
            <span>{error}</span>
            <button type="button" onClick={() => setIntento((actual) => actual + 1)}>
              Reintentar
            </button>
          </div>
        )}

        {cargando && !metricas && (
          <p className="estado-estadisticas" role="status">Cargando estadísticas...</p>
        )}

        {metricas && (
          <>
            <section className="indicadores-estadisticas" aria-label="Resumen global">
              <article className="indicador-estadisticas indicador-principal-estadisticas">
                <span>Videojuegos</span>
                <strong>{formatoNumero(metricas.total_videojuegos)}</strong>
              </article>
              <article className="indicador-estadisticas">
                <span>Reseñas analizadas</span>
                <strong>{formatoNumero(metricas.total_resenas)}</strong>
              </article>
              <article className="indicador-estadisticas">
                <span>Puntuación media</span>
                <strong>
                  {metricas.puntuacion_media_global === null
                    ? "—"
                    : `${metricas.puntuacion_media_global.toFixed(2)} / 5`}
                </strong>
              </article>
            </section>

            <div className="rejilla-estadisticas">
              <section className="panel-estadisticas panel-distribucion-estadisticas">
                <div className="encabezado-panel-estadisticas">
                  <div>
                    <h2>Sentimiento de las reseñas</h2>
                    <p>Distribución global por etiqueta</p>
                  </div>
                  <span className={`percepcion-estadisticas sentimiento-${metricas.percepcion_global}`}>
                    {ETIQUETAS_SENTIMIENTO[metricas.percepcion_global]}
                  </span>
                </div>

                <div className="lista-distribucion-estadisticas">
                  {SENTIMIENTOS.map((sentimiento) => {
                    const cantidad = metricas.distribucion[sentimiento.clave];
                    const porcentaje = metricas.distribucion[sentimiento.porcentaje];
                    return (
                      <div className="fila-distribucion-estadisticas" key={sentimiento.clave}>
                        <div className="datos-distribucion-estadisticas">
                          <span className={`punto-sentimiento punto-${sentimiento.clase}`} />
                          <span>{sentimiento.texto}</span>
                          <strong>{formatoNumero(cantidad)}</strong>
                          <span className="porcentaje-distribucion-estadisticas">
                            {porcentaje.toFixed(1)}%
                          </span>
                        </div>
                        <div
                          className="pista-distribucion-estadisticas"
                          role="img"
                          aria-label={`${sentimiento.texto}: ${porcentaje.toFixed(1)} por ciento`}
                        >
                          <span
                            className={`barra-distribucion-estadisticas barra-${sentimiento.clase}`}
                            style={{ width: `${porcentaje}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </section>

              <section className="panel-estadisticas panel-recientes-estadisticas">
                <div className="encabezado-panel-estadisticas">
                  <div>
                    <h2>Predicciones recientes</h2>
                    <p>{predicciones ? `${formatoNumero(predicciones.total)} guardadas` : ""}</p>
                  </div>
                </div>
                {predicciones?.resultados.length ? (
                  <ul className="lista-predicciones-estadisticas">
                    {predicciones.resultados.map((prediccion) => (
                      <li key={prediccion.id}>
                        <button
                          type="button"
                          className="prediccion-reciente-estadisticas"
                          onClick={() => navigate(`/videojuegos/${encodeURIComponent(prediccion.videojuego_id)}/reseñas`)}
                        >
                          <span className="contenido-prediccion-estadisticas">
                            <strong>{prediccion.title || "Reseña sin título"}</strong>
                            <span>{prediccion.videojuego_titulo}</span>
                            <time dateTime={prediccion.created_at}>{formatoFecha(prediccion.created_at)}</time>
                          </span>
                          <span className={`etiqueta-prediccion-estadisticas sentimiento-${prediccion.sentiment}`}>
                            {ETIQUETAS_SENTIMIENTO[prediccion.sentiment]}
                          </span>
                        </button>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="sin-predicciones-estadisticas">Todavía no hay predicciones guardadas.</p>
                )}
              </section>

                <section className="panel-estadisticas panel-videojuego-estadisticas">
              <div className="encabezado-panel-estadisticas">
                <div>
                  <h2>Estadísticas por videojuego</h2>
                  <p>Busca un título para ver su valoración y distribución.</p>
                </div>
              </div>

              <label className="busqueda-estadisticas" htmlFor="buscar-videojuego-estadisticas">
                <span>Videojuego</span>
                <input
                  id="buscar-videojuego-estadisticas"
                  type="search"
                  value={busqueda}
                  onChange={(evento) => setBusqueda(evento.target.value)}
                  placeholder="Escribe al menos dos caracteres"
                  autoComplete="off"
                />
              </label>

              {errorBusqueda && <p className="mensaje-error-estadisticas" role="alert">{errorBusqueda}</p>}
              {resultadosBusqueda.length > 0 && (
                <ul className="resultados-busqueda-estadisticas">
                  {resultadosBusqueda.map((videojuego) => (
                    <li key={videojuego.id}>
                      <button type="button" onClick={() => seleccionarVideojuego(videojuego)}>
                        <span>{videojuego.titulo}</span>
                        <small>{videojuego.id}</small>
                      </button>
                    </li>
                  ))}
                </ul>
              )}

              {videojuegoSeleccionado && (
                <div className="detalle-metricas-videojuego">
                  <div className="titulo-videojuego-estadisticas">
                    <strong>{videojuegoSeleccionado.titulo}</strong>
                    <button type="button" onClick={() => setVideojuegoSeleccionado(null)}>
                      Limpiar
                    </button>
                  </div>
                  {cargandoVideojuego && <p role="status">Cargando métricas...</p>}
                  {errorVideojuego && <p className="mensaje-error-estadisticas" role="alert">{errorVideojuego}</p>}
                  {metricasVideojuego && (
                    <div className="resumen-videojuego-estadisticas">
                      <div>
                        <span>Puntuación media</span>
                        <strong>
                          {metricasVideojuego.puntuacion_media === null
                            ? "Sin puntuaciones"
                            : `${metricasVideojuego.puntuacion_media.toFixed(2)} / 5`}
                        </strong>
                      </div>
                      <div>
                        <span>Valoraciones</span>
                        <strong>{formatoNumero(metricasVideojuego.numero_valoraciones)}</strong>
                      </div>
                      <div>
                        <span>Percepción</span>
                        <strong className={`texto-sentimiento-${metricasVideojuego.percepcion_global}`}>
                          {ETIQUETAS_SENTIMIENTO[metricasVideojuego.percepcion_global]}
                        </strong>
                      </div>
                    </div>
                  )}
                </div>
              )}
              </section>
            </div>
          </>
        )}
      </div>
    </main>
  );
}