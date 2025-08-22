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
    '''Patient data model
    Documento is the ID of the patient
    Tipo_documento is the type of document of the patient
    Nombre is the name of the patient
    Telefono is the phone number of the patient
    Correo is the email of the patient
    Sexo_biologico is the biological genre of the patient
    '''
    Tipo_documento: DocumentTypes.create(documents) = documents[0]
    Documento: int
    Nombre: str
    Telefono: int
    Correo: str
    Sexo_biologico: BiologicalGenre.create(genres) = genres[0]

class History(BaseModel):
    '''Patient history data model
    Documento is the ID of the patient
    '''
    Documento: int = 74125896