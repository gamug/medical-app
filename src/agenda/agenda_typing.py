import re, sqlite3
from pydantic import BaseModel
from src.commons.utils import get_list_values
from src.commons.common_types import BiologicalGenre, Hospitals, Months, Specialities

sqlite3.connect(':memory:')
conn = sqlite3.connect('medical_bussiness_db')
cursor = conn.cursor()

genres = get_list_values(cursor, 'SEXO_BIOLOGICO', 'SIMBOLO')
documents = get_list_values(cursor, 'TIPO_DOCUMENTO', 'NOMBRE_DOCUMENTO')
specialities = get_list_values(cursor, 'ESPECIALIDAD', 'NOMBRE_ESPECIALIDAD')
hospitals = get_list_values(cursor, 'HOSPITAL', 'NOMBRE')
months = get_list_values(cursor, 'MES', 'NOMBRE')
genres.append('--')
documents.append('--')
specialities.append('--')
hospitals.append('--')
months.append('--')

class Agenda(BaseModel):
    Nombre_medico: str = ''
    Mes_cita: Months.create(months) = '--'
    Especialidad_medico: Specialities.create(specialities) = '--'
    Sexo_biologico_medico: BiologicalGenre.create(genres) = '--'
    Hospital_atencion: Hospitals.create(hospitals) = '--'

class BookAppointment(BaseModel):
    Documento_paciente: int = 13431341
    Id_turno: int = 640266

class DeleteAppointment(BaseModel):
    Id_turno: int = 640266

class EditAppointment(BaseModel):
    Id_turno_viejo: int = 640266
    Id_turno_nuevo: int = 640267

class PatientAgenda(BaseModel):
    Documento_paciente: int = 13431341