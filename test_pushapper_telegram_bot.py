import pushapper_telegram_bot


def test_get_pep_talk():
    assert pushapper_telegram_bot.get_pep_talk("пес", 42) == \
        'Эй ты! ленивая задница! Некто пес нахуярил уже 42 отжиманий'
