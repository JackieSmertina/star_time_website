from flask import Flask, render_template, request
import math

app = Flask(__name__)

def calculate_sidereal_time(year, month, day, hour, minute, second):
    # === Переводим местное время Томска (UTC+7) в UT ===
    ut_hour = hour - 7
    ut_day = day
    ut_month = month
    ut_year = year

    if ut_hour < 0:
        ut_hour += 24
        ut_day -= 1

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
    jd = 367 * y - int(7 * (y + int((m + 12) / 12)) / 4) + int(275 * m / 9) + d + 1721013.5

    # === ГРИНВИЧСКОЕ ЗВЁЗДНОЕ ВРЕМЯ ===
    t = (jd - 2451545.0) / 36525.0
    gst_deg = (
        280.46061837 +
        360.98564736629 * (jd - 2451545.0) +
        0.000387933 * t ** 2 -
        t ** 3 / 38710000
    )
    gst_deg %= 360

    # === ЛОКАЛЬНОЕ ЗВЁЗДНОЕ ВРЕМЯ ===
    lst_deg = (gst_deg + 84.95) % 360

    # Переводим LST в чч:мм:сс
    lst_seconds = round((lst_deg / 15.0) * 3600)
    lst_hours = lst_seconds // 3600
    lst_minutes = (lst_seconds % 3600) // 60
    lst_seconds_remain = lst_seconds % 60

    return {
        'julian_day': f"{jd:.6f}",
        'sidereal_time_deg': f"{lst_deg:.2f}",
        'sidereal_time': f"{lst_hours:02d}:{lst_minutes:02d}:{lst_seconds_remain:02d}"
    }

def calculate_hour_angle(lst_deg, ra_h, ra_m, ra_s):
    ra_total_hours = ra_h + ra_m / 60 + ra_s / 3600
    ra_degrees = ra_total_hours * 15
    ha_degrees = (lst_deg - ra_degrees + 360) % 360

    ha_hours = ha_degrees / 15
    ha_h_out = int(ha_hours)
    ha_m_out = int((ha_hours - ha_h_out) * 60)
    ha_s_out = round((((ha_hours - ha_h_out) * 60) % 1) * 60)

    return f"{ha_h_out:02d}:{ha_m_out:02d}:{ha_s_out:02d}"

@app.route("/", methods=["GET", "POST"])
def index():
    data = {
        'date': '2025-05-23',
        'time': '00:46',
        'ra': '',
        'julian_day': '',
        'sidereal_time_deg': '',
        'sidereal_time': '',
        'hour_angle': '',
        'show_ra_form': False,
        'error': ''
    }

    if request.method == "POST":
        try:
            # Получаем дату и время
            date_str = request.form.get("date")
            time_str = request.form.get("time")

            y, m, d = map(int, date_str.split('-'))
            hh, mm = map(int, time_str.split(':'))
            ss = 0

            # Сохраняем значения
            data['date'] = date_str
            data['time'] = time_str

            # Считаем звёздное время
            result = calculate_sidereal_time(y, m, d, hh, mm, ss)
            data.update(result)
            data['show_ra_form'] = True  # Показываем форму с RA

            # Если передали RA, считаем HA
            ra_str = request.form.get("ra", "").strip()
            if ra_str:
                rah, ram, ras = map(float, ra_str.split(':'))
                lst_deg = float(data['sidereal_time_deg'])
                data['hour_angle'] = calculate_hour_angle(lst_deg, rah, ram, ras)
                data['ra'] = ra_str
        except Exception as e:
            data['error'] = "Ошибка ввода данных. Проверьте формат."

    return render_template("index.html", **data)

if __name__ == "__main__":
    app.run(debug=True)