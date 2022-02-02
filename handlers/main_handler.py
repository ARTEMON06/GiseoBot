from aiogram import types
from aiogram.dispatcher import FSMContext
from tools.PyGiseo import Parse
from tools import DbTools
from loader import dp, bot
from states import Menu
from .keyboards import *
import datetime
from handlers import start_handler


# печатаем основное меню
@dp.callback_query_handler(state=Menu.main_menu)
async def main_menu(call: types.CallbackQuery, mode=False):

    if call.data == 'start' or mode:
        if not mode:
            await call.message.delete()
        await DbTools.send_photo(call, 'main_page.png', mode=2,
                                 caption=f'Главное меню, пользователя {call.message.chat.username}',
                                 reply_markup=main_menu_keyboard)
        await Menu.func.set()
    else:
        await DbTools.send_photo(call, 'main_page.png')
        await call.message.edit_caption(caption=f'Главное меню, пользователя {call.message.chat.username}',
                                        reply_markup=main_menu_keyboard)
        await Menu.func.set()


# меню основных функций
@dp.callback_query_handler(state=Menu.func)
async def functions(call: types.CallbackQuery):
    if call.data == 'back':
        await main_menu(call)

    if call.data == 'homework_t':
        day = datetime.datetime.today().weekday() + 1
        next_day = datetime.date.today() + datetime.timedelta(days=1)
        next_day = next_day.strftime('%d.%m.%y')
        if day == 7: day = 1
        homework = DbTools.get_homework_text(call.message.chat.id, day)
        if homework:
            await DbTools.send_photo(call, f'homework.png')
            await call.message.edit_caption(f'Ваше домашнее задние на <b>{name_of_day(day)}, {next_day}</b>\n\n'
                                            f'{homework}',
                                            reply_markup=homework_back_t_keyboard, parse_mode='html')
        else:
            await call.answer('Информации нет на сайте!')

    if call.data == 'homework_n':
        day = datetime.datetime.today().weekday()
        today = datetime.date.today()
        today = today.strftime('%d.%m.%y')
        if day == 6: day = 0
        homework = DbTools.get_homework_text(call.message.chat.id, day)
        duty = DbTools.get_duty_text(call.message.chat.id)
        if homework:
            await DbTools.send_photo(call, f'homework.png')
            await call.message.edit_caption(f'Ваше домашнее задание на <b>{name_of_day(day)}, {today}</b>\n\n'
                                            f'{homework}\n<b>Ваши просроченные задания:</b>\n\n{duty}',
                                            reply_markup=homework_back_n_keyboard, parse_mode='html')
        else:
            await call.answer('Информации нет на сайте!')

    if call.data == 'next':
        day = datetime.datetime.today().weekday() + 1
        next_day = datetime.date.today() + datetime.timedelta(days=1)
        next_day = next_day.strftime('%d.%m.%y')
        if day == 7: day = 1
        if await DbTools.send_photo(call, f'parse_schedule_{day}.png'):
            await call.message.edit_caption(f'Ваше расписание на <b>{name_of_day(day)}, '
                                            f'{next_day}</b>',
                                            reply_markup=today_keyboard, parse_mode='html')

    if call.data == 'schedule':
        day = datetime.datetime.today().weekday()
        today = datetime.date.today()
        today = today.strftime('%d.%m.%y')
        if day == 6: day = 0
        if await DbTools.send_photo(call, f'parse_schedule_{day}.png'):
            await call.message.edit_caption(f'Ваше расписание на <b>{name_of_day(day)}, {today}'
                                            f'</b>', reply_markup=next_keyboard, parse_mode='html')

    if call.data == 'year':
        if await DbTools.send_photo(call, 'parse_middle_marks_year.png'):
            await call.message.edit_caption('Ваши средние баллы по предметам за год', reply_markup=back_keyboard)

    if call.data == 'quarter':
        await menu_quarter(call)

    if call.data == 'final':
        if await DbTools.send_photo(call, 'parse_final_marks.png'):
            await call.message.edit_caption('Ваши итоговые отметки', reply_markup=back_keyboard)

    if call.data == 'update':
        await update(call)

    if call.data == 'info':
        await menu_info(call)

    if call.data == 'account':
        await account_menu(call)


def name_of_day(day):
    if day == 0: return 'понедельник'
    if day == 1: return 'вторник'
    if day == 2: return 'среду'
    if day == 3: return 'четверг'
    if day == 4: return 'пятницу'
    if day == 5: return 'субботу'


async def menu_info(call: types.CallbackQuery):
    await DbTools.send_photo(call, 'info.png')
    await call.message.edit_caption('Выберите функцию ⬇', reply_markup=info_keyboard)
    await Menu.info_menu.set()


@dp.callback_query_handler(state=Menu.info_menu)
async def func_info(call: types.CallbackQuery):
    if call.data == 'back_info':
        await main_menu(call)
    if call.data == 'back':
        await menu_info(call)
    if call.data == 'support':
        await DbTools.send_photo(call, 'support.png')
        await call.message.edit_caption('По <a href="https://my.qiwi.com/Artem-S89vlnLKHq">этой ссылке</a> '
                                        'можно поддрежать наш проект! Спасибо!',
                                        reply_markup=back_keyboard, parse_mode='html')
    if call.data == 'over':
        await DbTools.send_photo(call, 'over.png')
        await call.message.edit_caption('Другие наши разработки можно увидеть на '
                                        '<a href="https://github.com/Genius-Team-DA?tab=repositories">'
                                        'репозитории гитхаб</a>',
                                        reply_markup=back_keyboard, parse_mode='html')
    if call.data == 'connect':
        await DbTools.send_photo(call, 'connect.png')
        await call.message.edit_caption('Наша почта: geniusteam@internet.ru', reply_markup=back_keyboard)


