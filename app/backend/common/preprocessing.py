import re
from functools import lru_cache

import spacy
from spacy.language import Language

from app.backend.config import configuracion


NEGACIONES_CONSERVADAS = {
    "no",
    "not",
    "n't",
    "never",
    "neither",
    "nor",
}


EMOTICONOS_POSITIVOS = {
    ":)",
    ":-)",
    "=)",
    ":d",
    ":-d",
    ";)",
    ";-)",
    "(:",
    ";p",
    ";-p",
    "<3",
}


EMOTICONOS_NEGATIVOS = {
    ":(",
    ":-(",
    "=(",
    ":'(",
    "):",
}


@lru_cache(maxsize=1)
def cargar_spacy() -> Language:
    """
    Carga una única vez el modelo de spaCy utilizado
    durante el preprocesamiento del conjunto de datos.
    """

    try:
        return spacy.load(
            configuracion.spacy_model,
            disable=[
                "parser",
                "ner",
            ],
        )

    except OSError as error:
        raise RuntimeError(
            "No se pudo cargar el modelo de spaCy "
            f"'{configuracion.spacy_model}'. "
            "Comprueba que esté instalado mediante: "
            f"python -m spacy download "
            f"{configuracion.spacy_model}"
        ) from error


def combinar_texto(
    titulo: str | None,
    texto: str | None,
) -> str:
    """
    Combina el título y el cuerpo de una reseña.

    Los valores nulos se sustituyen por cadenas vacías,
    se eliminan los espacios exteriores y ambos campos
    se unen mediante un espacio.
    """

    titulo_limpio = (
        str(titulo).strip()
        if titulo is not None
        else ""
    )

    texto_limpio = (
        str(texto).strip()
        if texto is not None
        else ""
    )

    texto_combinado = (
        f"{titulo_limpio} {texto_limpio}"
    ).strip()

    if not texto_combinado:
        raise ValueError(
            "La reseña debe contener un título o un texto."
        )

    return texto_combinado


def normalizar_texto(texto: str) -> str:
    """
    Aplica la normalización inicial utilizada durante
    la preparación del conjunto de datos.

    Operaciones:
    1. Conversión a minúsculas.
    2. Eliminación de etiquetas HTML.
    3. Sustitución de URL por el marcador 'url'.
    4. Normalización de espacios.
    """

    if not isinstance(texto, str):
        raise TypeError(
            "El texto debe ser una cadena de caracteres."
        )

    texto = texto.strip()

    if not texto:
        raise ValueError(
            "La reseña no puede estar vacía."
        )

    texto = texto.lower()

    # Eliminar etiquetas HTML reales.
    texto = re.sub(
        r"<[^>]+>",
        " ",
        texto,
    )

    # Eliminar también etiquetas que lleguen
    # codificadas mediante entidades HTML.
    texto = re.sub(
        r"&lt;[^&]+?&gt;",
        " ",
        texto,
    )

    texto = re.sub(
        r"https?://\S+|www\.\S+",
        " url ",
        texto,
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    ).strip()

    if not texto:
        raise ValueError(
            "La reseña ha quedado vacía después "
            "de la normalización."
        )

    return texto


def procesar_documento(documento) -> str:
    """
    Lematiza un documento y elimina los espacios,
    la puntuación y las palabras vacías, excepto las
    negaciones.
    """

    lemas: list[str] = []

    for token in documento:
        if token.is_space or token.is_punct:
            continue

        lema = token.lemma_.lower().strip()

        es_negacion = (
            token.text.lower() in NEGACIONES_CONSERVADAS
            or lema in NEGACIONES_CONSERVADAS
        )

        if token.is_stop and not es_negacion:
            continue

        if lema:
            lemas.append(lema)

    return " ".join(lemas)


def tokenizar_lematizar(texto: str) -> str:
    """
    Procesa una reseña mediante el modelo de spaCy
    utilizado durante el entrenamiento.
    """

    nlp = cargar_spacy()
    documento = nlp(texto)

    return procesar_documento(documento)


def convertir_emoticonos(texto: str) -> str:
    """
    Convierte emoticonos positivos y negativos en
    marcadores textuales. Los grupos de tres o más
    estrellas se sustituyen por el marcador 'estrellas'.
    """

    texto_convertido = str(texto)

    for emoticono in EMOTICONOS_POSITIVOS:
        texto_convertido = re.sub(
            re.escape(emoticono),
            " positivo ",
            texto_convertido,
        )

    for emoticono in EMOTICONOS_NEGATIVOS:
        texto_convertido = re.sub(
            re.escape(emoticono),
            " negativo ",
            texto_convertido,
        )

    texto_convertido = re.sub(
        r"\*{3,}",
        " estrellas ",
        texto_convertido,
    )

    texto_convertido = re.sub(
        r"\s+",
        " ",
        texto_convertido,
    ).strip()

    return texto_convertido


def recuperar_texto_vacio(texto: str) -> str:
    """
    Aplica el tratamiento alternativo utilizado cuando
    una reseña queda vacía tras eliminar las palabras
    vacías.

    En esta fase se conservan los lemas aunque sean
    palabras vacías.
    """

    texto_convertido = convertir_emoticonos(texto)

    nlp = cargar_spacy()
    documento = nlp(texto_convertido)

    lemas: list[str] = []

    for token in documento:
        if token.is_space or token.is_punct:
            continue

        lema = token.lemma_.lower().strip()

        if lema:
            lemas.append(lema)

    return " ".join(lemas)


def procesar_resena(
    titulo: str | None,
    texto: str | None,
) -> str:
    """
    Reproduce el procesamiento utilizado para generar
    la columna review_text_processed.

    La salida está preparada para ser transformada
    mediante el vectorizador TF-IDF guardado.
    """

    texto_combinado = combinar_texto(
        titulo=titulo,
        texto=texto,
    )

    texto_normalizado = normalizar_texto(
        texto_combinado
    )

    texto_procesado = tokenizar_lematizar(
        texto_normalizado
    )

    if not texto_procesado.strip():
        texto_procesado = recuperar_texto_vacio(
            texto_normalizado
        )

    texto_procesado = texto_procesado.strip()

    if not texto_procesado:
        raise ValueError(
            "La reseña no contiene información textual "
            "suficiente para realizar una predicción."
        )

    return texto_procesado
