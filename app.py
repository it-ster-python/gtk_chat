import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ui import chat


if __name__ == "__main__":
    win = chat.ChatWindow()
    win.connect("destroy", win.on_close)
    # win.show_all()
    Gtk.main()
