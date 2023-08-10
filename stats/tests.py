# from datetime import datetime


# #################################################################################################################################

# # Текущее время
# now = datetime.now()

# # Форматирование даты
# formatted_date = now.strftime("%d-%m-%Y")

# # День недели
# day_of_week = now.strftime("%A")

# # Неделя в году
# week_of_year = now.strftime("%U")

# print("Текущая дата: ", formatted_date)
# print("Неделя в году: ", str(week_of_year) + "\n")


# ######################################################################################################################################

# # Дата, которую нужно анализировать
# date_string = "20-08-2023"

# # Преобразование строки в datetime
# date_object = datetime.strptime(date_string, "%d-%m-%Y")

# # Неделя в году
# week_of_year = date_object.strftime("%W")  # Используйте "%W", если хотите, чтобы первый понедельник был первой неделей

# print("Дата: ", date_string)
# print("Неделя в году: ", week_of_year)
from datetime import datetime
import socket
print(sum([4, 5]))


def find_free_ports(port=50000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("localhost", port))
        return True
    except socket.error:
        return False


print(find_free_ports())

print(datetime.now().strftime("%U"))
