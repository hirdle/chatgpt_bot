import os

API_TOKEN_BOT = "6299673742:AAECZWIdE_-nNaEVsJ9jwhsae15QJ7EvntA"
API_TOKEN_OPENAI = os.environ['API_TOKEN_OPENAI'] 

channel_id = -1001641980767


subscription_text = """
Для использования бота вам нужно подписаться на канал или приобрести подписку👇

После того как подпишитесь на канал нажмите кнопку "Проверить подписку"

Или оформите "Премиум тариф"
"""

no_subscription_text = """
Вы еще не подписались на канал

Для использования бота вам нужно подписаться на канал или приобрести подписку👇

После того как подпишитесь на канал нажмите кнопку "Проверить подписку"

Или оформите "Премиум тариф"
"""

premium_text = """
Premium✨

❇️ Высокая скорость ответов: Пользователи, получают более быстрые и точные ответы. Тариф дает доступ к более мощным серверам и алгоритмам, которые позволяют боту быстрее обрабатывать запросы и предоставлять более точные ответы.

❇️ Расширенные возможности: Premium дает более широкий диапазон возможностей для пользователей. Например, расширенный словарный запас, автоматический перевод на другие языки, возможность задавать более сложные вопросы и получать более детальные ответы.

❇️ Конфиденциальность: Улучшенный уровень конфиденциальности и защиты данных, шифрование сообщений.

❇️ Индивидуальный подход: Premium пользователи получают возможность задавать персональные вопросы и получать персонализированные ответы.

❇️ Высокая точность: Premium пользователи получают более точные ответы. Это связано с более актуальными базами данных, а также с использованием более современных алгоритмов нейросети.

💰Цена 60р/мес.
@brusnika_s

Что еще дает тариф Premium?
Респект от нашей команды за поддержку проекта.
"""

await_text = """Ваш текст сейчас готовиться, это может занять некоторое время."""