async def update(call: types.CallbackQuery):
    await call.message.delete()
    mes1 = await call.message.answer('📥 Обновление информации 📥\n')
    res = DbTools.update_data(call.message.chat.id)
    if res != 'error':
        mes2 = await call.message.answer('✔ Обновление завершено! ✔')
    else:
        mes2 = await call.message.answer('❌ Ошибка при входе ❌\nпопробуйте позже...')
    await bot.delete_message(call.message.chat.id, mes1.message_id)
    await bot.delete_message(call.message.chat.id, mes2.message_id)
    await main_menu(call, mode=True)


async def menu_quarter(call: types.CallbackQuery):
    await DbTools.send_photo(call, 'select_quarter.png')
    await call.message.edit_caption('Выберите четверть ⬇', reply_markup=quarter_select_keyboard)
    await Menu.quarter_select.set()


async def account_menu(call):
    data = DbTools.get_user_data(call.message.chat.id)
    name = data[1]
    school = data[6]
    theme = data[7]

    if theme == 'theme_1':
        theme = 'светлая'
    elif theme == 'theme_2':
        theme = 'темная'
    elif theme == 'theme_3':
        theme = 'контрастная'

    await DbTools.send_photo(call, 'account_menu.png')
    await call.message.edit_caption(f'Сведения об аккаунте:\n\n'
                                    f'<b>Логин: </b>{name}\n'
                                    f'<b>ОО: </b>{school}\n'
                                    f'<b>Тема бота: </b>{theme}', reply_markup=account_keyboard, parse_mode='html')

    await Menu.account_menu.set()


# меню выбора четверти и посылка фото
@dp.callback_query_handler(state=Menu.quarter_select)
async def func_quarter(call: types.CallbackQuery):

    if call.data == 'select_quarter_1':
        if await DbTools.send_photo(call, 'parse_middle_marks_period_1.png'):
            await call.message.edit_caption('Баллы <b>1 четверть</b>', reply_markup=back_keyboard, parse_mode='html')

    elif call.data == 'select_quarter_2':
        if await DbTools.send_photo(call, 'parse_middle_marks_period_2.png'):
            await call.message.edit_caption('Баллы <b>2 четверть</b>', reply_markup=back_keyboard, parse_mode='html')

    elif call.data == 'select_quarter_3':
        if await DbTools.send_photo(call, 'parse_middle_marks_period_3.png'):
            await call.message.edit_caption('Баллы <b>3 четверть</b>', reply_markup=back_keyboard, parse_mode='html')

    elif call.data == 'select_quarter_4':
        if await DbTools.send_photo(call, 'parse_middle_marks_period_4.png'):
            await call.message.edit_caption('Баллы <b>4 четверть</b>', reply_markup=back_keyboard, parse_mode='html')

    if call.data == 'back':
        await menu_quarter(call)

    if call.data == 'back_selected':
        await main_menu(call)


# меню аккаунта
@dp.callback_query_handler(state=Menu.account_menu)
async def func_account_menu(call: types.CallbackQuery):
    if call.data == 'logout':
        await DbTools.send_photo(call, 'confirm.png')
        await call.message.edit_caption('Вы уверены, что хотите выйти?', reply_markup=logout_confirm_keyboard)
        await Menu.logout_confirm.set()
    elif call.data == 'change_theme':
        await DbTools.send_photo(call, 'theme_change_variants.png')
        await call.message.edit_caption('', reply_markup=change_theme_keyboard)
        await Menu.theme_change.set()
    elif call.data == 'vip':
        await call.answer('Эта функция еще не доступна, терпение...')
    if call.data == 'back':
        await main_menu(call)


@dp.callback_query_handler(state=Menu.theme_change)
async def func_change_theme(call: types.CallbackQuery):
    data = DbTools.get_user_data(chat_id=call.message.chat.id)
    theme_now = data[7]

    if theme_now == call.data:
        await call.answer('Тема уже установлена')
        await account_menu(call)

    elif call.data == 'back':
        await account_menu(call)

    else:
        await changing_theme(call, call.data)


async def changing_theme(call, theme):
    await call.message.delete()
    mes1 = await call.message.answer('📥 Обновление информации 📥\n')
    res = DbTools.change_theme(call.message.chat.id, theme)
    if res == 'error':
        mes2 = await call.message.answer('❌ Ошибка при смене темы ❌\nпопробуйте позже...')
    else:
        print('ok')
        mes2 = await call.message.answer('✔ Обновление завершено! ✔')
    await bot.delete_message(call.message.chat.id, mes1.message_id)
    await bot.delete_message(call.message.chat.id, mes2.message_id)
    await main_menu(call, mode=True)


# подтверждение выхода
@dp.callback_query_handler(state=Menu.logout_confirm)
async def func_confirm_logout(call: types.CallbackQuery):
    if call.data == 'yes':
        DbTools.logout_user(call.message.chat.id)
        await call.message.delete()
        await call.answer('Вы вышли из аккаунта!')
        await start_handler.start(call.message)
    elif call.data == 'no':
        await account_menu(call)
