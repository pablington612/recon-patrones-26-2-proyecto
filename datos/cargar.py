import pandas as pd

def cargar_datos_csv(raiz, carpeta, tipo):
    archivos = sorted((raiz / carpeta).glob(f'*__{tipo}.csv'))
    return pd.concat(
        [pd.read_csv(f).assign(well_id=f.name.split('__')[0]) for f in archivos],
        ignore_index=True,
    )