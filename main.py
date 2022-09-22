from group import get_current_schedule
from raspisanie import Schedule
import telebot
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from telebot import types
import datetime

schedule = Schedule()
state_storage = StateMemoryStorage()
bot = telebot.TeleBot('', state_storage=state_storage)

class MyStates(StatesGroup):
    group = State()

# Начало
@bot.message_handler(commands=['start','help'])
def start(message):
    mess = f'Привет, {message.from_user.first_name}. Этот бот предназначен только для студентов ЧЭМК корпуса 4, никто больше не имеет права пользоваться им!!!'
    bot.send_message(message.chat.id, mess, parse_mode='html')
    mess = '''Данные по расписаниям берутся из актуальных источников сайта http://www.chemk.org для 4 корпуса
Чтобы воспользоваться ботом выберите группу /group <Имя_вашей_группы>:
Например, /group Ип1-19'''
    groups = ""
    for group in schedule.get_full_schedule():
        groups += f'''
{group['group']}'''

    bot.send_message(message.chat.id, f'''
Группы которые здесь есть:
{groups}''')
    bot.send_message(message.chat.id,mess)
    bot.send_message(message.chat.id,"Если вы не студент ЧЭМК 4 корпуса, то я Вас накажу",parse_mode='html')

# Ввод группы
@bot.message_handler(commands=['group'])
def group(message):
    group = schedule.find_schedule(message.text.split(" ")[1].strip())
    if group == False:
        bot.send_message(message.chat.id, "Извините, но у меня нет такой группы")
    else:
        mess = f'''
Группа: {group['group']}
Далее пожалуйста введите день недели, чтобы узнать какие пары есть на этот день
Например, /week_day Понедельник
Или же вы можете посмотреть есть ли замены на завтра или сегодня:
/today - сегодня
/tomorrow - завтра'''

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
        btn1 = types.KeyboardButton("/Сегодня")
        btn2 = types.KeyboardButton("/Завтра")
        btn3 = types.KeyboardButton("/Понедельник")
        btn4 = types.KeyboardButton("/Вторник")
        btn5 = types.KeyboardButton("/Среда")
        btn6 = types.KeyboardButton("/Четверг")
        btn7 = types.KeyboardButton("/Пятница")
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
        bot.send_message(message.chat.id, mess, reply_markup=markup)
        bot.set_state(message.from_user.id, MyStates.group, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['group'] = group

def get_message(group,day_number,time):
    lessons = {}
    for lesson in group['schedule']:
        if int(lesson['day_number']) == day_number:
            lessons = lesson['subjects']

    if lessons == {}:
        return "В данный день по данной группе нету пар"

    lessons_string = ""
    for lesson in lessons:
        if "type" in lesson:
            week_number = datetime.datetime.fromtimestamp(time).strftime('%V')
            if (int(week_number)+1) % 2 == int(lesson['type']):
                lessons_string += f'''
№ пары: {lesson['number']}
Название: {lesson['name']}
Преподаватель: {lesson['teacher']}
Кабинет: {lesson['cabinet']}
'''
        else:
            lessons_string += f'''
№ пары: {lesson['number']}
Название: {lesson['name']}
Преподаватель: {lesson['teacher']}
Кабинет: {lesson['cabinet']}
'''

    return f'''Группа: {group['group']}
Пары: 
{lessons_string}'''

# Функции для выдачи сообщений по дням недели
@bot.message_handler(commands=['Понедельник','понедельник'])
def monday(message):
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if data == None:
                bot.send_message(message.chat.id, 'Пожалуйста сначала введите группу')
            else:
                bot.send_message(message.chat.id, get_message(data['group'], 1, message.date))

    except Exception:
        print('OK')

@bot.message_handler(commands=['Вторник','вторник'])
def tuesday(message):
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if data == None:
                bot.send_message(message.chat.id, 'Пожалуйста сначала введите группу')
            else:
                bot.send_message(message.chat.id, get_message(data['group'], 2, message.date))

    except Exception:
        print('OK')

@bot.message_handler(commands=['Среда','среда'])
def wednesday(message):
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if data == None:
                bot.send_message(message.chat.id, 'Пожалуйста сначала введите группу')
            else:
                bot.send_message(message.chat.id, get_message(data['group'], 3, message.date))

    except Exception:
        print('OK')

@bot.message_handler(commands=['Четверг','четверг'])
def thursday(message):
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if data == None:
                bot.send_message(message.chat.id, 'Пожалуйста сначала введите группу')
            else:
                bot.send_message(message.chat.id, get_message(data['group'], 4, message.date))

    except Exception:
        print('OK')

@bot.message_handler(commands=['Пятница','пятница'])
def friday(message):
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if data == None:
                bot.send_message(message.chat.id, 'Пожалуйста сначала введите группу')
            else:
                bot.send_message(message.chat.id, get_message(data['group'], 5, message.date))

    except Exception:
        print('OK')

def get_subgroup(group_name):
    i = 0
    array = group_name.split(" ")
    while i < len(array):
        if len(array[i]) == 1:
            return " ".join(array[i:])
        i += 1

def get_message_td_tm(group,type):
    if group == None:
        return 'Пожалуйста сначала введите группу'

    lessons = []
    changes = get_current_schedule(f"https://rsp.chemk.org/4korp/{type}.htm")
    if not changes:
        return "Замены еще не созданы"
    for change in changes:
        if change.get_group().startswith(group['group']):
            lessons.append({
                "lessons": change.get_lessons(),
                "group": change.get_group()
            })

    if type == "today":
        day = "сегодня"
    elif type == "tomorrow":
        day = "завтра"
    else:
        return "Ошибка: бот не правильно понял что хорошо, что плохо"

    if len(lessons) == 0:
        return f'В данной группе {day} нету замены'
    else:
        lessons_string = ""
        for lesson in lessons:
            for l in lesson['lessons']:
                string = ""
                if len(lesson['group']) > 6:
                    print(lesson['group'])
                    string = f"\r\nПодгруппа:{get_subgroup(lesson['group'])}"
                if len(l['lesson']) > 1:
                    continue
                string += f'''
№ пары: {l['lesson']}
Предмет: {l['subject']}
Кабинет: {l['cabinet']}
    '''
                lessons_string += string

    msg = f'''
Замены на {day}!
Группа: {group['group']}
Пары: 
{lessons_string}'''
    return msg

# Функции для выдачи сообщений по заменам на сегодня и завтра
@bot.message_handler(commands=['Сегодня','сегодня'])
def today(message):
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if data == None:
                bot.send_message(message.chat.id, 'Пожалуйста сначала введите группу')
            else:
                bot.send_message(message.chat.id, get_message_td_tm(data['group'], type='today'))

    except Exception:
        print('OK')

@bot.message_handler(commands=['завтра','Завтра'])
def today(message):
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if data == None:
                bot.send_message(message.chat.id, 'Пожалуйста сначала введите группу')
            else:
                bot.send_message(message.chat.id, get_message_td_tm(data['group'], type='tomorrow'))

    except Exception:
        print('OK')

bot.polling(none_stop=True)