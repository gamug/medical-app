import re, sqlite3
from typing import Any

def get_list_values(cursor: sqlite3.Cursor, table: str, column: str) -> list[str]:
    cursor.execute(f'SELECT {column} FROM {table}')
    genres = [g[0] for g in cursor.fetchall()]
    return genres

def get_ids_equivalence(cursor: sqlite3.Cursor, value: str, table: str, column_filter) -> tuple[int]:
    query = f"SELECT ID_{table} FROM {table} WHERE {column_filter}='{value}'"
    print(query)
    cursor.execute(query)
    value = cursor.fetchall()
    print(value)
    value = value[0][0]
    return value

def general_validation(cursor: sqlite3.Cursor, data: Any) -> dict:
    errors = {}
    #extra validations
    if not re.match('[a-z0-9_]+@[a-z0-9_]+\.com', data.Correo, flags=re.IGNORECASE):
        errors['Email_error'] = f"The Email {data.Correo} has a invalid format. Expected a format something@any.com"
    cursor.execute("SELECT ID_PACIENTE FROM PACIENTE")
    patients = [id_[0] for id_ in cursor.fetchall()]
    if data.Documento in patients:
        errors['Document_error'] = f"The patient with the document {data.Documento} already exists in the database"
    return errors