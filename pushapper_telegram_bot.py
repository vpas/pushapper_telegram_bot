#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import logging

from telegram import (Poll, ParseMode, KeyboardButton, KeyboardButtonPollType,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, PollAnswerHandler, PollHandler, MessageHandler,
                          Filters)
from telegram.utils.helpers import mention_html

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class Data:
    def __init__(self, bot_data):
        self.bot_data = bot_data
        if 'pushapper' not in bot_data:
            bot_data['pushapper'] = dict()
        self.data = bot_data['pushapper']

    def add_pushups(self, username, num_pushups):
        if username in self.data:
            count = int(self.data[username])
        else:
            count = 0
        self.data[username] = count + num_pushups

    def clear(self):
        self.data.clear()

    def leaderboard(self):
        return '\n'.join([
            '{}: {}'.format(k, v)
            for k, v in sorted(
                self.data.items(),
                key=lambda x: x[1],
                reverse=True,
            )
        ]) or 'EMPTY'

    def save(self):
        pass


def start(update, context):
    """Inform user about what this bot can do"""
    update.message.reply_text('/add_pushups_10 /leaderboard /clear')


def add_pushups(update, context, num_pushups):
    username = update.effective_message['chat']['username']
    print('add_pushups num_pushups: {} user: {}'.format(num_pushups, username))
    data = Data(context.bot_data)
    data.add_pushups(username=username, num_pushups=num_pushups)
    update.message.reply_text(data.leaderboard())


def leaderboard(update, context):
    print('leaderboard')
    data = Data(context.bot_data)
    update.message.reply_text(data.leaderboard())


def clear(update, context):
    Data(context.bot_data).clear()


def poll(update, context):
    """Sends a predefined poll"""
    questions = ["Good", "Really good", "Fantastic", "Great"]
    message = context.bot.send_poll(update.effective_user.id, "How are you?", questions,
                                    is_anonymous=False, allows_multiple_answers=True)
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {message.poll.id: {"questions": questions, "message_id": message.message_id,
                                 "chat_id": update.effective_chat.id, "answers": 0}}
    context.bot_data.update(payload)


def receive_poll_answer(update, context):
    """Summarize a users poll vote"""
    answer = update.poll_answer
    poll_id = answer.poll_id
    try:
        questions = context.bot_data[poll_id]["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return
    selected_options = answer.option_ids
    answer_string = ""
    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " and "
        else:
            answer_string += questions[question_id]
    user_mention = mention_html(update.effective_user.id, update.effective_user.full_name)
    context.bot.send_message(context.bot_data[poll_id]["chat_id"],
                             "{} feels {}!".format(user_mention, answer_string),
                             parse_mode=ParseMode.HTML)
    context.bot_data[poll_id]["answers"] += 1
    # Close poll after three participants voted
    if context.bot_data[poll_id]["answers"] == 3:
        context.bot.stop_poll(context.bot_data[poll_id]["chat_id"],
                              context.bot_data[poll_id]["message_id"])


def quiz(update, context):
    """Send a predefined poll"""
    questions = ["1", "2", "4", "20"]
    message = update.effective_message.reply_poll("How many eggs do you need for a cake?",
                                                  questions, type=Poll.QUIZ, correct_option_id=2)
    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    payload = {message.poll.id: {"chat_id": update.effective_chat.id,
                                 "message_id": message.message_id}}
    context.bot_data.update(payload)


def receive_quiz_answer(update, context):
    """Close quiz after three participants took it"""
    # the bot can receive closed poll updates we don't care about
    if update.poll.is_closed:
        return
    if update.poll.total_voter_count == 3:
        try:
            quiz_data = context.bot_data[update.poll.id]
        # this means this poll answer update is from an old poll, we can't stop it then
        except KeyError:
            return
        context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])


def preview(update, context):
    """Ask user to create a poll and display a preview of it"""
    # using this without a type lets the user chooses what he wants (quiz or poll)
    button = [[KeyboardButton("Press me!", request_poll=KeyboardButtonPollType())]]
    message = "Press the button to let the bot generate a preview for your poll"
    # using one_time_keyboard to hide the keyboard
    update.effective_message.reply_text(message,
                                        reply_markup=ReplyKeyboardMarkup(button,
                                                                         one_time_keyboard=True))


def receive_poll(update, context):
    """On receiving polls, reply to it by a closed poll copying the received poll"""
    actual_poll = update.effective_message.poll
    # Only need to set the question and options, since all other parameters don't matter for
    # a closed poll
    update.effective_message.reply_poll(
        question=actual_poll.question,
        options=[o.text for o in actual_poll.options],
        # with is_closed true, the poll/quiz is immediately closed
        is_closed=True,
        reply_markup=ReplyKeyboardRemove()
    )


def help_handler(update, context):
    """Display a help message"""
    update.message.reply_text("Use /quiz, /poll or /preview to test this "
                              "bot.")


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1389342304:AAEIow_maY4lEdxIvJlHdINgympV6SwHID8", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('add_pushups_10', functools.partial(add_pushups, num_pushups=10)))
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
