import re, sqlite3
from pydantic import BaseModel
from src.commons.utils import get_list_values
from src.commons.common_types import BiologicalGenre, DocumentTypes

sqlite3.connect(':memory:')
conn = sqlite3.connect('medical_bussiness_db')
cursor = conn.cursor()

genres = get_list_values(cursor, 'SEXO_BIOLOGICO', 'SIMBOLO')
documents = get_list_values(cursor, 'TIPO_DOCUMENTO', 'NOMBRE_DOCUMENTO')


class Patient(BaseModel):
    Tipo_documento: DocumentTypes.create(documents) = documents[0]
    Documento: int
    Nombre: str
    Telefono: int
    Correo: str
    Sexo_biologico: BiologicalGenre.create(genres) = genres[0]

class History(BaseModel):
    Documento: int = 74125896