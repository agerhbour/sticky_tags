from aqt.utils import showInfo, qconnect, tr
from aqt.qt import QMenu

def fuko(id):
    showInfo(f"ID: {id}")

def add_fuko(m: QMenu, id: int):
    a = m.addAction("Fuko")
    qconnect(a.triggered, lambda b, did=id: fuko(id))

from aqt import gui_hooks
gui_hooks.deck_browser_will_show_options_menu.append(add_fuko)