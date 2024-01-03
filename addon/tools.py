# -*- coding: utf-8 -*-
#
# Portions of this code are derived from the copyrighted works of:
#    Damien Elmes <anki@ichi2.net>
#
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
#
# This project is hosted on GitHub: https://github.com/tarix/anki-toolbox

from aqt import mw
from aqt.qt import *
from aqt.utils import tooltip

# ----------------------------------------------------------------------------

import csv

def menuAddKLCData():

    did = mw.col.decks.id('日本語::漢字')
    mid = mw.col.models.by_name('Japanese Kanji')

    kanji_id = mw.col.models.field_map(mid).get('Kanji', None)[0] 
    klcentry_id = mw.col.models.field_map(mid).get('KLCEntry', None)[0] 
    klckeyword_id = mw.col.models.field_map(mid).get('KLCKeyword', None)[0] 

    try:
        with open('data/klc.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)  # Skip the header row if it exists
            for row in csv_reader:
                csv_kanji = row[1]
                csv_klcentry = row[2]
                csv_klckeyword = row[5]
                #print('kanji: ', csv_kanji, ' klcentry: ', csv_klcentry, ' klckeyword: ', csv_klckeyword)
                # Get the ID of the note with the specified field value
                note_id = mw.col.find_notes(f'Kanji:"{csv_kanji}"')
                if note_id:
                    # Retrieve the note using the note ID
                    note = mw.col.get_note(note_id[0])
                    # update all of the note data
                    note.fields[klcentry_id] = csv_klcentry
                    note.fields[klckeyword_id] = csv_klckeyword
                    note.add_tag('klc')
                    # save the note
                    mw.col.update_note(note)
                else:
                    #print('not found: kanji: ', csv_kanji, ' klcentry: ', csv_klcentry, ' klckeyword: ', csv_klckeyword)
                    # create a new note
                    note = mw.col.new_note(mid)
                    # add all of the note data
                    note['Kanji'] = csv_kanji
                    note['KLCEntry'] = csv_klcentry
                    note['KLCKeyword'] = csv_klckeyword
                    note.add_tag('klc')
                    # add the note
                    mw.col.add_note(note, did)                    
            mw.reset()
    except FileNotFoundError:
        print(f"Error: File klc.csv not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def initAddKLCData():
    # add the menu option
    mw.form.action = QAction('ATK: Add KLC Data', mw)
    mw.form.action.setEnabled(True)
    mw.form.action.triggered.connect(menuAddKLCData)
    mw.form.menuTools.addAction(mw.form.action)

# -----------------------------------------------------------------------------

def init():
    mw.form.menuTools.addSeparator()
    initAddKLCData()

init()
