export interface Videojuego {
  id: string;
  titulo: string;
  puntuacion_media: number | null;
  numero_valoraciones: number;
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

export interface Resena {
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
  sentimiento: "positivo" | "neutral" | "negativo";
}

export interface RespuestaResenas {
  resultados: Resena[];
  pagina: number;
  limite: number;
  total: number;
  total_paginas: number;
}

const URL_VIDEOJUEGOS =
  "http://127.0.0.1:8000/api/videojuegos";

export async function obtenerVideojuegos(
  pagina = 1,
  limite = 20,
): Promise<RespuestaVideojuegos> {
  const parametros = new URLSearchParams({
    pagina: String(pagina),
    limite: String(limite),
  });
  const respuesta = await fetch(`${URL_VIDEOJUEGOS}/?${parametros}`);

  if (!respuesta.ok) {
    throw new Error(
      "No se ha podido obtener el listado de videojuegos",
    );
  }

  const datos: RespuestaVideojuegos = await respuesta.json();

  return datos;
}

export async function obtenerDetalleVideojuego(
  videojuegoId: string,
): Promise<DetalleVideojuego> {
  const respuesta = await fetch(
    `${URL_VIDEOJUEGOS}/${encodeURIComponent(videojuegoId)}`,
  );

  if (!respuesta.ok) {
    throw new Error("No se ha podido obtener el detalle del videojuego");
  }

  return respuesta.json();
}

export async function obtenerResenas(
  videojuegoId: string,
  pagina = 1,
  limite = 20,
): Promise<RespuestaResenas> {
  const parametros = new URLSearchParams({
    pagina: String(pagina),
    limite: String(limite),
  });
  const respuesta = await fetch(
    `${URL_VIDEOJUEGOS}/${encodeURIComponent(videojuegoId)}/resenas?${parametros}`,
  );

  if (!respuesta.ok) {
    throw new Error("No se han podido obtener las reseñas");
  }

  return respuesta.json();
}