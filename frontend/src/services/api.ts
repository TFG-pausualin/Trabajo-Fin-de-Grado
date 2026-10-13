const API_BASE_URL = (
  import.meta.env.DEV
    ? "http://127.0.0.1:8000/api"
    : "/api"
).replace(/\/+$/, "");


function obtenerCookie(nombre: string): string | null {
  const prefijo = `${nombre}=`;

  const cookie = document.cookie
    .split(";")
    .map((elemento) => elemento.trim())
    .find((elemento) => elemento.startsWith(prefijo));

  if (!cookie) {
    return null;
  }

  return decodeURIComponent(
    cookie.substring(prefijo.length),
  );
}


export async function solicitarApi<T>(
  ruta: string,
  opciones: RequestInit = {},
): Promise<T> {
  const headers = new Headers(opciones.headers);

  headers.set("Accept", "application/json");

  if (
    opciones.body
    && !headers.has("Content-Type")
  ) {
    headers.set(
      "Content-Type",
      "application/json",
    );
  }

  const metodo = (
    opciones.method ?? "GET"
  ).toUpperCase();

  const metodosConCsrf = [
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
  ];

  if (metodosConCsrf.includes(metodo)) {
    const tokenCsrf = obtenerCookie(
      "csrftoken",
    );

    if (tokenCsrf) {
      headers.set(
        "X-CSRFToken",
        tokenCsrf,
      );
    }
  }

  const respuesta = await fetch(
    `${API_BASE_URL}/${ruta.replace(/^\/+/, "")}`,
    {
      ...opciones,
      headers,
      credentials: "same-origin",
    },
  );

  if (!respuesta.ok) {
    const cuerpo: unknown = await respuesta
      .json()
      .catch(() => null);

    const detalle = obtenerMensajeError(cuerpo);

    throw new Error(
      detalle
      ?? `Error al conectar con el backend (${respuesta.status}).`,
    );
  }

  if (respuesta.status === 204) {
    return undefined as T;
  }

  return respuesta.json() as Promise<T>;
}


function obtenerMensajeError(
  cuerpo: unknown,
): string | null {
  if (typeof cuerpo === "string") {
    return cuerpo;
  }

  if (Array.isArray(cuerpo)) {
    return cuerpo
      .map(obtenerMensajeError)
      .filter(
        (mensaje): mensaje is string =>
          Boolean(mensaje),
      )
      .join(" ");
  }

  if (
    !cuerpo
    || typeof cuerpo !== "object"
  ) {
    return null;
  }

  const campos = cuerpo as Record<
    string,
    unknown
  >;

  if (typeof campos.detail === "string") {
    return campos.detail;
  }

  return (
    Object.entries(campos)
      .flatMap(([campo, valor]) => {
        const mensaje = obtenerMensajeError(
          valor,
        );

        return mensaje
          ? [`${campo}: ${mensaje}`]
          : [];
      })
      .join(" ")
    || null
  );
}