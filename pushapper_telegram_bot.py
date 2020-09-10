#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import json
import logging
import os
import time

from datetime import datetime, timedelta

from telegram.ext import (Updater, CommandHandler)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


CHAT_ID = -495468183
CHAT_ID_RAVENKLO = 192021208


class Data:
    DEFAULT_DATA = {
        'notify_chat_id': CHAT_ID_RAVENKLO,
        'clear_every_n_days': 7,
        'last_clear_timestamp': time.time(),
        'leaderboard': dict(),
    }

    def __init__(self, filename='pushapper_data.json'):
        self.filename = filename
        if os.path.exists(filename):
            with open(filename) as f:
                data_from_file = json.load(f)
        else:
            data_from_file = dict()
        self.data = dict(self.DEFAULT_DATA)
        self.data.update(data_from_file)

    def add_pushups(self, username, num_pushups):
        self.clear_if_needed()
        leaderboard_dict = self.data['leaderboard']
        if username in leaderboard_dict:
            count = int(leaderboard_dict[username])
        else:
            count = 0
        leaderboard_dict[username] = count + num_pushups
        self.save()

    def clear(self):
        self.data['leaderboard'].clear()
        self.data['last_clear_timestamp'] = time.time()
        self.save()

    def get_time_left(self):
        clear_datetime = (
            datetime.fromtimestamp(self.data['last_clear_timestamp']) +
            timedelta(days=int(self.data['clear_every_n_days']))
        )
        return clear_datetime - datetime.now()

    def need_to_clear(self):
        return self.get_time_left().total_seconds() < 0

    def clear_if_needed(self):
        if self.need_to_clear():
            self.clear()

    def get_leaderboard_items(self):
        return list(sorted(
            self.data['leaderboard'].items(),
            key=lambda x: x[1],
            reverse=True,
        ))

    def leaderboard(self):
        self.clear_if_needed()
        leaderboard_lines = []
        time_left = self.get_time_left()
        leaderboard_lines.append('Хреначить осталось дней: {} | часов: {}'.format(
            time_left.days,
            time_left.seconds // (60 * 60),
        ))
        leaderboard_lines.extend([
            '{}: {}'.format(k, v)
            for k, v in self.get_leaderboard_items()
        ] or ['EMPTY'])
        return '\n'.join(leaderboard_lines)

    def get_leader_name_and_count(self):
        leaderboard_items = self.get_leaderboard_items()
        if len(leaderboard_items) > 0:
            return leaderboard_items[0]
        else:
            return 'NONE', 0

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def set_notify_chat_id(self, chat_id):
        self.set_data_attr('notify_chat_id', chat_id)

    def get_notify_chat_id(self):
        return self.get_data_attr('notify_chat_id')

    def set_clear_every_n_days(self, clear_every_n_days):
        self.set_data_attr('clear_every_n_days', int(clear_every_n_days))

    def get_clear_every_n_days(self):
        return self.get_data_attr('clear_every_n_days')

    def set_data_attr(self, attr_name, attr_value):
        if attr_name in self.data and isinstance(self.data[attr_name], int):
            attr_value = int(attr_value)

        self.data[attr_name] = attr_value
        self.save()

    def get_data_attr(self, attr_name):
        return self.data[attr_name]


def get_msg_arg(update):
    return get_msg_args(update)[0]


def get_msg_args(update):
    return update.effective_message['text'].split()[1:]


def start(update, context):
    """Inform user about what this bot can do"""
    update.message.reply_text('\n'.join([
        '/add_pushups_10',
        '/add_pushups_20',
        '/add_pushups_30',
        '/add_pushups_40',
        '/add_pushups_50',
        '/leaderboard',
        '/clear',
    ]))
    print('*' * 100)
    print(update.effective_message)


def add_pushups(update, context, num_pushups=None):
    print('*' * 100)
    print(update.effective_message)
    username = update.effective_message.from_user.username
    print('username: {}'.format(username))
    if num_pushups is None:
        num_pushups = int(get_msg_arg(update))

    data = Data()

    update_msg_lines = []
    if data.need_to_clear():
        leader_name, leader_count = data.get_leader_name_and_count()
        update_msg_lines.append(
            'Звание самого упоротого за прошлую неделю достается гн. {} с {} отжиманиями\n'.format(
                leader_name,
                leader_count,
            )
        )

    update_msg_lines.append('Эй ты! ленивая задница! Некто {} нахуярил уже {} отжиманий'.format(
        username,
        num_pushups,
    ))

    data.add_pushups(username=username, num_pushups=num_pushups)
    notify_all(
        context,
        data=data,
        update_msg='\n'.join(update_msg_lines),
    )


def notify_all(context, data, update_msg):
    context.bot.send_message(chat_id=data.get_notify_chat_id(), text='\n'.join([
        update_msg,
        data.leaderboard(),
    ]))


def leaderboard(update, context):
    print('leaderboard')
    data = Data()
    update.message.reply_text(data.leaderboard())


def clear(update, context):
    Data().clear()


def set_notify_chat_id(update, context):
    set_attr(update, context, attr_name='notify_chat_id')


def set_attr(update, context, attr_name=None):
    msg_args = get_msg_args(update)
    if attr_name is None:
        attr_name = msg_args[0]
        attr_value = msg_args[1]
    else:
        attr_value = msg_args[0]
    Data().set_data_attr(attr_name, attr_value)

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1389342304:AAEIow_maY4lEdxIvJlHdINgympV6SwHID8", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('add_pushups_10', functools.partial(add_pushups, num_pushups=10)))
    dp.add_handler(CommandHandler('add_pushups_20', functools.partial(add_pushups, num_pushups=20)))
    dp.add_handler(CommandHandler('add_pushups_30', functools.partial(add_pushups, num_pushups=30)))
    dp.add_handler(CommandHandler('add_pushups_40', functools.partial(add_pushups, num_pushups=40)))
    dp.add_handler(CommandHandler('add_pushups_50', functools.partial(add_pushups, num_pushups=50)))
    dp.add_handler(CommandHandler('add_pushups_60', functools.partial(add_pushups, num_pushups=60)))
    dp.add_handler(CommandHandler('add_pushups_70', functools.partial(add_pushups, num_pushups=70)))
    dp.add_handler(CommandHandler('add_pushups_80', functools.partial(add_pushups, num_pushups=80)))
    dp.add_handler(CommandHandler('add_pushups_90', functools.partial(add_pushups, num_pushups=90)))
    dp.add_handler(CommandHandler('add_pushups_100', functools.partial(add_pushups, num_pushups=100)))

    dp.add_handler(CommandHandler('add_pushups', add_pushups))

    dp.add_handler(CommandHandler('set_notify_chat_id', set_notify_chat_id))
    dp.add_handler(CommandHandler(
        'set_clear_every_n_days',
        functools.partial(set_attr, attr_name='clear_every_n_days')))

    dp.add_handler(CommandHandler('set', set_attr))

    dp.add_handler(CommandHandler('leaderboard', leaderboard))
    dp.add_handler(CommandHandler('clear', clear))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
