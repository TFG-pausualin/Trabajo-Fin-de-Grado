import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

import {
  obtenerDetalleVideojuego,
  obtenerReseñas,
  type DetalleVideojuego,
  type Resena,
} from "../../services/videojuegosService";

import "../../styles/reseñas.css";

const RESEÑAS_POR_PAGINA = 20;

function obtenerImagenes(valor: unknown): Record<string, unknown>[] {
  if (!Array.isArray(valor)) return [];

  return valor.filter(
    (imagen): imagen is Record<string, unknown> =>
      typeof imagen === "object" && imagen !== null && !Array.isArray(imagen),
  );
}

function urlImagen(imagen: Record<string, unknown>): string | null {
  for (const campo of [
    "hi_res",
    "large",
    "large_image_url",
    "medium_image_url",
    "thumb",
    "small_image_url",
  ]) {
    const valor = imagen[campo];
    if (typeof valor === "string" && valor.trim()) return valor;
  }

  return null;
}

function formatearDetalle(valor: unknown): string {
  if (Array.isArray(valor)) {
    return valor.map(formatearDetalle).filter(Boolean).join("; ");
  }

  if (typeof valor === "object" && valor !== null) {
    return Object.entries(valor as Record<string, unknown>)
      .map(([clave, contenido]) => `${clave}: ${formatearDetalle(contenido)}`)
      .filter((entrada) => !entrada.endsWith(": "))
      .join("; ");
  }

  if (typeof valor === "boolean") return valor ? "Sí" : "No";
  if (valor === null || valor === undefined) return "";
  return String(valor);
}

function etiquetaDetalle(campo: string): string {
  return campo
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letra) => letra.toLocaleUpperCase("es-ES"));
}

