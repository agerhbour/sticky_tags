from aqt.utils import getText, qconnect, tr
from aqt.qt import QMenu
from aqt import mw, deckchooser

### This is such a massive hack before the add_cards_did_change_deck hook is available and since no matter what I try I cannot monkey patch the instance method.
after_choose_deck = []

def decorate(fn):
    def f(self):
        x=fn(self)
        for g in after_choose_deck:
            g()
        return x

    return f

deckchooser.DeckChooser.choose_deck = decorate(deckchooser.DeckChooser.choose_deck)
### END HACK

def sticky_tags(deck_id):
    deck = mw.col.decks.get(deck_id)
    new_stickies, succeeded = getText(f"Sticky tags for deck {deck['name']}: ", default=" ".join(get_sticky_tags(deck_id)))
    if succeeded:
        set_sticky_tags(deck_id, new_stickies.split(" "))


def add_sticky_tags_menu(m: QMenu, id: int):
    a = m.addAction("Sticky tags")
    qconnect(a.triggered, lambda b, did=id: sticky_tags(id))

from aqt import gui_hooks
gui_hooks.deck_browser_will_show_options_menu.append(add_sticky_tags_menu)

def get_sticky_tags(deck_id):
    deck = mw.col.decks.get(deck_id)
    config = mw.addonManager.getConfig(__name__)
    return config.get(deck['name'], [])

def set_sticky_tags(deck_id, stickies):
    deck = mw.col.decks.get(deck_id)
    config = mw.addonManager.getConfig(__name__)
    config[deck['name']] = stickies
    mw.addonManager.writeConfig(__name__, config)

from aqt import addcards
from types import MethodType
from anki.hooks import wrap

def on_add_cards_did_init(cards : addcards.AddCards):
    deck_id = cards.deck_chooser.selected_deck_id
    def update_tags_for_id(deck_id):
        sticky_tags = get_sticky_tags(deck_id)
        cards.editor.tags.setText(" ".join(sticky_tags))
        cards.editor.on_tag_focus_lost()
    update_tags_for_id(deck_id)
    def f():
        update_tags_for_id(cards.deck_chooser.selected_deck_id)
    after_choose_deck.clear()
    after_choose_deck.append(f)

    
gui_hooks.add_cards_did_init.append(on_add_cards_did_init)
