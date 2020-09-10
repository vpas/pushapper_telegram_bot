#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import logging
import json
import os

from telegram import (Poll, ParseMode, KeyboardButton, KeyboardButtonPollType,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, PollAnswerHandler, PollHandler, MessageHandler,
                          Filters)
from telegram.utils.helpers import mention_html

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


CHAT_ID = -495468183
CHAT_ID_RAVENKLO = 192021208


class Data:
    def __init__(self, filename='pushapper_data.json'):
        self.filename = filename
        if os.path.exists(filename):
            with open(filename) as f:
                self.data = json.load(f)
        else:
            self.data = {
                'notify_chat_id': CHAT_ID_RAVENKLO,
                'leaderboard': dict(),
            }

    def add_pushups(self, username, num_pushups):
        leaderboard_dict = self.data['leaderboard']
        if username in leaderboard_dict:
            count = int(leaderboard_dict[username])
        else:
            count = 0
        leaderboard_dict[username] = count + num_pushups
        self.save()

    def clear(self):
        self.data['leaderboard'].clear()
        self.save()

    def leaderboard(self):
        return '\n'.join([
            '{}: {}'.format(k, v)
            for k, v in sorted(
                self.data['leaderboard'].items(),
                key=lambda x: x[1],
                reverse=True,
            )
        ]) or 'EMPTY'

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f)

    def set_notify_chat_id(self, chat_id):
        self.data['notify_chat_id'] = chat_id
        self.save()

    def get_notify_chat_id(self):
        return self.data['notify_chat_id']


def get_msg_arg(update):
    return update.effective_message['text'].split()[1]


def start(update, context):
    """Inform user about what this bot can do"""
    update.message.reply_text('/add_pushups_10 /leaderboard /clear')
    print(update.effective_message)


def add_pushups(update, context, num_pushups=None):
    username = update.effective_message['chat']['username']
    if num_pushups is None:
        num_pushups = int(get_msg_arg(update))

    data = Data()
    data.add_pushups(username=username, num_pushups=num_pushups)
    update.message.reply_text(data.leaderboard())
    notify_all(
        context,
        data=data,
        update_msg='Эй ты, ленивая задница! Некто {} нахуярил ещё {} отжиманий!'.format(
            username,
            num_pushups,
        ),
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
    Data().set_notify_chat_id(get_msg_arg(update))

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
    dp.add_handler(CommandHandler('add_pushups', add_pushups))

    dp.add_handler(CommandHandler('set_notify_chat_id', set_notify_chat_id))

    dp.add_handler(CommandHandler('leaderboard', leaderboard))
    dp.add_handler(CommandHandler('clear', clear))

    # dp.add_handler(PollAnswerHandler(receive_poll_answer))
    # dp.add_handler(CommandHandler('quiz', quiz))
    # dp.add_handler(PollHandler(receive_quiz_answer))
    # dp.add_handler(CommandHandler('preview', preview))
    # dp.add_handler(MessageHandler(Filters.poll, receive_poll))
    # dp.add_handler(CommandHandler('help', help_handler))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
