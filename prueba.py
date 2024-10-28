from utils import *
from bot import *

fetch_ticket = get_ticket_mesa()
fetch_ticket_napear = get_ticket_napear()
fetch_cancel_napear = get_cancel_napear()

lista_mesa = fetch_ticket.split(', ')
lista_nape = fetch_ticket_napear.split(', ')
lista_cancel = fetch_cancel_napear.split(', ')

#LOGICA DE TICKET EN MESA CONTRA NAPEAR

lista_mesa_sin_reserva = []
for element in lista_mesa:
    if element not in lista_nape:
        lista_mesa_sin_reserva.append(element)

lista_reserva_cancelada = []
for element in lista_mesa:
    if element in lista_cancel:
        lista_reserva_cancelada.append(element)
        
# MINI BASE DE DATOS DE TICKETS  
if str(lista_mesa_sin_reserva) !='[]' or str(lista_reserva_cancelada)!='[]':
    comb_list = list(set(lista_mesa_sin_reserva + lista_reserva_cancelada))
else:
    comb_list = []
    
insert_canceladas = insert_db_canceladas(lista_reserva_cancelada)
insert_inexistente = insert_db_inexistente(lista_mesa_sin_reserva)

# ELIMINAR TICKET CERRADOS EN MESA

if str(comb_list)!='[]':
    delete_cerrados = eliminar_registros(comb_list)
#------------------
    
fetch_ticket_db = ticket_sin_notificacion()
fetch_mesa_data_canceladas = get_datos_mesa(fetch_ticket_db)

fetch_ticket_db_inex = ticket_sin_notificacion_inexistentes()
fetch_mesa_data_inex = get_datos_mesa(fetch_ticket_db_inex)

print(fetch_mesa_data_canceladas)
print(fetch_mesa_data_inex)

    