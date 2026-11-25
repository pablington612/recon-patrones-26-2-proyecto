from pathlib import Path
from dotenv import load_dotenv
import kagglehub


def descargar():
    """Descarga (o reutiliza la caché de) los datos de la competencia y devuelve la ruta raíz."""
    load_dotenv()
    return Path(kagglehub.competition_download('rogii-wellbore-geology-prediction'))


if __name__ == '__main__':
    print('Ruta a los archivos de la competencia:', descargar())
