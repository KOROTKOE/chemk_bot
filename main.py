from group import get_current_schedule
from raspisanie import Schedule
import telebot
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
import datetime

schedule = Schedule()
state_storage = StateMemoryStorage()
bot = telebot.TeleBot('5776516065:AAHygfHJNxfTAgCxTyJePWYZ-sgG-3jFzPE', state_storage=state_storage)

class MyStates(StatesGroup):
    group = State()

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
        bot.send_message(message.chat.id, mess)
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

@bot.message_handler(commands=['week_day'])
def week(message):
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if data == None:
                bot.send_message(message.chat.id,'Пожалуйста сначала введите группу')
            else:
                group = data['group']
                match message.text.split(" ")[1].strip():
                    case "Понедельник":
                        bot.send_message(message.chat.id, get_message(group, 1, message.date))
                    case "Вторник":
                        bot.send_message(message.chat.id, get_message(group, 2, message.date))
                    case "Среда":
                        bot.send_message(message.chat.id, get_message(group, 3, message.date))
                    case "Четверг":
                        bot.send_message(message.chat.id, get_message(group, 4, message.date))
                    case "Пятница":
                        bot.send_message(message.chat.id, get_message(group, 5, message.date))
                    case "Суббота":
                        bot.send_message(message.chat.id, get_message(group, 6))

    except Exception:
        print('OK')

def get_message_td_tm(group,type):
    if group == None:
        return 'Пожалуйста сначала введите группу'

    lessons = {}
    changes = get_current_schedule(f"https://rsp.chemk.org/4korp/{type}.htm")
    if not changes:
        return "Замены еще не созданы"
    for change in changes:
        if change.get_group().startswith(group['group']):
            lessons = change.get_lessons()

    if type == "today":
        day = "сегодня"
    elif type == "tomorrow":
        day = "завтра"
    else:
        return "Ошибка: бот не правильно понял что хорошо, что плохо"

    if lessons == {}:
        return f'В данной группе {day} нету замены'
    else:
        lessons_string = ""
        for lesson in lessons:
            lessons_string += f'''
№ пары: {lesson['lesson']}
Предмет: {lesson['subject']}
Кабинет: {lesson['cabinet']}
    '''

    msg = f'''
Замены на {day}!
Группа: {group['group']}
Пары: 
{lessons_string}'''
    return msg

@bot.message_handler(commands=['today'])
def today(message):
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if data == None:
                bot.send_message(message.chat.id, 'Пожалуйста сначала введите группу')
            else:
                bot.send_message(message.chat.id, get_message_td_tm(data['group'], type='today'))

    except Exception:
        print('OK')

@bot.message_handler(commands=['tomorrow'])
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