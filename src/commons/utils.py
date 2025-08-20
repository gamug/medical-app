import os, re, sqlite3, webbrowser
import pandas as pd
from typing import Any

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
        errors['Document_error'] = f"The patient with the document {data.Documento} already exists in the database"
    return errors

def generate_html_visual(df: pd.DataFrame, template: str, id_: str, suffix: str) -> None:
    html_content = df.to_html(index=False)
    with open(os.path.join('inputs', 'html_templates', template), 'r') as f:
        styled_html = f.readlines()
    styled_html = '\n'.join(styled_html).format(id_, len(df), html_content)
    path = os.path.join(os.getcwd(), 'output', suffix, f'{id_}_{suffix}.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(styled_html)
    webbrowser.open(f'file://{path}')