import { solicitarApi } from "./api";

export type Sentimiento = "positivo" | "neutral" | "negativo";

export interface SolicitudPrediccion {
  videojuego_id: string;
  title: string;
  text: string;
  rating: number | null;
  verified_purchase: boolean;
  images: string[];
}

export interface RespuestaPrediccion {
  id: number;
  videojuego: string;
  videojuego_titulo: string;
  parent_asin: string;
  rating: number | null;
  title: string;
  text: string;
  verified_purchase: boolean;
  images: string[];
  review_text_normalized: string;
  review_text_processed: string;
  sentiment: Sentimiento;
  created_at: string;
  updated_at: string;
}

export type ResultadoAnalisis = Pick<
  RespuestaPrediccion,
  "review_text_processed" | "sentiment"
>;

export async function analizarSentimiento(
  solicitud: SolicitudPrediccion,
): Promise<ResultadoAnalisis> {
  return solicitarApi<ResultadoAnalisis>("predicciones/analizar/", {
    method: "POST",
    body: JSON.stringify(solicitud),
  });
}

export async function predecirSentimiento(
  solicitud: SolicitudPrediccion,
): Promise<RespuestaPrediccion> {
  return solicitarApi<RespuestaPrediccion>("predicciones/", {
    method: "POST",
    body: JSON.stringify(solicitud),
  });
}
