import os
import telebot
from dotenv import load_dotenv
load_dotenv()
from bot_utils import *

TOKEN = os.getenv ("TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Utilize la funcion /ticket para ver el estado de reservas")


@bot.message_handler(commands=['ticket'])
def sign_handler(message):
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

    if str(fetch_mesa_data_canceladas) !='[]':
        for row in fetch_mesa_data_canceladas:
            cliente, ticket, fecha, estado, usuario = row
            mensaje = f'❌ *Reserva Napear Cancelada*\n*Cliente:* {cliente}\n*Ticket:* {ticket}\n*Fecha alta:* {fecha}\n*Estado:* {estado}\n*Creado por:* {usuario}'
            bot.send_message(message.chat.id, mensaje, parse_mode="Markdown")
            update_state = update_called_status(ticket)
    elif str(fetch_mesa_data_canceladas) =='[]': 
        mensaje = f'No hay reservas canceladas'
        bot.send_message(message.chat.id, mensaje, parse_mode="Markdown")
        
    if str(fetch_mesa_data_inex) !='[]':
        for row in fetch_mesa_data_inex:
            cliente, ticket, fecha, estado, usuario = row
            fetch_hora = comparar_timestamp(fecha)
            if fetch_hora == 1:
                mensaje = f'*⚠️ Ticket sin Reserva*\n*Cliente:* {cliente}\n*Ticket:* {ticket}\n*Fecha alta:* {fecha}\n*Estado:* {estado}\n*Creado por:* {usuario}'
                bot.send_message(message.chat.id, mensaje, parse_mode="Markdown")
                update_state = update_called_status(ticket)
    elif str(fetch_mesa_data_inex) =='[]':
        mensaje = f'No hay ticket sin reserva'
        bot.send_message(message.chat.id, mensaje, parse_mode="Markdown")  
            
bot.infinity_polling()      
