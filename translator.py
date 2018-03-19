# -*- coding: cp1250 -*-

"""
This program can be used for translating texts in selected file
from one language to another (according to the user choice)
using customized database. I am using my own database called 'projects'.
Second part of the program enables manual translation of remaining
sentences in the file and updating the database.
"""

import re
import mysql.connector

'#User input (host and database are alternatively set by default)'
user = input('Input database user: ')
password = input('Input database password: ')
host = input('Input IP address of the database or press enter: ')
database = input('Input the name of the database or press enter: ')
file_name = input('Input the name of the file to be translated: ')
language = input('Language used in the file (eng or cz): ')

default_host = '127.0.0.1'
default_database = 'projects'
if not host:
    host = default_host
if not database:
    database = default_database

'#Connection with database'
db = mysql.connector.connect(user=user, password=password, host=host, database=database)

# db = mysql.connector.connect(user='', password='', host='127.0.0.1', database='projects')

cursor = db.cursor()

query = "SELECT cz, eng FROM dictionary"

'#Execution of query'
cursor.execute(query)

'#Encoding was necessary for opening files with czech characters'
file_input = open(file_name, 'r+', encoding='cp1250')
text = file_input.read()

'#Make list of sentences from the file'
sentences = re.split('[.?!;$]\s+', text)
while '' in sentences:
    sentences.remove('')

# t = re.sub('\n+', '\n', text)
# sentences1 = '\n'.join(sentences)
# s = sentences.strip('\n')

'#Make two lists of sentences from the database'
old_list = []
new_list = []

if language == 'eng':
    for (cz, eng) in cursor:
        old_list.append(eng)
        new_list.append(cz)
elif language == 'cz':    
    for (cz, eng) in cursor:
        old_list.append(cz)
        new_list.append(eng)

'#Translate the text and delete it in the list of sentences'
index = 0
for x in old_list:
    if x in text:
        text = re.sub(x, new_list[index], text)
        print('"%s" have been translated' % x)
    while x in sentences:
        sentences.remove(x)
    index += 1
    text = ''

'# Option for loading data to variables directly from database'
#for (cz, eng) in cursor:
#     if language == 'eng':
#         new = cz
#         old = eng
#     elif language == 'cz':
#         new = eng
#         old = cz
#     else:
#         print('Error! Wrong language choice!')
#         break
# 
#     if old in text:
#         text = re.sub(old, new, text)
#         print('In file: "%s" have been translated: %s' % (file_name, old))
#         while old in sentences:
#             sentences.remove(old)
    
'# re.sub proved more usable then replace'
# text = text.replace(y, x)

file_input.seek(0)
file_input.write(text)
file_input.close()

length = len(sentences)
print('The number of untranslated sentences left in the file is: %s.'
      % length)

'# Second part of the program, manual translating of texts and saving texts to the database'
manual_trans = input('Do you wish to translate remaining sentences manually and save them to database (y/n)? ')

if manual_trans == 'y':
#    distributor = input('Input name of the distributor: ')
#    producer = input('Input name of the producer: ')
    file_input_trans = open(file_name, 'r+', encoding='cp1250')
    text_trans = file_input_trans.read()

    for y in sentences:
        choice = input('Do you wish to translate "%s" and save it to database (y/n)? ' % y)
        if choice == 'y':
            new_trans = input('Input text for translation: ')
            text_trans = re.sub(y, new_trans, text_trans)
            print('"%s" have been translated' % y)

            if language == 'eng':
                export = "INSERT INTO dictionary (distributor, producer, eng, cz) VALUES (%s, %s, %s, %s)"
                data_export = (distributor, producer, y, new_trans)
            elif language == 'cz':
                export = "INSERT INTO dictionary (distributor, producer, eng, cz) VALUES (%s, %s, %s, %s)"
                data_export = (distributor, producer, new_trans, y)
            else:
                break

            cursor.execute(export, data_export)
            db.commit()
            while y in sentences:
                sentences.remove(y)
                      
    file_input_trans.seek(0)
    file_input_trans.write(text_trans)
    file_input_trans.close()

cursor.close()
db.close()

'#user can check executed changes and then terminate the program manually.'
input('For termination press Enter.')
