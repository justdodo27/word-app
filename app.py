import sqlite3
import os
import bcrypt


class User():
    def __init__(self, username) -> None:
        self.username = username
        self.words = None
    
    def load_words(self, filename: str): # load word list
        pass

    def create_log(self): # create new log
        pass

    def load_log(self): # load previous logs (if exist)
        pass

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

    while True:
        clear_CLI()
        option = input('Type command: ')

        if option == '':
            pass
        elif option == 'create':
            username = input('Type your username: ')
            password = input('Type password: ')
            repeat = input('Please repeat your password: ')
            if password == repeat:
                if (msg := create_user(username, password)) == True:
                    input('Account successfully created!')
                else:
                    input(msg)
            else:
                input('Your passwords don\'t match!')
        elif option == 'login':
            username = input('Type your username: ')
            password = input('Type password: ')
            if user := login(username, password):
                input(user)
            else:
                input('Wrong username or password!')
        else:
            print('Wrong option! Type help to list available commands.')