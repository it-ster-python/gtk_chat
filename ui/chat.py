import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ui import login
import redis
import socket
import select
import json
import os


HOST = "127.0.0.1"
PORT = 5000


class ChatWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Mega Chat | Chat")
        # self.login_win = login.LoginWindow(self.regy_date)
        # self.login_win.show_all()
        self.connection = None
        self.__interfase()


    def __interfase(self):
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(800, 600)

        master_box = Gtk.Box()
        self.add(master_box)

        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_box.set_size_request(200, -1)
        master_box.pack_start(left_box, False, True, 0)

        center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        master_box.pack_start(center_box, True, True, 0)

        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        right_box.set_size_request(200, -1)
        master_box.pack_start(right_box, False, True, 0)

        avatar = Gtk.Image()
        avatar.set_from_file(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "gtk_chat_avatar.png"
            )
        )
        left_box.pack_start(avatar, False, True, 5)

        user_label = Gtk.Label(label="User name")
        # Проверить растягивание
        left_box.pack_start(user_label, False, True, 5)

        message_entry = Gtk.Entry()
        # Проверить растягивание
        center_box.pack_start(message_entry, False, True, 5)

        favorit_label = Gtk.Label(label="Избранное")
        # Проверить растягивание
        right_box.pack_start(favorit_label, False, True, 5)

        self.show_all()

    def regy_date(self):
        self.login.hide()
        storage = redis.StrictRedis()
        try:
            self.login = storage.get("login")
            self.password = storage.get("password")
        except redis.RedisError:
            print("Данных почему то не!")
            Gtk.main_quit()
        else:
            self.__create_conntetion()
            self.show_all()

    def __create_conntetion(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connection.connect((HOST, PORT))
        data = json.dumps({"login": self.login, "password": self.password})
        self.connection.send(data.encode("utf-8"))
        result = self.connection.recv(2048)
        data = json.loads(result.decode("utf-8"))
        if data.get("status") != "OK":
            print(data.get("message"))
            Gtk.main_quit()
        else:
            self.__run()

    def __run(self):
        pass
        # self.epoll = select.epoll()
        # self.connection.setblocking(0)
        # self.epoll.register(self.sock.fileno(), select.EPOLLIN)
