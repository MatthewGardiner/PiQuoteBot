from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import sqlite3
import random
import re
import time
import threading
QUEUE_DELAY = 2.0
messageQ = {}

def seven(bot, update):
    if re.match("^.*(7|(S|s)even(!*)).*$", update.message.text):
        add_message_to_queue(update.message, "Seven!")

def random_quote(bot, update):
    if len(quote_cache) > 0:
        add_message_to_queue(update.message, random.choice(quote_cache))

def message_queuer():
    while True:
        if len(messageQ) > 0:
            random_idx = random.randint(0, len(messageQ) - 1)
            msg_parent = messageQ.keys()[random_idx]
            msg_content = messageQ.pop(msg_parent)
            msg_parent.reply_text(msg_content)
            time.sleep(QUEUE_DELAY)

def add_message_to_queue(msg_parent, msg_content):
    messageQ[msg_parent] = msg_content
 
def create_schema():
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS quotes (text)')
    conn.commit()

def save_to_quotedb(message):
    c = conn.cursor()
    c.execute('INSERT INTO quotes VALUES (?)', (message, ))
    conn.commit()

def load_quotedb():
    c = conn.cursor()
    c.execute('SELECT * FROM quotes')
    for quote in c.fetchall():
        quote_cache.append(quote[0])

def quote(bot, update):
    try:
        quote = ' '.join(update.message.text.split(' ')[1:])
    except IndexError:
        add_to_message_queue(update.message, 'No quote specified!')
        return
    if quote in quote_cache:
    	add_to_message_queue(update.message, 'That quote is already added')
	return
    save_to_quotedb(quote)
    quote_cache.append(quote)
    add_to_message_queue(update.message, "Quote added!")

if __name__ == "__main__":
    quote_cache = []
    conn = sqlite3.connect('quotes.db', check_same_thread=False)
    msgThread = threading.Thread(target=message_queuer)#
    msgThread.start()
    create_schema()
    load_quotedb()
    updater = Updater(os.environ['TELEGRAM_API_KEY'])
    updater.dispatcher.add_handler(CommandHandler("quote", quote))
    updater.dispatcher.add_handler(CommandHandler("random_quote", random_quote))
    updater.dispatcher.add_handler(MessageHandler([Filters.text], seven))
    updater.start_polling()
    updater.idle()
