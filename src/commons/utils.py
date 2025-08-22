import os, re, sqlite3, webbrowser
import pandas as pd
from typing import Any, Optional

def check_directories():
    paths = ['output', os.path.join('output', 'agenda'), os.path.join('output', 'history'), os.path.join('output', 'patient_agenda')]
    for path in paths:
        if not os.path.exists(path):
            os.mkdir(path)

def get_list_values(cursor: sqlite3.Cursor, table: str, column: str) -> list[str]:
    cursor.execute(f'SELECT {column} FROM {table}')
    genres = [g[0] for g in cursor.fetchall()]
    return genres

def get_ids_equivalence(cursor: sqlite3.Cursor, value: str, table: str, column_filter) -> tuple[int]:
    query = f"SELECT ID_{table} FROM {table} WHERE {column_filter}='{value}'"
    cursor.execute(query)
    value = cursor.fetchall()
    value = False if not len(value) else value[0][0]
    return value

def general_validation(cursor: sqlite3.Cursor, data: Any) -> dict:
    errors = {}
    #extra validations
    if not re.match('[a-z0-9_]+@[a-z0-9_]+\.com', data.Correo, flags=re.IGNORECASE):
        errors['Email_error'] = f"The Email {data.Correo} has a invalid format. Expected a format something@any.com"
    cursor.execute("SELECT ID_PACIENTE FROM PACIENTE")
    patients = [id_[0] for id_ in cursor.fetchall()]
    if data.Documento in patients:
        errors['Document_error'] = f"The register with the document {data.Documento} already exists in the database"
    return errors

def validate_booking(cursor: sqlite3.Cursor, id_patient: int, id_swift: int) -> dict:
    errors = {}
    #validating apointment availability
    query = f'SELECT DISPONIBLE FROM TURNO WHERE ID_TURNO={id_swift}'
    cursor.execute(query)
    available = cursor.fetchall()
    if not len(available):
        errors['Appointment_nonexisted'] = f'The swift id {id_swift} isn\'t in the database created as an available appointment'
    elif not available[0][0]:
        query = f'SELECT ID_PACIENTE FROM AGENDA WHERE ID_TURNO={id_swift};'
        cursor.execute(query)
        patient = cursor.fetchall()[0][0]
        errors['Appointment_error'] = f'The swift id {id_swift} is already taken by the patient with ID {patient}'
    #validating patient availability for the booking
    query = f'''SELECT TURN.HORA_INICIO AS FECHA FROM
    (SELECT * FROM AGENDA WHERE ID_PACIENTE={id_patient}) AGEND
    INNER JOIN
    (SELECT * FROM TURNO) TURN
    ON AGEND.ID_TURNO=TURN.ID_TURNO'''
    cursor.execute(query)
    patient_availability = cursor.fetchall()
    query = f'SELECT HORA_INICIO FROM TURNO WHERE ID_TURNO={id_swift}'
    cursor.execute(query)
    appointment_date = cursor.fetchall()
    if len(patient_availability) and not 'Appointment_nonexisted' in errors:
        patient_availability = [value[0] for value in patient_availability]
        appointment_date = appointment_date[0][0]
        if appointment_date in patient_availability:
            errors['Patient_unavailability'] = f'The patient {id_patient} already has booked an appointment in the date {appointment_date}'
    return errors

def validate_agenda(cursor: sqlite3.Cursor, data: Any):
    errors = dict()
    cursor.execute("SELECT ID_PACIENTE FROM PACIENTE")
    patients = [id_[0] for id_ in cursor.fetchall()]
    if not data.Documento_paciente in patients:
        errors['Document_error'] = f'The document {data.Documento_paciente} is not registered as patient in the database'
    return errors

def manage_agend(conn: sqlite3.Connection, cursor: sqlite3.Cursor, data: Any, available_appointment: Optional[bool]=True) -> pd.DataFrame:
    Nombre_medico = data.Nombre_medico
    Mes_cita = get_ids_equivalence(cursor, data.Mes_cita._value_, 'MES', 'NOMBRE')
    Hospital_atencion = get_ids_equivalence(cursor, data.Hospital_atencion._value_, 'HOSPITAL', 'NOMBRE')
    Sexo_biologico_medico = get_ids_equivalence(cursor, data.Sexo_biologico_medico._value_, 'SEXO_BIOLOGICO', 'SIMBOLO')
    Especialidad_medico = get_ids_equivalence(cursor, data.Especialidad_medico._value_, 'ESPECIALIDAD', 'NOMBRE_ESPECIALIDAD')
    available_appointment = 'TRUE' if available_appointment else 'FALSE'
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
    DISPONIBLE={available_appointment}
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
    return df

def generate_html_visual(df: pd.DataFrame, template: str, id_: str, suffix: str) -> None:
    html_content = df.to_html(index=False)
    with open(os.path.join('inputs', 'html_templates', template), 'r') as f:
        styled_html = f.readlines()
    styled_html = '\n'.join(styled_html).format(id_, len(df), html_content)
    path = os.path.join(os.getcwd(), 'output', suffix, f'{id_}_{suffix}.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(styled_html)
    webbrowser.open(f'file://{path}')

def book_appointment(conn: sqlite3.Connection, id_patient: int, id_swift: int) -> None:
    query_cita = f'INSERT INTO AGENDA (ID_PACIENTE, ID_TURNO) VALUES ({id_patient}, {id_swift})'
    conn.execute(query_cita)
    conn.commit()
    query_cita = f'UPDATE TURNO SET DISPONIBLE=FALSE WHERE ID_TURNO={id_swift}'
    conn.execute(query_cita)
    conn.commit()

def delete_appointment(conn: sqlite3.Connection, id_swift: int) -> None:
    query_cita = f'DELETE FROM AGENDA WHERE ID_TURNO={id_swift};'
    conn.execute(query_cita)
    conn.commit()
    query_cita = f'UPDATE TURNO SET DISPONIBLE=TRUE WHERE ID_TURNO={id_swift}'
    conn.execute(query_cita)
    conn.commit()