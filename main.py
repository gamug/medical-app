import re, sqlite3
from fastapi import FastAPI, Depends

from src.commons.utils import get_ids_equivalence, general_validation
from src.patient.patient_typing import Patient
from src.doctor.doctor_typing import Doctor

sqlite3.connect(':memory:')
conn = sqlite3.connect('medical_bussiness_db')
cursor = conn.cursor()

app = FastAPI(
    title="Medical API",
    description="API for managing medical data",
    version="1.0.0",
    docs_url="/docs",  # Enables Swagger UI at /docs
    redoc_url="/redoc"  # Enables ReDoc at /redoc
)

@app.get("/")
def read_root():
    return {"Medical API": "This is the main page for the medical app. To access the swagger enter to the URL http://127.0.0.1:8000/docs#/"}

@app.get("/add_paciente")
async def add_patient(data: Patient=Depends()):
    """Adicionar paciente"""
    errors = general_validation(cursor, data)
    if len(errors):
        return errors
    #getting the document and genre ids
    genre, document = data.Sexo_biologico._value_, data.Tipo_documento._value_
    genre = get_ids_equivalence(cursor, genre, 'SEXO_BIOLOGICO', 'SIMBOLO')
    document = get_ids_equivalence(cursor, document, 'TIPO_DOCUMENTO', 'NOMBRE_DOCUMENTO')
    #inserting values
    conn.execute(
        f'''INSERT INTO PACIENTE (ID_PACIENTE, NOMBRE, TELEFONO, CORREO, ID_SEXO_BIOLOGICO, ID_TIPO_DOCUMENTO)
        VALUES ({data.Documento}, '{data.Nombre}', {data.Telefono}, '{data.Correo}', {genre}, {document})
        '''
    )
    conn.commit()
    return data

@app.get("/add_medico")
async def add_doctor(data: Doctor=Depends()):
    """Adicionar medico"""
    errors = general_validation(cursor, data)
    if len(errors):
        return errors
    #getting the document and genre ids
    genre, document, speciality = data.Sexo_biologico._value_, data.Tipo_documento._value_, data.Especialidad._value_
    genre = get_ids_equivalence(cursor, genre, 'SEXO_BIOLOGICO', 'SIMBOLO')
    document = get_ids_equivalence(cursor, document, 'TIPO_DOCUMENTO', 'NOMBRE_DOCUMENTO')
    speciality = get_ids_equivalence(cursor, speciality, 'ESPECIALIDAD', 'NOMBRE_ESPECIALIDAD')
    #inserting values
    conn.execute(
        f'''INSERT INTO MEDICO (ID_MEDICO, ID_ESPECIALIDAD, NOMBRE, TELEFONO, CORREO, ID_SEXO_BIOLOGICO, ID_TIPO_DOCUMENTO)
        VALUES ({data.Documento}, {speciality}, '{data.Nombre}', {data.Telefono}, '{data.Correo}', {genre}, {document})
        '''
    )
    conn.commit()
    return data