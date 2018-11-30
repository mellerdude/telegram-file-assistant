import telegram
import subprocess
import os
import ntpath
import ctypes
import sys
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from os import listdir, walk
import argparse
import logging


"""
Using arguments to enter the program from cmd:
python tg.py --token yourtokenhere --dl_path yourdownloadpathhere
"""
parser = argparse.ArgumentParser(description="login to telegram bot")
parser.add_argument("-d", "--debug", help="debug the program", action="store_true")
parser.add_argument("-t", "--token", help="add your token to the program")
parser.add_argument("-p", "--dl_path", help="write your directory", default=r'c:\downloads')

args = parser.parse_args()
if args.debug:
    print("debugging")
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

TOKEN = args.token
DOWNLOADS_PATH = args.dl_path


class File(object):
    """
    Class functions to summon file later in command_cmd function.
    """
    name = ''
    __data__ = bytes()

    def read(self):
        return bytes(self.__data__)

    def write(self, data):
        self.__data__ += data

    def close(self):
        return

    def __init__(self, name, data):
        self.name = name
        self.__data__ = bytes(data, 'utf8')


def start(bot,update):
    bot.send_message(chat_id=update.message.chat_id, text="Welcome to the telegram file assistant!\n\n"
        "You can summon commands using the chat. The commands are:\n\n"
        "1. /dir - Get a list of your path folders and files. Changes the active directory to the path.\n"
        "Example - /dir c:\yourfolder\ - will make c:\yourfolder\ the active directory "
        "and will print you all the folders and files in this folder\n\n"
        "2. /get - Summon a file to the chat using its file directory.\n"
        "Example - /get c:\\myfile.ext will bring you the file\n\n"
        "3. Dragging a file to the chat and a caption will appear. "
        "Write nothing and it will be sent to your active directory.(default - c:\downloads)\n"
        "You can write in the caption a new file path, name, and extention and it will change accordingly.\n"
        "Example - c:\mynewfolder\mynewfilename.newext\n")


def hidden(path):
    # checks if a file is hidden
    hidden_mask = 2
    attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
    return attrs >= 0 and attrs & hidden_mask

 
def dir_cmd(bot,update):
    """
    cmd function. works in the bot like so:

    /cmd -yourcmdcommand-

    Returns in the bot your output
    """
    global DOWNLOADS_PATH
    x = update.message.text
    x = x[5:]
    dir_output = ''
    os.chdir(x)
    DOWNLOADS_PATH = x
    # changes the active directory to the input of /dir
    for (dirpath, dirnames, filenames) in os.walk(x):
        break
    dir_output += 'Active directory: ' + os.getcwd() + '\n\n'
    dir_output += 'Directory names:\n\n'
    for i in dirnames:
        if hidden(i) == False and not i.startswith('.') and not i.endswith('.sys'):
            dir_output += i + '\n'
    dir_output += '\nFile names:\n\n'
    for i in filenames:
        if hidden(i) == False and not i.startswith('.') and not i.endswith('.sys'):
            dir_output += i + '\n'
    if len(dir_output) > 4000:
        # if your output is longer than 4000 characters, the bot sends a file with the output to you.
        invalid_chars = ['\\', ':', '*', '<', '>', '|', '"', '?', '/']
        for c in invalid_chars:
            x = x.replace(c, '.')
        new = File(x, dir_output)
        bot.send_document(chat_id=update.message.chat_id, document=new)
    else:
        bot.send_message(chat_id=update.message.chat_id, text=dir_output)


def file_cmd(bot, update):
    """
    file function. can change your file name,path and extention with string in caption.

    1. Drag file to the bot.
    2. write in caption new path and name:
    c:\newfolder\newfilename.newfileext
    The bot transfers your file to the new folder
    """
    global DOWNLOADS_PATH
    f = update.message.document.get_file()
    if not update.message.caption:
        # if you write nothing in the caption - copies file to dl-path.
        d = os.path.join(DOWNLOADS_PATH, update.message.document.file_name)
        f.download(d)
        bot.send_message(chat_id=update.message.chat_id, text="Your file was moved to " + DOWNLOADS_PATH)
    else:
        os.rename(update.message.document.file_name, ntpath.basename(update.message.caption))
        d = os.path.join(os.path.dirname(update.message.caption), ntpath.basename(update.message.caption))
        f.download(d)
        bot.send_message(chat_id=update.message.chat_id, text="Your file's new path and name are" + update.message.caption)



def get_cmd(bot, update):
    """get function. works in the bot like so:

    /get c:\foldername\filename.fileext

    the bot sends you the file specified.
    """
    global DOWNLOADS_PATH
    x = update.message.text
    x = x[5:]
    bot.send_document(chat_id=update.message.chat_id, document=open(x, 'rb'))


if __name__ == '__main__':
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    dir_handler = CommandHandler('dir', dir_cmd)
    dispatcher.add_handler(dir_handler)

    get_handler = CommandHandler('get', get_cmd)
    dispatcher.add_handler(get_handler)

    generic_handler = MessageHandler(Filters.document, file_cmd)
    dispatcher.add_handler(generic_handler)

    start_handler = MessageHandler(Filters.all, start)
    dispatcher.add_handler(start_handler)

    q = updater.start_polling()
