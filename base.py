import sqlite3
import random

class SQLighter:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def user_exists(self, email):#проверяем, есть ли пользователь в бд
        with self.connection:
            result = self.cursor.execute('SELECT * FROM User WHERE email = ?', (email,)).fetchall()
            return bool(len(result))

    def get_user(self, email): #получить user
        with self.connection:
            result = self.cursor.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchall()
            return(result[0])#1 обозначает номер столбца в таблице

    def get_pass(self, email): #получить user
        with self.connection:
            result = self.cursor.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchall()
            return(result[0][2])#1 обозначает номер столбца в таблице



    def add_user(self, id):#добавляем пользователя в бд
        with self.connection:
            return self.cursor.execute("INSERT INTO users (id) VALUES(?)", (id,))

    def get_users(self): #получаем список всех пользователей
        with self.connection:
            result = self.cursor.execute('SELECT * FROM users').fetchall()
            return result



    def tg(self, id_user,email):#обновить имя
         with self.connection:
             return self.cursor.execute("UPDATE user SET tg = ? WHERE email = ?", (id_user, email))
   


        
    def close(self):
        self.connection.close()
