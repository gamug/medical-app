import datetime, sqlite3
import pandas as pd
from fastapi import FastAPI, Depends

from src.commons.utils import check_directories, get_ids_equivalence, generate_html_visual, general_validation, validate_booking
from src.patient.patient_typing import History, Patient
from src.doctor.doctor_typing import Doctor
from src.agenda.agenda_typing import Agenda, BookAppointment

check_directories()

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
        return errors, 404
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
    return {'message': f'Patient with Document number {data.Documento} created'}, 200

@app.get("/add_medico")
async def add_doctor(data: Doctor=Depends()):
    """Adicionar medico"""
    errors = general_validation(cursor, data)
    if len(errors):
        return errors, 404
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
    return {'message': f'Doctor with Document number {data.Documento} created'}, 200

@app.get("/get_historia_paciente")
async def get_patient_history(data: History=Depends()):
    query = f"""SELECT SINTOMATOLOGIA, DIAGNOSTICO, MEDICACION, COMENTARIOS FROM HISTORIA WHERE ID_CITA IN (
    SELECT ID_CITA FROM AGENDA WHERE ID_PACIENTE={data.Documento}
        )"""
    df = pd.read_sql_query(query, conn)
    if df.empty:
        return {'message': 'No records found for patient'}, 404
    generate_html_visual(df, 'generic.txt', str(data.Documento), 'history')
    return {'message': 'Query completed'}, 200

@app.get("/get_agenda_disponible")
async def get_available_agenda(data: Agenda=Depends()):
    Nombre_medico = data.Nombre_medico
    Mes_cita = get_ids_equivalence(cursor, data.Mes_cita._value_, 'MES', 'NOMBRE')
    Hospital_atencion = get_ids_equivalence(cursor, data.Hospital_atencion._value_, 'HOSPITAL', 'NOMBRE')
    Sexo_biologico_medico = get_ids_equivalence(cursor, data.Sexo_biologico_medico._value_, 'SEXO_BIOLOGICO', 'SIMBOLO')
    Especialidad_medico = get_ids_equivalence(cursor, data.Especialidad_medico._value_, 'ESPECIALIDAD', 'NOMBRE_ESPECIALIDAD')
    queries = {
        'Nombre_medico': f"AND ID_MEDICO IN (SELECT ID_MEDICO FROM MEDICO WHERE LOWER(NOMBRE)) LIKE '%{Nombre_medico.lower()}%'" if len(Nombre_medico) else '',
        'Mes_cita': f"AND CAST(STRFTIME('%m', HORA_INICIO) AS INTEGER)>={Mes_cita}" if Mes_cita else '',
        'Hospital_atencion': f'AND ID_CONSULTORIO IN (SELECT ID_CONSULTORIO FROM CONSULTORIO WHERE ID_HOSPITAL={Hospital_atencion})' if Hospital_atencion else '',
        'Sexo_biologico_medico': f'AND ID_MEDICO IN (SELECT ID_MEDICO FROM MEDICO WHERE ID_SEXO_BIOLOGICO={Sexo_biologico_medico})' if Sexo_biologico_medico else '',
        'Especialidad_medico': f'AND ID_MEDICO IN (SELECT ID_MEDICO FROM MEDICO WHERE ID_ESPECIALIDAD={Especialidad_medico})' if Especialidad_medico else ''
    }
    #Vamos, sí que aprendí con este query :)
    query = f'''SELECT TMED.ID_TURNO, TMED.HORA_INICIO, TMED.NOMBRE, TMED.NOMBRE_ESPECIALIDAD, TMED.ID_CONSULTORIO, HOSP.HOSPITAL
    FROM
    (SELECT T.ID_TURNO, T.ID_CONSULTORIO, T.HORA_INICIO, MED.NOMBRE, MED.NOMBRE_ESPECIALIDAD
    FROM(SELECT * FROM TURNO WHERE
    HORA_INICIO>(SELECT DATETIME('now')) AND
    DISPONIBLE=TRUE
    {queries['Nombre_medico']}
    {queries['Mes_cita']}
    {queries['Hospital_atencion']}
    {queries['Sexo_biologico_medico']}
    {queries['Especialidad_medico']}) T
    INNER JOIN
    (SELECT M.ID_MEDICO, M.NOMBRE, E.NOMBRE_ESPECIALIDAD
    FROM MEDICO M INNER JOIN
    ESPECIALIDAD E
    ON M.ID_ESPECIALIDAD=E.ID_ESPECIALIDAD) MED
    ON T.ID_MEDICO=MED.ID_MEDICO) TMED
    INNER JOIN
    (SELECT C.ID_CONSULTORIO, H.NOMBRE as HOSPITAL
    FROM HOSPITAL H INNER JOIN
    CONSULTORIO C
    ON C.ID_HOSPITAL=H.ID_HOSPITAL) HOSP
    ON TMED.ID_CONSULTORIO=HOSP.ID_CONSULTORIO;'''
    df = pd.read_sql_query(query, conn)
    id_ = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
    generate_html_visual(df, 'generic.txt', id_, 'agenda')
    return {'message': 'Query completed'}, 200

@app.get("/agendar_cita")
async def book_appointment(data: BookAppointment=Depends()):
    id_patient = data.Documento_paciente._value_
    id_swift = data.Id_turno._vale_
    errors = validate_booking(cursor, id_patient, id_swift)
    if len(errors):
        return errors, 404
    query_cita = f'INSERT INTO AGENDA (ID_PACIENTE, ID_TURNO) VALUES ({data.Documento_paciente}, {data.Id_turno})'
    