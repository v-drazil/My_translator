# -*- coding: UTF-8 -*-

import re
import argparse


class FileTranslate:

    def __init__(self, cz_list, eng_list):
        self.cz_list = cz_list
        self.eng_list = eng_list
        self.text = None
        self.sentences = []
        self.db = None
        self.cursor = None

    def f_open(self):
        with open(file_name, 'r', encoding='UTF-8') as file_input:
            self.text = file_input.read()
        self.text = re.sub('\s', ' ', self.text)
        self.text = re.sub(' +', ' ', self.text)
        self.sentences = re.split('[.?!;:] ', self.text)
        for item in self.sentences:
            short = len(item)
            if short <= 4:
                self.sentences.remove(item)
        self.sentences = set(self.sentences)

    def txt_import(self):
        with open(txt_file, 'r', encoding='UTF-8') as txt_input:
            self.db = txt_input.read()
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
        if args.database_choice:
            self.cursor.close()
            self.db.close()

    def f_translate(self):
        print('-------------------------')
        sentences = list(self.sentences)
        for item in self.sentences:
            if args.language_choice:
                if item in self.cz_list:
                    position = self.cz_list.index(item)
                    self.text = re.sub(item, self.eng_list[position], self.text)
                    print('translated: "{}"'.format(item))
                    sentences.remove(item)
            else:
                if item in self.eng_list:
                    position = self.eng_list.index(item)
                    self.text = re.sub(item, self.cz_list[position], self.text)
                    print('translated: "{}"'.format(item))
                    sentences.remove(item)
        self.sentences = set(sentences)

    def f_write(self):
        self.text = self.text.replace('. ', '.<x>')
        self.text = self.text.replace('! ', '!<x>')
        self.text = self.text.replace('? ', '?<x>')
        self.text = self.text.replace('; ', ';<x>')
        self.text = self.text.replace(': ', ':<x>')
        text = re.split('<x>', self.text)
        text = '\n'.join(text)
        with open(file_name, 'w', encoding='UTF-8') as file_input:
            print(text, file=file_input)

    def f_manual_trans(self):
        length = len(self.sentences)
        print('The number of untranslated sentences left in the file is: {}.'.format(length))
        manual_trans = input('Do you wish to translate and save remaining sentences manually (y/n)? ')
        if manual_trans == 'y':
            if args.database_choice:
                self.db = mysql.connector.connect(user=user, password=password, host=host, database=database)
                self.cursor = self.db.cursor()
            for item in self.sentences:
                choice = input('Do you wish to translate "{}" and save it to the database (y/n)? '.format(item))
                if choice == 'y':
                    new_trans = input('Input text for translation: ')
                    self.text = re.sub(item, new_trans, self.text)
                    print('Translated and saved: "{}"'.format(item))
                    if args.database_choice:
                        if args.language_choice:
                            ex = "INSERT INTO dictionary (cz, eng) VALUES (%s, %s)"
                            data_ex = (item, new_trans)
                        else:
                            ex = "INSERT INTO dictionary (cz, eng) VALUES (%s, %s)"
                            data_ex = (new_trans, item)
                        self.cursor.execute(ex, data_ex)
                        self.db.commit()
                    else:
                        txt_ex_list = []
                        if args.language_choice:
                            txt_ex_list.append(item)
                            txt_ex_list.append(new_trans)
                            txt_ex = (';'.join(txt_ex_list))
                            with open(txt_file, 'a', encoding='UTF-8') as txt_input:
                                print(txt_ex, file=txt_input)
                        else:
                            txt_ex_list.append(new_trans)
                            txt_ex_list.append(item)
                            txt_ex = (';'.join(txt_ex_list))
                            with open(txt_file, 'a', encoding='UTF-8') as txt_input:
                                print(txt_ex, file=txt_input)

            if args.database_choice:
                self.cursor.close()
                self.db.close()


'#End of class and function definition'

parser = argparse.ArgumentParser(description="""
This program can be used for translating texts in selected file
from one language to another language using sql or txt database.
Database file, file designated for translation and its language are
pre-set, but user can change default setting by following arguments.
Second part of the program enables manual translation of remaining
sentences in the file and updating the database.
""")

parser.add_argument('-a', action='store_true', default=False,
                    dest='database_choice',
                    help='Set switch to true for using sql database instead of txt database.')
parser.add_argument('-b', action='store_true', default=False,
                    dest='language_choice',
                    help='Set switch to true for translating of sentences from czech to english language'
                    '(default: translating of sentences from english to czech language.')
parser.add_argument('-d', action='store', default='dictionary.txt',
                    dest='txt_file',
                    help='Store the name of the file to be used as the txt database (default: dictionary.txt).')
parser.add_argument('-f', action='store', default='testfile.txt',
                    dest='file_name',
                    help='Store the name of the file to be translated (default: testfile.txt).')
parser.add_argument('--version', action='version', version='%(prog)s 1.10')

args = parser.parse_args()

'#Import mysql.connector according to the argument from command line'
if args.database_choice:
    import mysql.connector

'#Global variables'
list_cz = []
list_eng = []
final = FileTranslate(list_cz, list_eng)


if args.database_choice:
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
    file_name = args.file_name

    '#sql database import using function from the Class'
    final.sql_import()
else:
    txt_file = args.txt_file
    file_name = args.file_name
    '#txt database import using function from the Class'
    final.txt_import()

'#File processing using functions from the Class'
final.f_open()
final.f_translate()
final.f_manual_trans()
final.f_write()
