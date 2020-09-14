import pushapper_telegram_bot


def test_get_pep_talk():
    assert pushapper_telegram_bot.get_pep_talk("пес", 42, 123) == \
        'Эй ты! Ленивая задница! Пока ты делал свой PhD, некто пес легчайше нахуярил уже 42 отжиманий.'
