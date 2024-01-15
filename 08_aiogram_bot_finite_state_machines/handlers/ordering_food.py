from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.simple_row import make_row_keyboard

router = Router()

# Эти значения далее будут подставляться в итоговый текст, отсюда такая на первый взгляд странная форма прилагательных
available_food_names = ["Суши", "Спагетти", "Хачапури"]
available_food_sizes = ["Маленькую", "Среднюю", "Большую"]
available_drink_names = ["Минералка", "Водка", "Пиво"]
available_drink_sizes = ["Рюмка", "Стакан", "Литр"]
swear_words = ['да пошел ты', 'тупой', 'дурак']


# Итак, перейдём непосредственно к описанию состояний. Все состояния можно объединить в один класс.
# Для хранения состояний необходимо создать класс, наследующийся от класса StatesGroup,
# внутри него нужно создать переменные, присвоив им экземпляры класса State:
class OrderFood(StatesGroup):
    choosing_food_name = State()
    choosing_food_size = State()


class OrderDrink(StatesGroup):
    choosing_drink_name = State()
    choosing_drink_size = State()


# Пользователь грубит
class UserHector(StatesGroup):
    user_hector = State()


@router.message(F.text.lower().in_(swear_words))
async def swear_words(message: Message, state: FSMContext):
    await message.answer(text="Вы оскорбили бота!\nНадо бы извиниться.", reply_markup=make_row_keyboard([], add_button='Прости, бот, я больше так не буду'))
    await state.set_state(UserHector.user_hector)


@router.message(UserHector.user_hector, F.text.in_(['прости', 'извини', 'Извини']))
@router.message(UserHector.user_hector, F.text.startswith('Прости'))
async def swear_words(message: Message, state: FSMContext):
    await message.answer(text=f'Не вздумай повторить это, {message.from_user.full_name}!')
    await cmd_food(message, state)


@router.message(UserHector.user_hector)
async def swear_words(message: Message, state: FSMContext):
    await message.answer(text=f'Пока ты, {message.from_user.full_name}, не извинишься,\nя на твои просьбы не реагирую!')


# Обработчик первого шага, реагирующий на команду /food в случае, если у пользователя не установлен никакой State:
@router.message(StateFilter(None), Command('food'))
async def cmd_food(message: Message, state: FSMContext):
    await message.answer(text="Выберите блюдо:", reply_markup=make_row_keyboard(available_food_names))
    # Устанавливаем пользователю состояние "выбирает название блюда"
    await state.set_state(OrderFood.choosing_food_name)


# Обработчик шага, реагирующий на команду /drink в случае, если у пользователя не установлен никакой State:
@router.message(StateFilter(None), Command('drink'))
async def cmd_drink(message: Message, state: FSMContext):
    await message.answer(text="Выберите напиток:", reply_markup=make_row_keyboard(available_drink_names))
    # Устанавливаем пользователю состояние "выбирает название напитка"
    await state.set_state(OrderDrink.choosing_drink_name)


# Этап выбора блюда #

# Фильтры сообщают, что нижестоящая функция сработает тогда и только тогда,
# когда пользователь будет в состоянии OrderFood.choosing_food_name и текст сообщения будет совпадать с одним из элементов списка available_food_names.
@router.message(OrderFood.choosing_food_name, F.text.in_(available_food_names))
async def food_chosen(message: Message, state: FSMContext):
    # Пишем данные (текст сообщения) в хранилище FSM, и эти данные уникальны для пары (chat_id, user_id) (есть нюанс, о нём позже).
    await state.update_data(chosen_food=message.text.lower())
    await message.answer(text="Спасибо. Теперь, пожалуйста, выберите размер порции:", reply_markup=make_row_keyboard(available_food_sizes, add_button='Отмена'))
    # Наконец, переводим пользователя в состояние OrderFood.choosing_food_size.
    await state.set_state(OrderFood.choosing_food_size)


