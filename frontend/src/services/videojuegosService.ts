import { solicitarApi } from "./api";

export interface Videojuego {
  id: string;
  titulo: string;
  puntuacion_media: number | null;
  numero_valoraciones: number;
  numero_resenas: number;
  etiqueta_sentimiento: "negativo" | "neutral" | "positivo" | null;
  categoria_principal: string | null;
  tienda: string | null;
}

export interface DetalleVideojuego extends Videojuego {
  detalles: Record<string, unknown>;
}

export interface RespuestaVideojuegos {
  resultados: Videojuego[];
  pagina: number;
  limite: number;
  total: number;
  total_paginas: number;
}

export type SentimientoResena = "positivo" | "neutral" | "negativo";

export interface Resena {
  id: string;
  rating: number | null;
  title: string | null;
  text: string;
  images: Record<string, unknown>[];
  asin: string | null;
  parent_asin: string;
  user_id: string | null;
  timestamp: string | null;
  helpful_vote: number | null;
  verified_purchase: boolean | null;
  sentimiento: SentimientoResena | null;
}

export interface RespuestaReseñas {
  resultados: Resena[];
  pagina: number;
  limite: number;
  total: number;
  total_paginas: number;
}

interface ResenaApi {
  id: string;
  titulo: string;
  texto: string;
  puntuacion: number | null;
  compra_verificada: boolean;
  imagenes: unknown;
  usuario_original_id: string | null;
  fecha_original: string | null;
  sentimiento: Resena["sentimiento"];
  creada_en: string;
  asin: string | null;
  parent_asin: string;
  votos_utiles: number;
}

interface RespuestaPaginadaApi<T> {
  count: number;
  results: T[];
}

export async function obtenerVideojuegos(
  pagina = 1,
  limite = 20,
  busqueda = "",
  etiqueta = "",
): Promise<RespuestaVideojuegos> {
  const parametros = new URLSearchParams({
    pagina: String(pagina),
    limite: String(limite),
  });
  if (busqueda) parametros.set("busqueda", busqueda);
  if (etiqueta) parametros.set("etiqueta", etiqueta);
  const datos = await solicitarApi<RespuestaPaginadaApi<Videojuego>>(
    `videojuegos/?${parametros}`,
  );

  return {
    resultados: datos.results,
    pagina,
    limite,
    total: datos.count,
    total_paginas: Math.ceil(datos.count / limite),
  };
}

export async function obtenerDetalleVideojuego(
  videojuegoId: string,
): Promise<DetalleVideojuego> {
  return solicitarApi<DetalleVideojuego>(
    `videojuegos/${encodeURIComponent(videojuegoId)}/`,
  );
}

export async function obtenerReseñas(
  videojuegoId: string,
  pagina = 1,
  limite = 20,
  sentimiento: SentimientoResena | "" = "",
): Promise<RespuestaReseñas> {
  const parametros = new URLSearchParams({
    videojuego: videojuegoId,
    ordering: "-fecha_original,-creada_en",
    pagina: String(pagina),
    limite: String(limite),
  });
  if (sentimiento) parametros.set("sentimiento", sentimiento);
  const datos = await solicitarApi<RespuestaPaginadaApi<ResenaApi>>(
    `resenas/?${parametros}`,
  );
  const resultados = datos.results.map((resena) => ({
    id: resena.id,
    rating: resena.puntuacion,
    title: resena.titulo,
    text: resena.texto,
    images: normalizarImagenes(resena.imagenes),
    asin: resena.asin,
    parent_asin: resena.parent_asin,
    user_id: resena.usuario_original_id,
    timestamp: resena.fecha_original ?? resena.creada_en,
    helpful_vote: resena.votos_utiles,
    verified_purchase: resena.compra_verificada,
    sentimiento: resena.sentimiento,
  }));

  return {
    resultados,
    pagina,
    limite,
    total: datos.count,
    total_paginas: Math.ceil(datos.count / limite),
  };
}

function normalizarImagenes(valor: unknown): Record<string, unknown>[] {
  if (!Array.isArray(valor)) return [];

  return valor.flatMap((imagen) => {
    if (typeof imagen === "string") return [{ large: imagen }];
    if (typeof imagen === "object" && imagen !== null && !Array.isArray(imagen)) {
      return [imagen as Record<string, unknown>];
    }
    return [];
  });
}