"""
utils_censo.py
==============
Funciones para el tratamiento de valores censurados en tablas del Censo 2020 (INEGI).

Códigos especiales INEGI
------------------------
  -6  →  No aplica           (la unidad geográfica no tiene esa categoría; equivale a 0)
  -8  →  No especificado /   (valor suprimido por confidencialidad estadística;
          confidencial         el INEGI oculta recuentos ≤ 5 personas/viviendas)

Funciones disponibles
---------------------
  diagnostico_censurados  →  Resumen de -6 y -8 por columna
  tratar_no_aplica        →  Reemplaza -6 con un valor (por defecto 0)
  tratar_confidencial     →  Reemplaza -8 según el método elegido
  tratar_censurados       →  Aplica ambos tratamientos en un solo paso
  marcar_censurados       →  Agrega columnas booleanas de bandera antes de limpiar
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# 1. Diagnóstico
# ---------------------------------------------------------------------------

def diagnostico_censurados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve un resumen con el conteo y porcentaje de valores -6 y -8
    por cada columna numérica del DataFrame.

    Parámetros
    ----------
    df : pd.DataFrame (o GeoDataFrame)

    Retorna
    -------
    pd.DataFrame con columnas:
        n_menos_6, pct_menos_6, n_menos_8, pct_menos_8,
        n_especiales, pct_especiales
    """
    cols_num = df.select_dtypes(include="number").columns
    n = len(df)

    resumen = pd.DataFrame({
        "n_menos_6":   (df[cols_num] == -6).sum(),
        "pct_menos_6": ((df[cols_num] == -6).sum() / n * 100).round(1),
        "n_menos_8":   (df[cols_num] == -8).sum(),
        "pct_menos_8": ((df[cols_num] == -8).sum() / n * 100).round(1),
    }).assign(
        n_especiales  = lambda x: x["n_menos_6"] + x["n_menos_8"],
        pct_especiales= lambda x: (x["n_especiales"] / n * 100).round(1),
    )

    return resumen[resumen["n_especiales"] > 0]


# ---------------------------------------------------------------------------
# 2. Tratamiento de -6 (No aplica)
# ---------------------------------------------------------------------------

def tratar_no_aplica(
    df: pd.DataFrame,
    cols: list = None,
    reemplazo: float = 0.0,
) -> pd.DataFrame:
    """
    Reemplaza los valores -6 ("No aplica") por ``reemplazo`` (por defecto 0).

    En datos de conteo censal, -6 indica que la categoría no existe para esa
    unidad geográfica, por lo que equivale conceptualmente a cero.

    Parámetros
    ----------
    df        : DataFrame de entrada (no se modifica el original).
    cols      : Lista de columnas a procesar. Si None, se usan todas las numéricas.
    reemplazo : Valor con el que sustituir -6. Por defecto 0.

    Retorna
    -------
    pd.DataFrame con los valores -6 reemplazados.
    """
    resultado = df.copy()
    cols_num = resultado.select_dtypes(include="number").columns
    cols_proc = cols if cols is not None else cols_num

    # Sólo actuar sobre columnas que realmente contienen -6
    cols_con_6 = [c for c in cols_proc if (resultado[c] == -6).any()]

    for c in cols_con_6:
        resultado[c] = resultado[c].replace(-6, reemplazo)

    n_celdas = sum((df[c] == -6).sum() for c in cols_con_6)
    print(f"[tratar_no_aplica] {len(cols_con_6)} columnas afectadas | "
          f"{n_celdas:,} celdas reemplazadas (-6 → {reemplazo})")

    return resultado


# ---------------------------------------------------------------------------
# 3. Tratamiento de -8 (Confidencial)
# ---------------------------------------------------------------------------

METODOS_CONF = ("nan", "cero", "mediana", "media", "valor_bajo")


