import sqlite3
from pydantic import BaseModel
from src.commons.utils import get_list_values
from src.commons.common_types import BiologicalGenre, DocumentTypes, Specialities

sqlite3.connect(':memory:')
conn = sqlite3.connect('medical_bussiness_db')
cursor = conn.cursor()

genres = get_list_values(cursor, 'SEXO_BIOLOGICO', 'SIMBOLO')
documents = get_list_values(cursor, 'TIPO_DOCUMENTO', 'NOMBRE_DOCUMENTO')
specialities = get_list_values(cursor, 'ESPECIALIDAD', 'NOMBRE_ESPECIALIDAD')

class Doctor(BaseModel):
    '''Doctor data model
    Documento is the ID of the doctor
    Tipo_documento is the type of document of the doctor
    Especialidad is the speciality of the doctor
    Nombre is the name of the doctor
    Telefono is the phone number of the doctor
    Correo is the email of the doctor
    Sexo_biologico is the biological genre of the doctor
    '''
    Tipo_documento: DocumentTypes.create(documents) = documents[0]
    Documento: int
    Especialidad: Specialities.create(specialities) = specialities[0]
    Nombre: str
    Telefono: int
    Correo: str
    Sexo_biologico: BiologicalGenre.create(genres) = genres[0]