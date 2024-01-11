# -*- coding: utf-8 -*-
#
# Portions of this code are derived from the copyrighted works of:
#    Damien Elmes <anki@ichi2.net>
#
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
#
# This project is hosted on GitHub: https://github.com/tarix/anki-toolbox

import csv, importlib, re

from aqt import mw
from aqt.qt import *
from aqt.utils import tooltip
from anki.utils import strip_html

# ----------------------------------------------------------------------------

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
    mw.form.action = QAction('ATB: Add KLC Data', mw)
    mw.form.action.setEnabled(True)
    mw.form.action.triggered.connect(menuAddKLCData)
    mw.form.menuTools.addAction(mw.form.action)

# -----------------------------------------------------------------------------

_mecab = None

# FIXME: convert to more updated mecab
def mecab():
    global _mecab
    if _mecab == None:
        # import the japanese plugin mecab module
        reading = importlib.import_module('3918629684.reading')
        try:
            # create our controller and initialize it
            _mecab = reading.MecabController()
            _mecab.setup()
        except:
            _mecab = None
    return _mecab

def extract_vocab(notes):
    # regex to match the vocab
    pattern1 = r'^(.+?)：'
    pattern2 = r'^(.+?):'
    # Use re.MULTILINE to enable matching at the start of each line
    match = re.search(pattern1, notes, flags=re.MULTILINE)
    if match == None:
        match = re.search(pattern2, notes, flags=re.MULTILINE)
    # see if we found the vocab
    if match:
        vocab = match.group(1).strip()
        return vocab
    else:
        return None

def generate_cloze( vocab, ruby ):
    if vocab == ruby:
        return f'{{{{c1::{vocab}::{vocab}}}}}'
    else:
        return f'{{{{c1:: {ruby}::{vocab}}}}}'

def menuFixJalupDeck():
    print('Menu: Fix Jalup Deck')
    notes = mw.col.find_notes('deck:"Jalup::2. Intermediate"')
    for i, nid in enumerate(notes):
        # get the next note
        note = mw.col.get_note(nid)
        # calculate the stage and card number
        stage = int(i / 250) + 1
        cnum = i + 1
        # check if we are already processed
        text = strip_html( note['Expression'] )
        # grab the vocab word
        vocab = extract_vocab( strip_html(note['Meaning']) )
        if not vocab == None:
            # grab the vocab reading
            ruby = mecab().reading( vocab )
            # generate the cloze
            cloze = generate_cloze( vocab, ruby )
            # replace and update the text
            text = str.replace( text, vocab, cloze )
        else:
            # tag this note as not clozed
            note.add_tag('ja-jalup-nocloze')
        # update the note
        note['Text'] = text
        note['Source'] = f'Jalup Intermediate Stage {stage} #{cnum}'
        # save the note changes
        mw.col.update_note(note)

def initFixJalupDeck():
    # add the menu option
    mw.form.action = QAction('ATB: Fix Jalup Deck', mw)
    mw.form.action.setEnabled(True)
    mw.form.action.triggered.connect(menuFixJalupDeck)
    mw.form.menuTools.addAction(mw.form.action)

# -----------------------------------------------------------------------------

def init():
    mw.form.menuTools.addSeparator()
    initAddKLCData()
    initFixJalupDeck()

init()
