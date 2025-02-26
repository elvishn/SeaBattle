from typing import List, Dict, Tuple
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command
from aiogram.utils.exceptions import TelegramAPIError, BadRequest
import copy

# Вместо BOT TOKEN HERE нужно вставить токен вашего бота,
# полученный у @BotFather
BOT_TOKEN = '7722734285:AAEVt-QgTQIU7W3OWeB713mi6I20CGSvwR8'

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Инициализируем константу размера игрового поля
FIELD_SIZE = 8

# Создаем словарь соответствий
LEXICON = {
    '/start': 'Вот твое поле. Можешь делать ход',
    0: ' ',
    1: '🌊',
    2: '💥',
    'miss': 'Мимо!',
    'hit': 'Попал!',
    'used': 'Вы уже стреляли сюда!',
    'next_move': 'Делайте ваш следующий ход'
}

# Хардкодим расположение кораблей на игровом поле
ships: List[List[int]] = [
    [1, 0, 1, 1, 1, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 1, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0]
]

# Инициализируем "базу данных" пользователей
users: Dict[int, Dict[str, list]] = {}


# Генерация callback_data
def generate_callback_data(x: int, y: int) -> str:
    return f"{x}:{y}"


# Парсинг callback_data
def parse_callback_data(data: str) -> Tuple[int, int]:
    x, y = map(int, data.split(":"))
    return x, y

# Функция, которая пересоздает новое поле для каждого игрока
def reset_field(user_id: int) -> None:
    users[user_id]['ships'] = copy.deepcopy(ships)
    users[user_id]['field'] = [
        [0 for _ in range(FIELD_SIZE)]
        for _ in range(FIELD_SIZE)
    ]
# Функция, генерирующая клавиатуру
def get_field_keyboard(user_id: int) -> types.InlineKeyboardMarkup:
    array_buttons: List[List[types.InlineKeyboardButton]] = []

    for i in range(FIELD_SIZE):
        array_buttons.append([])
        for j in range(FIELD_SIZE):
            array_buttons[i].append(types.InlineKeyboardButton(
                text=LEXICON[users[user_id]['field'][i][j]],
                callback_data=generate_callback_data(i, j)
            ))

    return types.InlineKeyboardMarkup(inline_keyboard=array_buttons)


# Хэндлер команды /start
@dp.message_handler(Command("start"))
async def process_start_command(message: types.Message):
    if message.from_user.id not in users:
        users[message.from_user.id] = {}
    reset_field(message.from_user.id)
    await message.answer(
        text=LEXICON['/start'],
        reply_markup=get_field_keyboard(message.from_user.id)
    )


# Этот хэндлер будет срабатывать на нажатие любой инлайн-кнопки на поле,
# запускать логику проверки результата нажатия и формирования ответа
@dp.callback_query_handler()
async def process_category_press(callback: types.CallbackQuery):
    x, y = parse_callback_data(callback.data)
    field = users[callback.from_user.id]['field']
    ships = users[callback.from_user.id]['ships']

    if field[x][y] == 0 and ships[x][y] == 0:
        answer = LEXICON['miss']
        field[x][y] = 1
    elif field[x][y] == 0 and ships[x][y] == 1:
        answer = LEXICON['hit']
        field[x][y] = 2
    else:
        answer = LEXICON['used']

    try:
        await callback.message.edit_text(
            text=LEXICON['next_move'],
            reply_markup=get_field_keyboard(callback.from_user.id)
        )
    except (TelegramAPIError, BadRequest) as e:
        pass

    await callback.answer(answer)


if __name__ == "__main__":
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
