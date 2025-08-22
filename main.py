import datetime, sqlite3
import pandas as pd
from fastapi import FastAPI, Depends

# from src.commons.utils import check_directories, get_ids_equivalence, generate_html_visual, general_validation, validate_booking, book_appointment
import src.commons.utils as utils
from src.patient.patient_typing import History, Patient
from src.doctor.doctor_typing import Doctor
from src.agenda.agenda_typing import Agenda, BookAppointment, DeleteAppointment, EditAppointment, PatientAgenda

utils.check_directories()

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

@app.get("/adicionar_paciente")
async def add_patient(data: Patient=Depends()):
    """Adicionar paciente"""
    errors = utils.general_validation(cursor, data)
    if len(errors):
        return errors, 404
    #getting the document and genre ids
    genre, document = data.Sexo_biologico._value_, data.Tipo_documento._value_
    genre = utils.get_ids_equivalence(cursor, genre, 'SEXO_BIOLOGICO', 'SIMBOLO')
    document = utils.get_ids_equivalence(cursor, document, 'TIPO_DOCUMENTO', 'NOMBRE_DOCUMENTO')
    #inserting values
    conn.execute(
        f'''INSERT INTO PACIENTE (ID_PACIENTE, NOMBRE, TELEFONO, CORREO, ID_SEXO_BIOLOGICO, ID_TIPO_DOCUMENTO)
        VALUES ({data.Documento}, '{data.Nombre}', {data.Telefono}, '{data.Correo}', {genre}, {document})
        '''
    )
    conn.commit()
    return {'message': f'Patient with Document number {data.Documento} created'}, 200

@app.get("/adicionar_medico")
async def add_doctor(data: Doctor=Depends()):
    """Adicionar medico"""
    errors = utils.general_validation(cursor, data)
    if len(errors):
        return errors, 404
    #getting the document and genre ids
    genre, document, speciality = data.Sexo_biologico._value_, data.Tipo_documento._value_, data.Especialidad._value_
    genre = utils.get_ids_equivalence(cursor, genre, 'SEXO_BIOLOGICO', 'SIMBOLO')
    document = utils.get_ids_equivalence(cursor, document, 'TIPO_DOCUMENTO', 'NOMBRE_DOCUMENTO')
    speciality = utils.get_ids_equivalence(cursor, speciality, 'ESPECIALIDAD', 'NOMBRE_ESPECIALIDAD')
    #inserting values
    conn.execute(
        f'''INSERT INTO MEDICO (ID_MEDICO, ID_ESPECIALIDAD, NOMBRE, TELEFONO, CORREO, ID_SEXO_BIOLOGICO, ID_TIPO_DOCUMENTO)
        VALUES ({data.Documento}, {speciality}, '{data.Nombre}', {data.Telefono}, '{data.Correo}', {genre}, {document})
        '''
    )
    conn.commit()
    return {'message': f'Doctor with Document number {data.Documento} created'}, 200

@app.get("/consultar_historia_paciente")
async def get_patient_history(data: History=Depends()):
    query = f"""SELECT SINTOMATOLOGIA, DIAGNOSTICO, MEDICACION, COMENTARIOS FROM HISTORIA WHERE ID_CITA IN (
    SELECT ID_CITA FROM AGENDA WHERE ID_PACIENTE={data.Documento}
        )"""
    df = pd.read_sql_query(query, conn)
    if df.empty:
        return {'message': 'No records found for patient'}, 404
    utils.generate_html_visual(df, 'generic.txt', str(data.Documento), 'history')
    return {'message': 'Query completed'}, 200

@app.get("/consultar_agenda_disponible")
async def get_available_agenda(data: Agenda=Depends()):
    df = utils.manage_agend(conn, cursor, data, available_appointment=True)
    id_ = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
    utils.generate_html_visual(df, 'generic.txt', id_, 'agenda')
    return {'message': 'Query completed'}, 200

@app.get("/consultar_agenda_doctor")
async def get_doctor_agenda(data: Agenda=Depends()):
    df = utils.manage_agend(conn, cursor, data, available_appointment=False)
    id_ = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
    utils.generate_html_visual(df, 'generic.txt', id_, 'agenda')
    return {'message': 'Query completed'}, 200

@app.get("/agendar_cita")
async def book_appointment(data: BookAppointment=Depends()):
    id_patient = data.Documento_paciente
    id_swift = data.Id_turno
    errors = utils.validate_booking(cursor, id_patient, id_swift)
    if len(errors):
        return errors, 404
    utils.book_appointment(conn, id_patient, id_swift)
    return {'message': 'Query completed'}, 200

@app.get("/eliminar_cita")
async def delete_appointment(data: DeleteAppointment=Depends()):
    id_swift = data.Id_turno
    utils.delete_appointment(conn, id_swift)
    return {'message': 'Query completed'}, 200

@app.get("/editar_cita")
async def edit_appointment(data: EditAppointment=Depends()):
    old_id_swift = data.Id_turno_viejo
    new_id_swift = data.Id_turno_nuevo
    id_patient = f'SELECT ID_PACIENTE FROM AGENDA WHERE ID_TURNO={old_id_swift};'
    cursor.execute(id_patient)
    id_patient = cursor.fetchall()[0][0]
    old_date = f'SELECT HORA_INICIO FROM TURNO WHERE ID_TURNO={old_id_swift};'
    cursor.execute(old_date)
    old_date = cursor.fetchall()[0][0]
    new_date = f'SELECT HORA_INICIO FROM TURNO WHERE ID_TURNO={new_id_swift};'
    cursor.execute(new_date)
    new_date = cursor.fetchall()[0][0]
    utils.delete_appointment(conn, old_id_swift)
    errors = utils.validate_booking(cursor, id_patient, new_id_swift)
    if len(errors):
        utils.book_appointment(conn, id_patient, old_id_swift)
        return errors, 404
    utils.book_appointment(conn, id_patient, new_id_swift)
    return {'message': f'The appointment for the patient {id_patient} was changed from {old_date} to {new_date}'}, 200

