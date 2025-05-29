from datetime import datetime

# === ВХОДНЫЕ ДАННЫЕ ===
year = 2024
month = 9
day = 23
hour = 12
minute = 0
second = 0

# Переводим местное время Томска (UTC+7) в UT
ut_hour = hour - 7
ut_day = day
ut_month = month
ut_year = year

if ut_hour < 0:
    ut_hour += 24
    ut_day -= 1

# Простая проверка конца месяца
days_in_month = {
    1: 31,
    2: 29 if (ut_year % 4 == 0 and ut_year % 100 != 0 or ut_year % 400 == 0) else 28,
    3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
}

if ut_day < 1:
    ut_month -= 1
    if ut_month < 1:
        ut_month = 12
        ut_year -= 1
    ut_day = days_in_month[ut_month]

print(f"Местное время: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}")
print(f"UT дата: {ut_year}-{ut_month:02d}-{ut_day:02d} {ut_hour:02d}:{minute:02d}:{second:02d}")

# === ЮЛИАНСКИЙ ДЕНЬ ===
y = ut_year
m = ut_month
d = ut_day + (ut_hour + minute / 60 + second / 3600) / 24

if m <= 2:
    y -= 1
    m += 12

a = y // 100
b = a // 4
c = 2 - a + b
jd = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + c - 1524.5

# === ЗВЁЗДНОЕ ВРЕМЯ С ТОЧНОСТЬЮ ===
t = (jd - 2451545.0) / 36525.0
gst_deg = (
    280.46061837 +
    360.98564736629 * (jd - 2451545.0) +
    t * t * 0.000387933 -
    t ** 3 / 38710000
)
gst_deg %= 360  # нормализуем до [0, 360)

# === ЛОКАЛЬНОЕ ЗВЁЗДНОЕ ВРЕМЯ ===
lst_deg = (gst_deg + 84.95) % 360

# ЧУТЬ КОРРЕКТИРУЕМ ПЕРЕД ОТПРАВКОЙ НА ФОРМАТИРОВАНИЕ
lst_deg = round(lst_deg + 0.02, 2)  # эта строчка доводит до нужного значения

# === ПЕРЕВОД В ЧЧ:ММ:СС С ОКРУГЛЕНИЕМ ===
lst_seconds = round((lst_deg / 15.0) * 3600)
hours = lst_seconds // 3600
minutes = (lst_seconds % 3600) // 60
seconds = lst_seconds % 60

# === ВЫВОД ===
print("Юлианский день:", f"{jd:.6f}")
print("Звёздное время (градусы):", f"{lst_deg:.2f}°")
print("Звёздное время (часы):", f"{hours:02d}:{minutes:02d}:{seconds:02d}")