import sqlite3
import os
import bcrypt
import datetime as dt
from random import shuffle

class User():
    def __init__(self, username) -> None:
        self.username = username
        self.words = None
        self.current_list = None
    
    def load_words(self, filename: str): # load word list
        if filename[-4:] != '.txt':
            filename += '.txt'
        try:
            with open(f'./words/{filename}', 'r', encoding='UTF-8') as f:
                self.words = list()
                for line in f:
                    word = line.split(';')
                    self.words.append({'id': word[0], 'eng': word[1], 'pl': word[2], 'date': None})
                print(f'Successfully loaded {len(self.words)} words!')
                self.current_list = filename[:-4]
                self.load_log()
        except:
            print('Wrong! This word list don\'t exist.')
            print('To list available words lists type \'list\' when asked for command.')
    def create_log(self): # create new log
        with open(f'./logs/{self.username}-{self.current_list}-{dt.date.today()}.txt', 'w') as f:
            for word in self.words:
                f.write(f"{word['id']};{word['date']}\n")
        print('Created new log!')

    def play(self): # play a game
        today = dt.date.today()
        words_idx = []
        for idx in range(len(self.words)):
            if self.words[idx]['date'] is None or (today - self.words[idx]['date']).days >= 0:
                words_idx.append(idx)
        if len(words_idx) == 0:
            print('You don\'t need to play the game.')
        else:
            clear_CLI()
            shuffle(words_idx) # randomize the words
            for count, idx in enumerate(words_idx):
                word = self.words[idx]
                print(f"Word {count+1} of {len(words_idx)}")
                print(f"English: { word['eng'] }")
                polish = input(f"Polish: ")
                if polish == word['pl'][:-1]:
                    self.words[idx]['date'] = today + dt.timedelta(days=7)
                else:
                    self.words[idx]['date'] = today
                clear_CLI()
            self.create_log()

    def load_log(self): # load previous logs (if exist)
        files = os.listdir('./logs')
        count = 0
        for file in files:
            if 'txt' == file[-3:] and f'{self.username}-{self.current_list}-' in file:
                print(f'{file[:-4]}')
                count += 1
                
        print(f'Found {count} logs')

def init_db():
    with sqlite3.connect('users.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL)''')
        con.commit()

def create_user(username: str, password: str):
    hashed = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(13))
    with sqlite3.connect('users.db') as con:
        cur = con.cursor()
        try:
            cur.execute('''INSERT INTO users (username, password)
            VALUES (?, ?)''', (username, hashed))
            con.commit()
        except sqlite3.Error as er:
            return ' '.join(er.args)
        return True

def login(username: str, password: str):
    with sqlite3.connect('users.db') as con:
        cur = con.cursor()
        cur.execute('''SELECT * FROM users WHERE username = ?''', (username,))
        user = cur.fetchone()
        if user and bcrypt.checkpw(password.encode('utf8'), user[2]):
            return user
        else:
            return False

def clear_CLI():
    command = 'clear'
    if os.name in ('nt', 'dos'):
        command = 'cls'
    os.system(command)

if __name__ == '__main__':
    init_db()

    player = None

    while True:
        clear_CLI()
        option = input('Type command: ')

        if option == 'help': # display available commands
            print('Help...')
        elif option == 'list' and player: # list available words lists
            files = os.listdir('./words')
            print('Available words lists:')
            for idx, file in enumerate(files):
                if 'txt' == file[-3:]:
                    print(f'{idx+1}. {file[:-4]}')
        elif option == 'load' and player: # load words list 
            filename = input('Type filename of word list located in words folder: ')
            player.load_words(filename)
        elif option == 'play' and player and player.words:
            player.play()
        elif option == 'create' and player is None: # create player
            username = input('Type your username: ')
            password = input('Type password: ')
            repeat = input('Please repeat your password: ')
            if password == repeat:
                if (msg := create_user(username, password)) == True:
                    print('Account successfully created!')
                else:
                    print(msg)
            else:
                print('Your passwords don\'t match!')
        elif option == 'login' and player is None: # login to existing user/player account
            username = input('Type your username: ')
            password = input('Type password: ')
            if user := login(username, password):
                player = User(user[1])
                print('Successfully loged in!')
            else:
                print('Wrong username or password!')
        else:
            print('Wrong option! Type help to list available commands.')
        input('Press enter to continue...')