def tratar_confidencial(
    df: pd.DataFrame,
    cols: list = None,
    metodo: str = "nan",
    valor_bajo: float = 3.0,
) -> pd.DataFrame:
    """
    Reemplaza los valores -8 ("No especificado / confidencial") según el método
    elegido.

    El INEGI suprime recuentos muy pequeños (≤ 5 personas o viviendas) para
    proteger la identidad de los informantes. La estrategia adecuada depende
    del análisis posterior.

    Parámetros
    ----------
    df         : DataFrame de entrada (no se modifica el original).
    cols       : Lista de columnas a procesar. Si None, se usan todas las numéricas.
    metodo     : Estrategia de imputación. Opciones:

        'nan'        → Convierte -8 en NaN (recomendado; marca la ausencia de dato).
        'cero'       → Sustituye por 0 (límite inferior conservador; subestima).
        'mediana'    → Imputa con la mediana de la columna (excluyendo censurados).
        'media'      → Imputa con la media de la columna (excluyendo censurados).
        'valor_bajo' → Sustituye por ``valor_bajo`` (por defecto 3). Útil cuando
                       se sabe que el valor es positivo pero pequeño (INEGI
                       censura recuentos ≤ 5, así que 3 es un estimado central).

    valor_bajo : Valor numérico usado cuando metodo='valor_bajo'. Por defecto 3.

    Retorna
    -------
    pd.DataFrame con los valores -8 tratados.
    """
    if metodo not in METODOS_CONF:
        raise ValueError(f"metodo='{metodo}' no válido. Opciones: {METODOS_CONF}")

    resultado = df.copy()
    cols_num = resultado.select_dtypes(include="number").columns
    cols_proc = cols if cols is not None else cols_num

    cols_con_8 = [c for c in cols_proc if (resultado[c] == -8).any()]

    for c in cols_con_8:
        mascara = resultado[c] == -8

        if metodo == "nan":
            resultado.loc[mascara, c] = np.nan

        elif metodo == "cero":
            resultado.loc[mascara, c] = 0.0

        elif metodo == "mediana":
            valores_validos = resultado.loc[~mascara & (resultado[c] >= 0), c]
            imputacion = valores_validos.median() if len(valores_validos) > 0 else 0.0
            resultado.loc[mascara, c] = imputacion

        elif metodo == "media":
            valores_validos = resultado.loc[~mascara & (resultado[c] >= 0), c]
            imputacion = valores_validos.mean() if len(valores_validos) > 0 else 0.0
            resultado.loc[mascara, c] = round(imputacion, 1)

        elif metodo == "valor_bajo":
            resultado.loc[mascara, c] = float(valor_bajo)

    n_celdas = sum((df[c] == -8).sum() for c in cols_con_8)
    print(f"[tratar_confidencial] {len(cols_con_8)} columnas afectadas | "
          f"{n_celdas:,} celdas tratadas (método='{metodo}')")

    return resultado


# ---------------------------------------------------------------------------
# 4. Tratamiento combinado
# ---------------------------------------------------------------------------

def tratar_censurados(
    df: pd.DataFrame,
    cols: list = None,
    metodo_conf: str = "nan",
    valor_bajo: float = 3.0,
    reemplazo_no_aplica: float = 0.0,
) -> pd.DataFrame:
    """
    Aplica en un solo paso el tratamiento de -6 y -8.

    Parámetros
    ----------
    df                  : DataFrame de entrada.
    cols                : Columnas a procesar (None = todas las numéricas).
    metodo_conf         : Método para -8. Ver ``tratar_confidencial``.
    valor_bajo          : Valor usado cuando metodo_conf='valor_bajo'.
    reemplazo_no_aplica : Valor con el que sustituir -6 (por defecto 0).

    Retorna
    -------
    pd.DataFrame con ambos tipos de censurado tratados.
    """
    print("── Tratamiento de datos censurados ──────────────────────────────")
    resultado = tratar_no_aplica(df, cols=cols, reemplazo=reemplazo_no_aplica)
    resultado = tratar_confidencial(
        resultado, cols=cols, metodo=metodo_conf, valor_bajo=valor_bajo
    )
    print("─────────────────────────────────────────────────────────────────")
    return resultado


# ---------------------------------------------------------------------------
# 5. Marcado de censurados (flags antes de limpiar)
# ---------------------------------------------------------------------------

def marcar_censurados(
    df: pd.DataFrame,
    cols: list = None,
    sufijo_6: str = "_flag_na",
    sufijo_8: str = "_flag_conf",
) -> pd.DataFrame:
    """
    Agrega columnas booleanas que indican qué filas tenían -6 o -8 en cada
    columna numérica, antes de aplicar el tratamiento.

    Útil para análisis de sensibilidad o para excluir filas censuradas en
    análisis específicos.

    Parámetros
    ----------
    df        : DataFrame de entrada (no se modifica el original).
    cols      : Columnas a revisar. Si None, se usan todas las numéricas.
    sufijo_6  : Sufijo para las columnas flag de -6. Por defecto '_flag_na'.
    sufijo_8  : Sufijo para las columnas flag de -8. Por defecto '_flag_conf'.

    Retorna
    -------
    pd.DataFrame con las columnas flag añadidas al final.
    """
    resultado = df.copy()
    cols_num = resultado.select_dtypes(include="number").columns
    cols_proc = cols if cols is not None else cols_num

    n_flags = 0
    for c in cols_proc:
        tiene_6 = (resultado[c] == -6).any()
        tiene_8 = (resultado[c] == -8).any()

        if tiene_6:
            resultado[f"{c}{sufijo_6}"] = resultado[c] == -6
            n_flags += 1
        if tiene_8:
            resultado[f"{c}{sufijo_8}"] = resultado[c] == -8
            n_flags += 1

    print(f"[marcar_censurados] {n_flags} columnas flag agregadas")
    return resultado
