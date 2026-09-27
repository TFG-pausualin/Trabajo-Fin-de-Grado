export type Sentimiento = "positivo" | "neutral" | "negativo";

export interface SolicitudPrediccion {
  videojuego_id: string;
  titulo: string;
  texto: string;
  puntuacion: number | null;
  compra_verificada: boolean;
  imagenes: string[];
}

export interface RespuestaPrediccion {
  videojuego_id: string;
  titulo: string;
  texto: string;
  texto_procesado: string;
  sentimiento: Sentimiento;
  puntuacion: number | null;
  compra_verificada: boolean;
  imagenes: string[];
}

const URL_PREDICCIONES =
  "http://127.0.0.1:8000/api/predicciones/";

export async function predecirSentimiento(
  solicitud: SolicitudPrediccion,
): Promise<RespuestaPrediccion> {
  const respuesta = await fetch(URL_PREDICCIONES, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(solicitud),
  });

  if (!respuesta.ok) {
    const datos: unknown = await respuesta.json().catch(() => null);
    const detalle = obtenerDetalleError(datos);
    throw new Error(detalle ?? "No se pudo analizar la reseña");
  }

  return respuesta.json() as Promise<RespuestaPrediccion>;
}

function obtenerDetalleError(datos: unknown): string | null {
  if (!datos || typeof datos !== "object" || !("detail" in datos)) {
    return null;
  }

  const detalle = datos.detail;
  if (typeof detalle === "string") return detalle;

  if (Array.isArray(detalle)) {
    const mensajes = detalle.flatMap((item) => {
      if (!item || typeof item !== "object" || !("msg" in item)) {
        return [];
      }

      return typeof item.msg === "string" ? [item.msg] : [];
    });

    if (mensajes.length > 0) return mensajes.join(" ");
  }

  return null;
}