export default function Reseñas() {
  const navigate = useNavigate();
  const location = useLocation();
  const { videojuego: videojuegoId } = useParams();
  const titulo = (location.state as { titulo?: string } | null)?.titulo;
  const [videojuego, setVideojuego] = useState<DetalleVideojuego | null>(null);
  const [cargandoDetalle, setCargandoDetalle] = useState(true);
  const [errorDetalle, setErrorDetalle] = useState("");
  const [reseñas, setReseñas] = useState<Resena[]>([]);
  const [pagina, setPagina] = useState(1);
  const [total, setTotal] = useState(0);
  const [totalPaginas, setTotalPaginas] = useState(0);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const nombreVideojuego = videojuego?.titulo ?? titulo ?? videojuegoId ?? "Videojuego";

  useEffect(() => {
    let activa = true;

    async function cargarDetalle() {
      if (!videojuegoId) return;

      setCargandoDetalle(true);
      setErrorDetalle("");

      try {
        const respuesta = await obtenerDetalleVideojuego(videojuegoId);
        if (activa) setVideojuego(respuesta);
      } catch {
        if (activa) setErrorDetalle("No se pudo cargar la ficha del videojuego");
      } finally {
        if (activa) setCargandoDetalle(false);
      }
    }

    cargarDetalle();

    return () => {
      activa = false;
    };
  }, [videojuegoId]);

  useEffect(() => {
    let activa = true;

    async function cargarReseñas() {
      if (!videojuegoId) return;

      setCargando(true);
      setError("");

      try {
        const respuesta = await obtenerReseñas(
          videojuegoId,
          pagina,
          RESEÑAS_POR_PAGINA,
        );

        if (!activa) return;
        setReseñas(respuesta.resultados);
        setTotal(respuesta.total);
        setTotalPaginas(respuesta.total_paginas);
      } catch {
        if (activa) setError("No se pudieron cargar las reseñas");
      } finally {
        if (activa) setCargando(false);
      }
    }

    cargarReseñas();

    return () => {
      activa = false;
    };
  }, [videojuegoId, pagina]);

  const escribirResena = () => {
    if (!videojuegoId) return;

    navigate(
      `/videojuegos/${encodeURIComponent(videojuegoId)}/nueva-reseña`,
      { state: { titulo: nombreVideojuego } },
    );
  };

  const imagenesProducto = obtenerImagenes(videojuego?.detalles.images);
  const camposDetalle = Object.entries(videojuego?.detalles ?? {}).filter(
    ([campo]) => !["images", "title", "average_rating", "rating_number"].includes(campo),
  );

  return (
    <main className="pagina-reseñas">
      <section className="contenido-reseñas">
        <button
          type="button"
          className="boton-volver-reseñas"
          onClick={() => navigate("/videojuegos")}
        >
          ← Volver a videojuegos
        </button>

        <header className="cabecera-reseñas">
          <span className="etiqueta-videojuego">
            Videojuego seleccionado
          </span>

          <h1>{nombreVideojuego}</h1>

          <p>
            Consulta las opiniones disponibles o escribe una nueva reseña.
          </p>
        </header>

        {cargandoDetalle && (
          <p className="mensaje-reseñas">Cargando ficha del videojuego...</p>
        )}

        {errorDetalle && (
          <p className="mensaje-reseñas mensaje-error-reseñas">{errorDetalle}</p>
        )}

        {videojuego && (
          <section className="detalle-videojuego" aria-label="Ficha del videojuego">
            <div className="resumen-detalle-videojuego">
              {imagenesProducto.slice(0, 1).map((imagen, indice) => {
                const url = urlImagen(imagen);
                return url ? (
                  <img
                    key={`${url}-${indice}`}
                    className="imagen-detalle-videojuego"
                    src={url}
                    alt={nombreVideojuego}
                  />
                ) : null;
              })}
              <div className="metricas-detalle-videojuego">
                <span>
                  {videojuego.puntuacion_media === null
                    ? "Sin valoración media"
                    : `${videojuego.puntuacion_media.toFixed(1)} / 5`}
                </span>
                <span>
                  {videojuego.numero_valoraciones.toLocaleString("es-ES")} valoraciones
                </span>
              </div>
            </div>

            {imagenesProducto.length > 1 && (
              <div className="galeria-imagenes-videojuego">
                {imagenesProducto.slice(1).map((imagen, indice) => {
                  const url = urlImagen(imagen);
                  return url ? (
                    <img
                      key={`${url}-${indice}`}
                      src={url}
                      alt={`${nombreVideojuego}, imagen ${indice + 2}`}
                      loading="lazy"
                    />
                  ) : null;
                })}
              </div>
            )}

            {camposDetalle.length > 0 && (
              <dl className="campos-detalle-videojuego">
                {camposDetalle.map(([campo, valor]) => (
                  <div className="campo-detalle-videojuego" key={campo}>
                    <dt>{etiquetaDetalle(campo)}</dt>
                    <dd>{formatearDetalle(valor)}</dd>
                  </div>
                ))}
              </dl>
            )}
          </section>
        )}

        <div className="acciones-reseñas">
          <h2>Reseñas etiquetadas ({total.toLocaleString("es-ES")})</h2>

          <button
            type="button"
            className="boton-nueva-resena"
            onClick={escribirResena}
          >
            Escribir una reseña
          </button>
        </div>

        {cargando && <p className="mensaje-reseñas">Cargando reseñas...</p>}

        {error && <p className="mensaje-reseñas mensaje-error-reseñas">{error}</p>}

        {!cargando && !error && reseñas.length > 0 && (
          <div className="lista-reseñas">
            {reseñas.map((resena, indice) => (
              <article
                key={`${resena.asin ?? "sin-asin"}-${resena.timestamp ?? "sin-fecha"}-${indice}`}
                className="tarjeta-resena"
              >
                <div className="cabecera-tarjeta-resena">
                  <span
                    className={`sentimiento sentimiento-${resena.sentimiento}`}
                  >
                    {resena.sentimiento}
                  </span>

                  <div className="datos-cabecera-resena">
                    {resena.rating !== null && (
                      <span
                        className="puntuacion-resena"
                        aria-label={`${resena.rating} de 5 estrellas`}
                      >
                        {"★".repeat(resena.rating)}
                        <span className="estrellas-vacias">
                          {"★".repeat(5 - resena.rating)}
                        </span>
                      </span>
                    )}

                    {resena.timestamp && (
                      <time dateTime={resena.timestamp}>
                        {new Date(resena.timestamp).toLocaleDateString("es-ES")}
                      </time>
                    )}
                  </div>
                </div>

                {resena.title && <h3 className="titulo-resena">{resena.title}</h3>}
                <p className="texto-resena">{resena.text}</p>

                {resena.images.length > 0 && (
                  <div className="imagenes-resena">
                    {resena.images.map((imagen, indice) => {
                      const url = urlImagen(imagen);
                      return url ? (
                        <img
                          key={`${url}-${indice}`}
                          src={url}
                          alt={`Imagen adjunta a la reseña ${indice + 1}`}
                          loading="lazy"
                        />
                      ) : null;
                    })}
                  </div>
                )}

                <dl className="metadatos-resena">
                  {resena.user_id && (
                    <div><dt>Usuario</dt><dd>{resena.user_id}</dd></div>
                  )}
                  {resena.asin && (
                    <div><dt>ASIN</dt><dd>{resena.asin}</dd></div>
                  )}
                  <div><dt>Videojuego</dt><dd>{resena.parent_asin}</dd></div>
                  {resena.helpful_vote !== null && (
                    <div><dt>Votos útiles</dt><dd>{resena.helpful_vote}</dd></div>
                  )}
                  {resena.verified_purchase !== null && (
                    <div>
                      <dt>Compra verificada</dt>
                      <dd>{resena.verified_purchase ? "Sí" : "No"}</dd>
                    </div>
                  )}
                </dl>
              </article>
            ))}
          </div>
        )}

        {!cargando && !error && reseñas.length === 0 && (
          <div className="sin-reseñas">
            <h2>Todavía no hay reseñas</h2>
            <p>No hay reseñas etiquetadas disponibles para {nombreVideojuego}.</p>
          </div>
        )}

        {!cargando && !error && total > 0 && (
          <nav className="paginacion-reseñas" aria-label="Paginación de reseñas">
            <button
              type="button"
              className="control-paginacion-reseñas"
              onClick={() => setPagina((actual) => actual - 1)}
              disabled={pagina <= 1}
            >
              Anterior
            </button>
            <span aria-live="polite">
              Página {pagina} de {totalPaginas} · {total} reseñas
            </span>
            <button
              type="button"
              className="control-paginacion-reseñas"
              onClick={() => setPagina((actual) => actual + 1)}
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