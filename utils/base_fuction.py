from datetime import datetime, date, timedelta
from telegram import InlineKeyboardButton
import jdatetime

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_week_date_range():
    today = date.today()
    weedDay = today.weekday()
    if weedDay == 0:
        start = today - timedelta(days=(2))
    elif weedDay == 1:
        start = today - timedelta(days=(3))
    elif weedDay == 2:
        start = today - timedelta(days=(4))
    elif weedDay == 3:
        start = today - timedelta(days=(5))
    elif weedDay == 4:
        start = today - timedelta(days=(6))
    elif weedDay == 5:
        start = today
    else:
        start = today - timedelta(days=(1))

    end = start + timedelta(days=6)

    return [start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')]


def convert_gregorian_date_to_jalali_str(dateObj):
    # jalali months
    jalaliMonths = {
        1: 'فروردین',
        2: 'اردیبهشت',
        3: 'خرداد',
        4: 'تیر',
        5: 'مرداد',
        6: 'شهریور',
        7: 'مهر',
        8: 'آبان',
        9: 'آذر',
        10: 'دی',
        11: 'بهمن',
        12: 'اسفند'
    }

    jalaliDate = jdatetime.date.fromgregorian(day = dateObj.day, month = dateObj.month, year = dateObj.year)
    jalaliDateStr = str(jalaliDate.day) + ' ' + jalaliMonths[jalaliDate.month] + ' ' + str(jalaliDate.year)
    weekDayStr = jalaliDate.j_weekdays_fa[jalaliDate.weekday()]

    return {'jalali_date_str': jalaliDateStr, 'week_day_str': weekDayStr}


def get_all_week_date():
    # get week date range
    weekDate = get_week_date_range()
    startWeekDate = datetime.strptime(weekDate[0], '%Y-%m-%d')
    # week date list
    startWeekJson = convert_gregorian_date_to_jalali_str(startWeekDate)
    startWeekJson['gregorian_date'] = startWeekDate.strftime('%Y-%m-%d')
    weekDateList = [startWeekJson]
    # add other week days
    for item in range(1, 7):
        dayDate = startWeekDate + timedelta(days=item)
        dayJson = convert_gregorian_date_to_jalali_str(dayDate)
        dayJson['gregorian_date'] = dayDate.strftime('%Y-%m-%d')
        weekDateList.append(dayJson)

    return weekDateList


def convert_seconds_to_time_str(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    timeStr = '{:02}:{:02}'.format(int(hours), int(minutes))
    return timeStr


def convert_status_to_str(value):
    status = {
        'have_capacity': 'دارد',
        'full_capacity': 'تکمیل',
        'canceled': 'لغو شد'
    }
    return status[value]
 

def generate_week_program_str(weekProgram):
    # get week date list
    weekDateList = get_all_week_date()
    
    weekProgramStr = "برنامه هفتگی 🗓\n\n"

    for weekDay in weekDateList:
        weekProgramStr += f"🔹 {weekDay['week_day_str']} ({weekDay['jalali_date_str']}):\n"
        for obj in weekProgram:
            objDate = obj['date'].strftime('%Y-%m-%d')
            if objDate == weekDay['gregorian_date']:
                weekProgramStr += f"{obj['title']}\n"
                objStartTimeStr = convert_seconds_to_time_str(obj['start_time'].seconds)
                weekProgramStr += f"ساعت: {objStartTimeStr}\n"
                weekProgramStr += f"ظرفیت: {convert_status_to_str(obj['status'])}\n"
                weekProgramStr += f"توضیحات: /p_description_{obj['program_id']}\n" 
                weekProgramStr += f"اطلاعات فیلم: /p_info_{obj['program_id']}\n"
                weekProgramStr += f"تیزر فیلم: /p_teaser_{obj['program_id']}\n"
                weekProgramStr += f"مشاهده سالن: /s_view_hall_{obj['id']}\n"

        if weekDay['week_day_str'] != 'جمعه':
            weekProgramStr += f"-------------------------\n"

    return weekProgramStr


def get_hall_buttons(hallJson, screeningID):
    buttons = []

    chairList = []
    for chair in hallJson['list']:
        if chair['status'] == 0:
            chairTitle = str(chair['id']) + ': ' + str(chair['price']) + 'T'
            if chair['type'] == 'vip':
                chairTitle += ' (Vip)'
            chairObj = InlineKeyboardButton(chairTitle, callback_data=f'screening_{screeningID}_chair_{chair["id"]}')
        elif chair['status'] == 1:
            chairTitle = str(chair['id']) + ': 🔄'
            if chair['type'] == 'vip':
                chairTitle += ' (Vip)'
            chairObj = InlineKeyboardButton(chairTitle, callback_data=f'screening_{screeningID}_chair_{chair["id"]}')
        else:
            chairTitle = str(chair['id']) + ': ⛔️'
            if chair['type'] == 'vip':
                chairTitle += ' (Vip)'
            chairObj = InlineKeyboardButton(chairTitle, callback_data=f'screening_{screeningID}_chair_{chair["id"]}')
        chairList.append(chairObj)

        if chair['id'] == 4:
            buttons.append(chairList)
            chairList = []
        if chair['id'] in [10,16]:
            buttons.append(chairList)
            chairList = []

    return buttons
