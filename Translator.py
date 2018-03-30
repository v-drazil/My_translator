# -*- coding: UTF-8 -*-

"""
This program can be used for translating texts in selected file
from one language to another language using sql or txt database.
Language is recognised automatically according to the database.
Second part of the program enables manual translation of remaining
sentences in the file and updating the database.
"""

import re
import mysql.connector
import argparse


class FileTranslate:

    def __init__(self, cz_list, eng_list):
        self.cz_list = cz_list
        self.eng_list = eng_list
        self.file_input = None
        self.text = None
        self.sentences = []
        self.db = None
        self.cursor = None
        self.txt_input = None
        self.language = None

    def f_open(self):
        self.file_input = open(file_name, 'r', encoding='UTF-8')
        self.text = self.file_input.read()
        self.file_input.close()
        self.text = re.sub(' +', ' ', self.text)
        self.sentences = re.split('[.?!;\n]\s+|\n', self.text)
        for item in self.sentences:
            short = len(item)
            if short <= 4:
                self.sentences.remove(item)
        self.sentences = set(self.sentences)

    def txt_import(self):
        self.txt_input = open(txt_file, 'r', encoding='UTF-8')
        self.db = self.txt_input.read()
        self.txt_input.close()
        db_sentences = re.split('[;\n]', self.db)
        if '' in db_sentences:
            db_sentences.remove('')

        index = 0
        for x in db_sentences:
            self.cz_list.append(x)
            db_sentences.remove(x)
            self.eng_list.append(db_sentences[index])
            index += 1

    def sql_import(self):
        self.db = mysql.connector.connect(user=user, password=password, host=host, database=database)
        self.cursor = self.db.cursor()
        query = "SELECT cz, eng FROM dictionary"
        self.cursor.execute(query)

        for (cz, eng) in self.cursor:
            self.cz_list.append(cz)
            self.eng_list.append(eng)

    def f_translate(self):
        print('-------------------------')
        sentences = list(self.sentences)
        for item in self.sentences:
            if item in self.cz_list:
                position = self.cz_list.index(item)
                self.text = re.sub(item, self.eng_list[position], self.text)
                print('"{}" have been translated'.format(item))
                sentences.remove(item)
                self.language = 'cz'
            elif item in self.eng_list:
                position = self.eng_list.index(item)
                self.text = re.sub(item, self.cz_list[position], self.text)
                print('"{}" have been translated'.format(item))
                sentences.remove(item)
                self.language = 'eng'
        self.sentences = set(sentences)
        self.file_input = open(file_name, 'w', encoding='UTF-8')
        self.file_input.write(self.text)
        self.file_input.close()
        length = len(self.sentences)
        print('The number of untranslated sentences left in the file is: {}.'.format(length))

    def f_manual_trans(self):
        manual_trans = input(
            'Do you wish to translate remaining sentences manually and save them to the database (y/n)? ')
        if manual_trans == 'y':
            for item in self.sentences:
                choice = input('Do you wish to translate "{}" and save it to the database (y/n)? '.format(item))
                if choice == 'y':
                    new_trans = input('Input text for translation: ')
                    self.text = re.sub(item, new_trans, self.text)
                    print('"{}" have been translated and saved.'.format(item))
                    if database_choice(database_file):
                        ex = ''
                        data_ex = ''
                        if self.language == 'eng':
                            ex = "INSERT INTO dictionary (cz, eng) VALUES (%s, %s)"
                            data_ex = (new_trans, item)
                        elif self.language == 'cz':
                            ex = "INSERT INTO dictionary (cz, eng) VALUES (%s, %s)"
                            data_ex = (item, new_trans)
                        self.cursor.execute(ex, data_ex)
                        self.db.commit()
                    else:
                        txt_ex_list = []
                        if self.language == 'eng':
                            txt_ex_list.append(new_trans)
                            txt_ex_list.append(item)
                            txt_ex = (';'.join(txt_ex_list) + '\n')
                            self.txt_input = open(txt_file, 'a', encoding='UTF-8')
                            self.txt_input.write(txt_ex)
                            self.txt_input.close()
                        elif self.language == 'cz':
                            txt_ex_list.append(item)
                            txt_ex_list.append(new_trans)
                            txt_ex = (';'.join(txt_ex_list) + '\n')
                            self.txt_input = open(txt_file, 'a', encoding='UTF-8')
                            self.txt_input.write(txt_ex)
                            self.txt_input.close()

            self.file_input = open(file_name, 'w', encoding='UTF-8')
            self.file_input.write(self.text)
            self.file_input.close()


def database_choice(db_choice):
    bad_choice = True
    while bad_choice:
        if db_choice == '1':
            return True
        else:
            return False


'#End of class and function definition'

parser = argparse.ArgumentParser()
parser.parse_args()

'#Global variables'
list_cz = []
list_eng = []
final = FileTranslate(list_cz, list_eng)

'#User input using database_choice function'
print('Select file format to be used as database for translation.')
database_file = input('For SQL please press "1", for TXT please press random key or enter: ')

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

    '#sql database import using function from the Class'
    final.sql_import()
else:
    txt_file = input('Input the name of the file to be used as the database or press enter: ')
    file_name = input('Input the name of the file to be translated or press enter: ')
    default_txt_file = 'dictionary.txt'
    default_file_name = 'testfile.txt'
    if not txt_file:
        txt_file = default_txt_file
    if not file_name:
        file_name = default_file_name
    '#txt database import using function from the Class'
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
