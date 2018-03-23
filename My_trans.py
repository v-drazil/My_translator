# -*- coding: UTF-8 -*-

"""
This program can be used for translating texts in selected file
from one language to another (according to the user choice)
using customized database or csv file. I am using my own database called 'projects'.
For the purpose of testing I have been used the txt file as the database too.
Second part of the program enables manual translation of remaining
sentences in the file and updating the database.
"""

import re
import mysql.connector


class FileTranslate:

    def __init__(self, lang1_list, lang2_list):
        self.lang1_list = lang1_list
        self.lang2_list = lang2_list
        self.file_input = None
        self.text = None
        self.sentences = []
        self.db = None
        self.cursor = None
        self.txt_input = None

    def f_open(self):
        self.file_input = open(file_name, 'r+', encoding='UTF-8')
        self.text = self.file_input.read()
        self.sentences = re.split('[.?!;$]\s+', self.text)
        if '' in self.sentences:
            self.sentences.remove('')

    def txt_import(self):
        self.txt_input = open(txt_file, 'r+', encoding='UTF-8')
        self.db = self.txt_input.read()
        db_sentences = re.split('[;\n]', self.db)
        if '' in db_sentences:
            db_sentences.remove('')

        index = 0
        for x in db_sentences:
            self.lang1_list.append(x)
            db_sentences.remove(x)
            self.lang2_list.append(db_sentences[index])
            index += 1

    def sql_import(self):
        self.db = mysql.connector.connect(user=user, password=password, host=host, database=database)
        self.cursor = self.db.cursor()
        query = "SELECT cz, eng FROM dictionary"
        self.cursor.execute(query)

        for (cz, eng) in self.cursor:
            self.lang1_list.append(cz)
            self.lang2_list.append(eng)

    def f_translate(self):
        if language == 'cz':
            index = 0
            for x in self.lang1_list:
                if x in self.text:
                    self.text = re.sub(x, self.lang2_list[index], self.text)
                    print('"%s" have been translated' % x)
                    while x in self.sentences:
                        self.sentences.remove(x)
                index += 1
        elif language == 'eng':
            index = 0
            for x in self.lang2_list:
                if x in self.text:
                    self.text = re.sub(x, self.lang1_list[index], self.text)
                    print('"%s" have been translated' % x)
                    while x in self.sentences:
                        self.sentences.remove(x)
                index += 1
        self.file_input.seek(0)
        self.file_input.write(self.text)
        length = len(self.sentences)
        print('The number of untranslated sentences left in the file is: %s.'
              % length)

    def f_manual_trans(self):
        manual_trans = input('Do you wish to translate remaining sentences manually and save them to database (y/n)? ')
        if manual_trans == 'y':
            for y in self.sentences:
                choice = input('Do you wish to translate "%s" and save it to database (y/n)? ' % y)
                if choice == 'y':
                    new_trans = input('Input text for translation: ')
                    self.text = re.sub(y, new_trans, self.text)
                    print('"%s" have been translated and saved.' % y)
                    if database_choice(database_file):
                        ex = ''
                        data_ex = ''
                        if language == 'eng':
                            ex = "INSERT INTO dictionary (cz, eng) VALUES (%s, %s)"
                            data_ex = (new_trans, y)
                        elif language == 'cz':
                            ex = "INSERT INTO dictionary (cz, eng) VALUES (%s, %s)"
                            data_ex = (y, new_trans)
                        self.cursor.execute(ex, data_ex)
                        self.db.commit()
                    else:
                        txt_ex_list = []
                        if language == 'eng':
                            txt_ex_list.append(new_trans)
                            txt_ex_list.append(y)
                            txt_ex = ('\n' + (';'.join(txt_ex_list)))
                            self.txt_input.write(txt_ex)
                        elif language == 'cz':
                            txt_ex_list.append(y)
                            txt_ex_list.append(new_trans)
                            txt_ex = ('\n'+(';'.join(txt_ex_list)))
                            self.txt_input.write(txt_ex)
                else:
                    continue
            self.file_input.seek(0)
            self.file_input.write(self.text)

    def f_close(self):
        # self.file_input.seek(0)
        # self.file_input.write(self.text)
        if database_choice(database_file):
            self.cursor.close()
            self.db.close()
        else:
            self.txt_input.close()
        self.file_input.close()

        '#user can check executed changes and then terminate the program manually.'
        input('For termination press Enter.')


def database_choice(db_choice):
    bad_choice = True
    while bad_choice:
        if db_choice == '1':
            return True
        elif db_choice == '2':
            return False
        else:
            print(u"You pressed a wrong key.")
            raise ValueError


'#End of class and function definition'

'#User input using database_choice function'
print('Select file format to be used as database for translation.')
database_file = input('For SQL please press "1", for TXT please press "2". Then confirm by enter. ')

'#Global variables'
cz_list = []
eng_list = []
final = FileTranslate(cz_list, eng_list)

if database_choice(database_file):
    user = input('Input database user: ')
    password = input('Input database password: ')
    host = input('Input IP address of the database or press enter: ')
    database = input('Input the name of the database or press enter: ')
    default_host = '127.0.0.1'
    default_database = 'projects'
    if not host:
        host = default_host
    if not database:
        database = default_database
    file_name = input('Input the name of the file to be translated: ')
    language = input('Language used in the file (eng or cz): ')

    '#Database import using function from the Class'
    final.sql_import()
else:
    txt_file = input('Input the name of the file to be used as the database: ')
    file_name = input('Input the name of the file to be translated: ')
    language = input('Language used in the file (eng or cz): ')

    '#txt file import using function from the Class'
    final.txt_import()

'#File processing using functions from the Class'
final.f_open()
final.f_translate()
final.f_manual_trans()
final.f_close()
