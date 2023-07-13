# Парсер пользователей Telegram по определенным условиям
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest
import sys
import csv
import traceback
import time
from datetime import datetime
import pandas as pd
import xlsxwriter
import openpyxl as ox

api_id = ID  # Введите ваш API ID
api_hash = 'ХЕШ'  # Введите ваш API хеш
phone = 'PHONE NUMBER'  # Введите ваш номер телефона
client = TelegramClient(phone, api_id, api_hash)
c = -1
data = []  # Список для сохранения данных участников

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    client.sign_in(phone, input('Введите код, полученный в вашем мессенджере Telegram: '))

chats = []
last_date = None
chunk_size = 200
groups = []

# Получение списка диалогов пользователя
result = client(GetDialogsRequest(
    offset_date=last_date,
    offset_id=0,
    offset_peer=InputPeerEmpty(),
    limit=chunk_size,
    hash=0
))
chats.extend(result.chats)

# Отбор только мегагрупп
for chat in chats:
    try:
        if chat.megagroup == True:  # Проверка, является ли группа мегагруппой
            groups.append(chat)
    except:
        continue

print('Выберите группу, из которой хотите получить информацию об участниках:')
i = 0
for g in groups:
    print(str(i) + '- ' + g.title)
    i += 1

g_index = input("Введите номер: ")
target_group = groups[int(g_index)]  # Выбор целевой группы

print('Получение информации об участниках...')
all_participants = []
all_participants = client.get_participants(target_group, aggressive=True)  # Получение всех участников группы

now = datetime.now()
date = now.strftime('%Y-%m-%d %H:%M:%S')
print(date)

# Преобразование строки в объект datetime
dt_to_datetime = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
print(dt_to_datetime)

print('Сохранение в файл...')
with open("members_online.csv", "w", encoding='UTF-8') as f:
    writer = csv.writer(f, delimiter=",", lineterminator="\n")
    writer.writerow(['username', 'user id', 'access hash', 'name', 'group', 'group id', 'last seen'])
    for user in all_participants:
        c = c + 1
        accept = True
        try:
            lastDate = user.status.was_online
            dateUser = lastDate.strftime('%Y-%m-%d %H:%M:%S')
            dt_to_datetime1 = datetime.strptime(dateUser, '%Y-%m-%d %H:%M:%S')
            num_months = dt_to_datetime - dt_to_datetime1
            if (num_months.days > 4 or user.username == "saintanist"):
                accept = False
        except:
            continue

        if (accept):
            if user.username:
                username = user.username
            else:
                username = ""
            if user.first_name:
                first_name = user.first_name
            else:
                first_name = ""
            if user.last_name:
                last_name = user.last_name
            else:
                last_name = ""
            name = (first_name + ' ' + last_name).strip()
            writer.writerow([username, user.id, user.access_hash, name, target_group.title, target_group.id, user.status])
            whisky = {"Username": username, "First_name": first_name, "Last_name": last_name,
                      "Последний онлайн (в днях)": num_months, "User ID": user.id}
            data.append(whisky)

# Создание DataFrame из списка данных
df = pd.DataFrame(data)

# Сохранение данных в файл Excel
df.to_excel('online.xlsx')
writer = pd.ExcelWriter("online.xlsx", engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1')

# Настройка ширины столбцов в файле Excel
workbook = writer.book
worksheet = writer.sheets['Sheet1']
worksheet.set_column(1, 1, 35)
worksheet.set_column(2, 2, 35)
worksheet.set_column(3, 3, 30)
worksheet.set_column(4, 4, 30)
worksheet.set_column(5, 5, 30)
writer.close()

print('Информация об участниках успешно получена и сохранена в файл.')
