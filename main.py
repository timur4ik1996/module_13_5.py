from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
# для клавиатур:
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio

api = '...'
bot = Bot(token=api)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
kb.row(button1, button2)
# kb.add..., kb.insert...

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я -- бот помогающий твоему здоровью.',
                         reply_markup=kb)

@dp.message_handler(text='Рассчитать')
async def set_age(message):
    await message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(text='Информация')
async def info(message):
    await message.answer('Я -- бот, рассчитывающий норму ккал по упрощенной формуле Миффлина-Сан Жеора.')


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост (см):')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес (кг):')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    try:
        age = float(data['age'])
        weight = float(data['weight'])
        growth = float(data['growth'])
    except:
        await message.answer(f'Не могу конвертировать введенные значения в числа.')
        await state.finish()
        return


    calories_man = 10 * weight + 6.25 * growth - 5 * age + 5
    calories_wom = 10 * weight + 6.25 * growth - 5 * age - 161
    await message.answer(f'Норма (муж.): {calories_man} ккал')
    await message.answer(f'Норма (жен.): {calories_wom} ккал')
    await state.finish()


@dp.message_handler()
async def all_messages(message):
    print(f'Получено: {message.text}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)