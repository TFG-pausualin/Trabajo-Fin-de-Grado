import { solicitarApi } from "./api";

export interface DistribucionSentimientos {
  positivas: number;
  neutrales: number;
  negativas: number;
  porcentaje_positivas: number;
  porcentaje_neutrales: number;
  porcentaje_negativas: number;
}

export interface MetricasGlobales {
  total_videojuegos: number;
  total_resenas: number;
  puntuacion_media_global: number | null;
  percepcion_global: "positivo" | "neutral" | "negativo";
  distribucion: DistribucionSentimientos;
}

export interface MetricasVideojuego {
  videojuego_id: string;
  titulo: string;
  puntuacion_media: number | null;
  numero_valoraciones: number;
  percepcion_global: "positivo" | "neutral" | "negativo";
  distribucion: DistribucionSentimientos;
}

export interface PrediccionReciente {
  id: number;
  videojuego_id: string;
  videojuego_titulo: string;
  title: string;
  text: string;
  rating: number | null;
  sentiment: "positivo" | "neutral" | "negativo";
  verified_purchase: boolean;
  created_at: string;
}

export interface ListaPrediccionesRecientes {
  total: number;
  resultados: PrediccionReciente[];
}

export function obtenerMetricasGlobales(): Promise<MetricasGlobales> {
  return solicitarApi<MetricasGlobales>("metricas/");
}

export function obtenerMetricasVideojuego(
  videojuegoId: string,
): Promise<MetricasVideojuego> {
  return solicitarApi<MetricasVideojuego>(
    `metricas/videojuegos/${encodeURIComponent(videojuegoId)}/`,
  );
}

export function obtenerPrediccionesRecientes(
  limite = 8,
): Promise<ListaPrediccionesRecientes> {
  return solicitarApi<ListaPrediccionesRecientes>(
    `metricas/predicciones-recientes/?limite=${limite}`,
  );
}