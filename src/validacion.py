"""Carga de pozos, evaluación y líneas base para ROGII: Wellbore Geology Prediction."""

import numpy as np
import pandas as pd
from pathlib import Path


def cargar_pozos(carpeta):
    """Lee todos los pozos horizontales de una carpeta.

    Busca los archivos ``*__horizontal_well.csv`` (ignora los ``typewell`` y
    los ``.png``), los ordena para que el orden sea siempre el mismo y los
    resultados sean reproducibles, y toma el nombre del pozo de la parte del
    nombre del archivo anterior a ``"__"`` (por ejemplo, ``015fe0d2``).

    Los pozos se guardan por separado, y no en una sola tabla, porque todo el
    problema se trabaja pozo por pozo.

    Parámetros
    ----------
    carpeta : str o Path
        Carpeta con los archivos de los pozos (por ejemplo, ``train/``).

    Regresa
    -------
    dict[str, pd.DataFrame]
        Un DataFrame por pozo, con el nombre del pozo como llave.
    """
    pozos = {}
    for f in sorted(Path(carpeta).glob("*__horizontal_well.csv")):
        nombre = f.name.split("__")[0]
        pozos[nombre] = pd.read_csv(f)
    return pozos


def zona_eval(df):
    """Marca los renglones de la zona de evaluación de un pozo.

    La zona de evaluación son los renglones donde ``TVT_input`` es ``NaN``,
    es decir, los que hay que predecir. Se usa en todas las demás funciones
    para no repetir la condición y dejar claro qué significa.

    Parámetros
    ----------
    df : pd.DataFrame
        Un pozo horizontal, con la columna ``TVT_input``.

    Regresa
    -------
    pd.Series de bool
        ``True`` en los renglones a predecir y ``False`` en los conocidos.
    """
    return df["TVT_input"].isna()


def rmse_global(pozos, predecir):
    """Evalúa una función de predicción en la zona de evaluación de cada pozo.

    Para cada pozo, compara el ``TVT`` real con las predicciones solo en los
    renglones de la zona de evaluación y guarda los errores. Después junta
    los errores de todos los pozos y calcula un solo RMSE, igual que Kaggle,
    de modo que los pozos con zonas de evaluación largas pesan más. También
    calcula el RMSE de cada pozo, para ver cuáles fallan más.

    Como ``predecir`` es un argumento, la misma función sirve para evaluar
    cualquier modelo, por ejemplo ``rmse_global(pozos, b0_persistencia)``.

    Parámetros
    ----------
    pozos : dict[str, pd.DataFrame]
        Pozos con la columna ``TVT`` (los de entrenamiento), como los regresa
        ``cargar_pozos``.
    predecir : callable
        Función que recibe el DataFrame de un pozo y regresa un arreglo con
        una predicción por cada renglón de la zona de evaluación, en orden.

    Regresa
    -------
    float
        RMSE global, con los errores de todos los pozos juntos.
    pd.Series
        RMSE de cada pozo, con el nombre del pozo como índice.
    """
    errores, por_pozo = [], {}
    for nombre, df in pozos.items():
        m = zona_eval(df)
        e = df.loc[m, "TVT"].to_numpy() - predecir(df)
        errores.append(e)
        por_pozo[nombre] = np.sqrt(np.mean(e**2))
    return np.sqrt(np.mean(np.concatenate(errores)**2)), pd.Series(por_pozo)


def b0_persistencia(df):
    """Línea base de persistencia: repite el último TVT conocido.

    Supone que el pozo se mantiene en la misma posición geológica después del
    punto de inicio de la predicción (PS). Toma el último ``TVT_input``
    conocido y lo repite en todos los renglones de la zona de evaluación.

    Parámetros
    ----------
    df : pd.DataFrame
        Un pozo horizontal, con la columna ``TVT_input``.

    Regresa
    -------
    np.ndarray
        Una predicción por cada renglón de la zona de evaluación.
    """
    conocido = df[~zona_eval(df)]
    return np.full(zona_eval(df).sum(), conocido["TVT_input"].iloc[-1])


def b1_capas_planas(df):
    """Línea base de capas planas: ajusta el TVT según cuánto sube o baja el pozo.

    Supone que las capas son horizontales, así que todo cambio de TVT viene
    del cambio en ``Z``: si el pozo sube 3 pies desde el PS, el TVT baja
    3 pies. Usa el último renglón conocido (el PS) como referencia.

    Supone que ``TVT + Z`` es constante con capas planas. Hay que verificar
    el signo con los datos: la correlación entre ``diff(TVT)`` y ``diff(Z)``
    en la zona conocida debería ser cercana a -1.

    Parámetros
    ----------
    df : pd.DataFrame
        Un pozo horizontal, con las columnas ``TVT_input`` y ``Z``.

    Regresa
    -------
    np.ndarray
        Una predicción por cada renglón de la zona de evaluación.
    """
    m = zona_eval(df); ps = df[~m].iloc[-1]
    return ps["TVT_input"] - (df.loc[m, "Z"].to_numpy() - ps["Z"])


def b2_buzamiento(df, n=200):
    """Línea base de buzamiento lineal: extrapola la inclinación de las capas.

    Supone que las capas están inclinadas con un ángulo constante cerca del
    PS. Calcula ``offset = TVT + Z`` en los últimos ``n`` renglones conocidos
    (sería constante si las capas fueran planas), le ajusta una recta
    ``offset = a·MD + b`` y la extrapola a la zona de evaluación. Después
    despeja el TVT: como ``offset = TVT + Z``, entonces ``TVT = offset - Z``.

    Si la pendiente ``a`` es cero, el resultado es el mismo que el de
    ``b1_capas_planas``; por eso B2 es una generalización de B1. Igual que
    en B1, hay que verificar el signo de ``TVT + Z`` con los datos.

    Parámetros
    ----------
    df : pd.DataFrame
        Un pozo horizontal, con las columnas ``TVT_input``, ``Z`` y ``MD``.
    n : int, opcional
        Número de renglones conocidos antes del PS que se usan para ajustar la
        recta. Con ``n`` chico la pendiente es ruidosa; con ``n`` grande
        refleja geología lejana. Se elige con la validación. Por defecto, 200.

    Regresa
    -------
    np.ndarray
        Una predicción por cada renglón de la zona de evaluación.
    """
    m = zona_eval(df)
    cola = df[~m].tail(n)
    offset = cola["TVT_input"] + cola["Z"]
    a, b = np.polyfit(cola["MD"], offset, 1)
    return a * df.loc[m, "MD"].to_numpy() + b - df.loc[m, "Z"].to_numpy()