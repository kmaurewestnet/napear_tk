import os
import requests
import psycopg2
import json
import re
import mysql.connector
import datetime
from dotenv import load_dotenv
load_dotenv()

mesa_db = os.getenv ("MESA_DB")
mesa_user = os.getenv ("MESA_USER")
mesa_host = os.getenv ("MESA_IP")
mesa_pass = os.getenv ("MESA_PASS")

nape_db = os.getenv ("NAPE_DB")
nape_user = os.getenv ("NAPE_USER")
nape_host = os.getenv ("NAPE_IP")
nape_pass = os.getenv ("NAPE_PASS")

connMesa = psycopg2.connect(database=mesa_db, user=mesa_user, password=mesa_pass, host=mesa_host, port= '5432')
connNap = mysql.connector.connect(host=nape_host, user=nape_user, database=nape_db, password=nape_pass)

def get_ticket_mesa():
    cursor = connMesa.cursor()
    with connMesa.cursor() as cur:
            try:
                cur.execute("""SELECT string_agg(t.id::text, ', ' order by t.id) as ticket
                                from ticket t
                                WHERE 
                                t.fecha_alta >= (now() - interval '30 day')    
                                and (t.estado !='cerrado (resuelto)' and t.estado !='cerrado (no resuelto)')
                                and t.categoria_id IN (100,125,154);""")
            except Exception as exc:
                print("Error executing SQL: %s"%exc)
            ticket = cur.fetchall()
            ticket = ticket[0]
            ticket = str(ticket)
            ticket = ticket.replace(',)', '')
            ticket = ticket.replace('(', '')
            ticket = ticket.replace("'", '')
    return (ticket)

def get_ticket_napear():
    
    if connNap and connNap.is_connected():
        with connNap.cursor() as cursor:
            result = cursor.execute("""SELECT GROUP_CONCAT(r.ticket_id SEPARATOR ', ') as ticket
                                        FROM registros r
                                        left join estados_configs ec ON r.estado_id = ec.id
                                        left join registro_reservas rr ON r.id = rr.registro_id
                                        left join users u ON r.user_id_creacion = u.id
                                        where
                                        r.created_at >= (now() - interval 30 day)""")
            rows = cursor.fetchall()
            rows = rows[0]
            ticket = str(rows)
            ticket = ticket.replace(',)', '')
            ticket = ticket.replace('(', '')
            ticket = ticket.replace("'", '')
    return(ticket)
            
def get_cancel_napear():
    
    if connNap and connNap.is_connected():
        with connNap.cursor() as cursor:
            result = cursor.execute("""SELECT GROUP_CONCAT(r.ticket_id SEPARATOR ', ') as ticket
                                        FROM registros r
                                        left join estados_configs ec ON r.estado_id = ec.id
                                        left join registro_reservas rr ON r.id = rr.registro_id
                                        left join users u ON r.user_id_creacion = u.id
                                        inner join (Select ticket_id, max(created_at) as fecha from registros where created_at >= (now() - interval 30 day) GROUP BY ticket_id) s ON r.ticket_id = s.ticket_id and r.created_at = s.fecha
                                        where
                                        r.created_at >= (now() - interval 30 day)
                                        and ec.nombre = 'CANCELADA'""")
            rows = cursor.fetchall()
            rows = rows[0]
            cancel = str(rows)
            cancel = cancel.replace(',)', '')
            cancel = cancel.replace('(', '')
            cancel = cancel.replace("'", '')
    return(cancel)

# EDITAR CONSULTA MESA
def get_datos_mesa(ids):
    
    ids = str(ids)
    if ids != '[]':
        ids = ids.replace('[', '(')
        ids = ids.replace(']', ')')
        ids = ids.replace("'", '')
        cursor = connMesa.cursor()
        with connMesa.cursor() as cur:
                        try:
                            cur.execute("""SELECT t.codigo_cliente, t.id::text as ticket, t.fecha_alta::text, t.estado as estado_ticket, u.nombre as creado_por
                                            from ticket t
                                            left join usuario u ON t.autor_id = u.id
                                            WHERE 
                                            t.id IN """+ids+""";""")
                        except Exception as exc:
                            print("Error executing SQL: %s"%exc)
                        ticket = cur.fetchall()
        return(ticket)
    else:
        ticket = []
        return(ticket)

# INSERTAR DATOS EN MICRO DB DE TICKET CANCELADOS

def insert_db_canceladas(ids):
    
    file_path = 'db.json'

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
    else:
        data = []

    existing_ids = {entry["id"] for entry in data}

    for id_value in ids:
        if id_value not in existing_ids:
            new_entry = {"id": id_value, "type": "Cancelada", "called": "false"}
            data.append(new_entry)

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# INSERTAR DATOS EN MICRO DB DE TICKET SIN RESERVA

        
def insert_db_inexistente(ids):
    
    file_path = 'db.json'

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
    else:
        data = []

    existing_ids = {entry["id"] for entry in data}

    for id_value in ids:
        if id_value not in existing_ids:
            new_entry = {"id": id_value, "type": "INEXISTENTE", "called": "false"}
            data.append(new_entry)

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
        
# ELIMINA DATOS EN MICRO DB DE TICKET CERRADOS EN MESA

def eliminar_registros(comb_list):

    file_path = 'db.json'

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
    else:
        data = []

    data_dict = {entry["id"]: entry for entry in data}

    updated_data = []

    for id_value in comb_list:
        if id_value in data_dict:
            updated_data.append(data_dict[id_value])
        else:
            new_entry = {"id": id_value, "type": "Cancelada", "called": "false"}
            updated_data.append(new_entry)

    with open(file_path, 'w') as file:
        json.dump(updated_data, file, indent=4)
        
def ticket_sin_notificacion():
    file_path = 'db.json'

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
    else:
        data = []

    ids_with_false_called = [entry["id"] for entry in data if entry.get("called") == "false" and entry.get("type") == "Cancelada"]

    return(ids_with_false_called)

def ticket_sin_notificacion_inexistentes():
    file_path = 'db.json'

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
    else:
        data = []

    ids_with_false_called = [entry["id"] for entry in data if entry.get("called") == "false" and entry.get("type") == "INEXISTENTE"]

    return(ids_with_false_called)   

def update_called_status(id_value):
    
    file_path = 'db.json'
    if os.path.exists(file_path):

        with open(file_path, 'r') as file:
            data = json.load(file)
    else:
        print("El archivo no existe.")
        return

    found = False
    for entry in data:
        if entry["id"] == id_value:
            entry["called"] = "true"
            found = True
            break
    
    if found:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    else:
        print(f"El ID {id_value} no se encontró en el archivo.")

