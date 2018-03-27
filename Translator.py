
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
import argparse

parser = argparse.ArgumentParser()
parser.parse_args()


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
        # with open(file_name, encoding='UTF-8') as f:
        #     self.text = f.read()
        self.file_input = open(file_name, 'r', encoding='UTF-8')
        self.text = self.file_input.read()
        self.file_input.close()
        self.sentences = re.split('[.?!;$]\s+', self.text)
        if '' in self.sentences:
            self.sentences.remove('')

    def txt_import(self):
        # with open(txt_file, encoding='UTF-8') as f:
        #     self.db = f.read()
        self.txt_input = open(txt_file, 'r', encoding='UTF-8')
        self.db = self.txt_input.read()
        self.txt_input.close()
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
            for item in self.lang1_list:
                if item in self.text:
                    self.text = re.sub(item, self.lang2_list[index], self.text)
                    print('"{}" have been translated' .format(item))
                    while item in self.sentences:
                        self.sentences.remove(item)
                index += 1
        elif language == 'eng':
            index = 0
            for item in self.lang2_list:
                if item in self.text:
                    self.text = re.sub(item, self.lang1_list[index], self.text)
                    print('"{}" have been translated' .format(item))
                    while item in self.sentences:
                        self.sentences.remove(item)
                index += 1
        # with open(file_name, encoding='UTF-8') as f:
        #     f.write(self.text)
        self.file_input = open(file_name, 'w', encoding='UTF-8')
        self.file_input.write(self.text)
        self.file_input.close()

        length = len(self.sentences)
        print('The number of untranslated sentences left in the file is: {}.' .format(length))

    def f_manual_trans(self):
        manual_trans = input('Do you wish to translate remaining sentences manually and save them to database (y/n)? ')
        if manual_trans == 'y':
            for item in self.sentences:
                choice = input('Do you wish to translate "{}" and save it to database (y/n)? ' .format(item))
                if choice == 'y':
                    new_trans = input('Input text for translation: ')
                    self.text = re.sub(item, new_trans, self.text)
                    print('"{}" have been translated and saved.' .format(item))
                    if database_choice(database_file):
                        ex = ''
                        data_ex = ''
                        if language == 'eng':
                            ex = "INSERT INTO dictionary (cz, eng) VALUES (%s, %s)"
                            data_ex = (new_trans, item)
                        elif language == 'cz':
                            ex = "INSERT INTO dictionary (cz, eng) VALUES (%s, %s)"
                            data_ex = (item, new_trans)
                        self.cursor.execute(ex, data_ex)
                        self.db.commit()
                    else:
                        txt_ex_list = []
                        if language == 'eng':
                            txt_ex_list.append(new_trans)
                            txt_ex_list.append(item)
                            txt_ex = (';'.join(txt_ex_list)+'\n')
                            self.txt_input = open(txt_file, 'a', encoding='UTF-8')
                            self.txt_input.write(txt_ex)
                            self.txt_input.close()
                        elif language == 'cz':
                            txt_ex_list.append(item)
                            txt_ex_list.append(new_trans)
                            txt_ex = (';'.join(txt_ex_list)+'\n')
                            self.txt_input = open(txt_file, 'a', encoding='UTF-8')
                            self.txt_input.write(txt_ex)
                            self.txt_input.close()
                else:
                    continue
            self.file_input = open(file_name, 'w', encoding='UTF-8')
            self.file_input.write(self.text)
            self.file_input.close()


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

if database_choice(database_file):
    self.cursor.close()
    self.db.close()

'#user can check executed changes and then terminate the program manually.'
input('For termination press Enter.')