# А если пользователь решит ввести что-то самостоятельно, без клавиатуры?
# В этом случае, надо сообщить пользователю об ошибке и дать ему ещё попытку.
# Очень часто начинающие разработчки ботов на этом моменте задают вопрос: «а как оставить юзера в том же состоянии?».
# Ответ простой: чтобы оставить пользователя в текущем состоянии, достаточно его [состояние] не менять, т.е. буквально ничего не делать.
# Напишем дополнительный хэндлер, у которого будет фильтр только на состояние OrderFood.choosing_food_name, а фильтра на текст не будет.
# Если расположить его под функцией food_chosen(), то получится «реагируй в состоянии choosing_food_name, на все тексты, кроме тех, что ловит предыдущий хэндлер» (иными словами, «лови все неправильные варианты»).
@router.message(OrderFood.choosing_food_name)
# В целом, никто не мешает указывать State полностью строками. Это может пригодиться, если по какой-то причине ваши названия стейтов генерируются в рантайме (но зачем?)
# @router.message(StateFilter("OrderFood:choosing_food_name"))
async def food_chosen_incorrectly(message: Message):
    await message.answer(text="Я не знаю такого блюда.\n\n""Пожалуйста, выберите одно из названий из списка ниже:", reply_markup=make_row_keyboard(available_food_names, add_button='Отмена'))


# Этап выбора размера порции и отображение сводной информации

@router.message(OrderFood.choosing_food_size, F.text.in_(available_food_sizes))
async def food_size_chosen(message: Message, state: FSMContext):
    # Вызов get_data() возвращает объект хранилища для конкретного пользователя в конкретном чате.
    # Из него [хранилища] мы достаём сохранённое значение название блюда и подставляем в сообщение.
    user_data = await state.get_data()
    await message.answer(text=f"Вы выбрали {message.text.lower()} порцию {user_data['chosen_food']}.\n"f"Попробуйте теперь заказать напитки: /drink", reply_markup=ReplyKeyboardRemove())
    # Метод clear() у State возвращает пользователя в «пустое» состояние и удаляет все сохранённые данные.
    # Сброс состояния и сохранённых данных у пользователя
    await state.clear()
    # Что делать, если нужно только очистить состояние или только затереть данные?
    # Для этого провалимся в определение функции clear() в исходниках aiogram 3.x:
    # class FSMContext:
    #     # Часть кода пропущена
    #
    #     async def clear(self) -> None:
    #         await self.set_state(state=None)
    #         await self.set_data({})
    # Теперь вы знаете, как очистить что-то одно :)


@router.message(OrderFood.choosing_food_size)
async def food_size_chosen_incorrectly(message: Message):
    await message.answer(text="Я не знаю такого размера порции.\n\n""Пожалуйста, выберите один из вариантов из списка ниже:", reply_markup=make_row_keyboard(available_food_sizes, add_button='Отмена'))


# Этап выбора напитка

# Фильтры сообщают, что нижестоящая функция сработает тогда и только тогда,
@router.message(OrderDrink.choosing_drink_name, F.text.in_(available_drink_names))
async def drink_chosen(message: Message, state: FSMContext):
    # Пишем данные (текст сообщения) в хранилище FSM, и эти данные уникальны для пары (chat_id, user_id)
    await state.update_data(chosen_drink=message.text.lower())
    await message.answer(text="Спасибо. Теперь, пожалуйста, выберите размер порции:", reply_markup=make_row_keyboard(available_drink_sizes, add_button='Отмена'))
    # Наконец, переводим пользователя в состояние OrderDrink.choosing_drink_size.
    await state.set_state(OrderDrink.choosing_drink_size)


@router.message(OrderDrink.choosing_drink_name)
async def drink_chosen_incorrectly(message: Message):
    await message.answer(text="Я не знаю такого напитка.\n\n""Пожалуйста, выберите одно из названий из списка ниже:", reply_markup=make_row_keyboard(available_drink_names, add_button='Отмена'))


# Этап выбора размера порции и отображение сводной информации

@router.message(OrderDrink.choosing_drink_size, F.text.in_(available_drink_sizes))
async def drink_size_chosen(message: Message, state: FSMContext):
    # Вызов get_data() возвращает объект хранилища для конкретного пользователя в конкретном чате.
    # Из него [хранилища] мы достаём сохранённое значение название напитка и подставляем в сообщение.
    user_data = await state.get_data()
    await message.answer(text=f"Вы выбрали порцию '{message.text.lower()}' напитка '{user_data['chosen_drink']}'.\n"f"Хорошо вам посидеть!", reply_markup=ReplyKeyboardRemove())
    # Метод clear() у State возвращает пользователя в «пустое» состояние и удаляет все сохранённые данные.
    # Сброс состояния и сохранённых данных у пользователя
    await state.clear()


@router.message(OrderDrink.choosing_drink_size)
async def drink_size_chosen_incorrectly(message: Message):
    await message.answer(text="Я не знаю такого размера порции.\n\n""Пожалуйста, выберите один из вариантов из списка ниже:", reply_markup=make_row_keyboard(available_drink_sizes, add_button='Отмена'))