@app.get("/consultar_agenda_paciente")
async def get_patient_agenda(data: PatientAgenda=Depends()):
    query = f'''SELECT PAT_AGEND_TURN_MED_ESP_SEX_CONS.ID_TURNO, PAT_AGEND_TURN_MED_ESP_SEX_CONS.NOMBRE_PACIENTE,
    PAT_AGEND_TURN_MED_ESP_SEX_CONS.DOCUMENTO, PAT_AGEND_TURN_MED_ESP_SEX_CONS.CORREO, 
    PAT_AGEND_TURN_MED_ESP_SEX_CONS.TELEFONO, PAT_AGEND_TURN_MED_ESP_SEX_CONS.FECHA_CITA,
    PAT_AGEND_TURN_MED_ESP_SEX_CONS.NOMBRE_MEDICO, PAT_AGEND_TURN_MED_ESP_SEX_CONS.NOMBRE_ESPECIALIDAD AS ESPECIALIDAD,
    PAT_AGEND_TURN_MED_ESP_SEX_CONS.TELEFONO_MEDICO, PAT_AGEND_TURN_MED_ESP_SEX_CONS.CORREO_MEDICO,
    PAT_AGEND_TURN_MED_ESP_SEX_CONS.SIMBOLO AS SEXO_MEDICO, HOSP.NOMBRE_HOSPITAL, HOSP.DIRECCION_HOSPITAL,
    HOSP.TELEFONO_HOSPITAL, HOSP.CORREO_HOSPITAL FROM
    (SELECT * FROM 
    (SELECT * FROM 
    (SELECT * FROM (SELECT PAT_AGEND_TURN.ID_TURNO, PAT_AGEND_TURN.NOMBRE_PACIENTE, PAT_AGEND_TURN.DOCUMENTO, PAT_AGEND_TURN.CORREO, PAT_AGEND_TURN.TELEFONO,
    PAT_AGEND_TURN.ID_CONSULTORIO, PAT_AGEND_TURN.FECHA_CITA, MED.NOMBRE AS NOMBRE_MEDICO, MED.ID_ESPECIALIDAD, MED.TELEFONO AS TELEFONO_MEDICO,
    MED.CORREO AS CORREO_MEDICO, MED.ID_SEXO_BIOLOGICO FROM
    (SELECT PAT_AGEND.ID_TURNO, PAT_AGEND.NOMBRE AS NOMBRE_PACIENTE, PAT_AGEND.ID_PACIENTE AS DOCUMENTO, PAT_AGEND.CORREO, PAT_AGEND.TELEFONO, TURN.ID_MEDICO,
    TURN.ID_CONSULTORIO, TURN.HORA_INICIO AS FECHA_CITA FROM (SELECT * FROM 
    (SELECT * FROM AGENDA WHERE ID_PACIENTE={data.Documento_paciente}) AGEND
    INNER JOIN
    (SELECT * FROM PACIENTE) PATIENT
    ON AGEND.ID_PACIENTE=PATIENT.ID_PACIENTE) PAT_AGEND
    INNER JOIN
    (SELECT * FROM TURNO) TURN
    ON PAT_AGEND.ID_TURNO=TURN.ID_TURNO) PAT_AGEND_TURN
    INNER JOIN
    (SELECT * FROM MEDICO) MED
    ON MED.ID_MEDICO=PAT_AGEND_TURN.ID_MEDICO) PAT_AGEND_TURN_MED
    INNER JOIN
    (SELECT * FROM ESPECIALIDAD) ESP
    ON ESP.ID_ESPECIALIDAD=PAT_AGEND_TURN_MED.ID_ESPECIALIDAD) PAT_AGEND_TURN_MED_ESP
    INNER JOIN
    (SELECT * FROM SEXO_BIOLOGICO) SEX
    ON SEX.ID_SEXO_BIOLOGICO=PAT_AGEND_TURN_MED_ESP.ID_SEXO_BIOLOGICO) PAT_AGEND_TURN_MED_ESP_SEX
    INNER JOIN
    (SELECT ID_CONSULTORIO, ID_HOSPITAL FROM CONSULTORIO) CONS
    ON CONS.ID_CONSULTORIO=PAT_AGEND_TURN_MED_ESP_SEX.ID_CONSULTORIO) PAT_AGEND_TURN_MED_ESP_SEX_CONS
    INNER JOIN
    (SELECT ID_HOSPITAL, NOMBRE AS NOMBRE_HOSPITAL, DIRECCION AS DIRECCION_HOSPITAL, CORREO AS CORREO_HOSPITAL,
    TELEFONO AS TELEFONO_HOSPITAL FROM HOSPITAL) HOSP
    ON HOSP.ID_HOSPITAL=PAT_AGEND_TURN_MED_ESP_SEX_CONS.ID_HOSPITAL;'''
    errors = utils.validate_agenda(cursor, data)
    if len(errors):
        return errors, 404
    df = pd.read_sql_query(query, conn)
    utils.generate_html_visual(df, 'generic.txt', data.Documento_paciente, 'patient_agenda')
    return {'message': 'Query completed'}, 200