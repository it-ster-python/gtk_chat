import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, GLib
from ui import login
import redis
import socket

import select
import json
import os
from ui import event
import pickle
from threading import Lock


LOCK = Lock()
HOST = "127.0.0.1"
PORT = 5000


class ChatWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Mega Chat | Chat")
        event.Event(name="login", callback=self.regy_date)
        self.login_win = login.LoginWindow()
        self.login_win.show_all()
        self.connection = None
        self.__interfase()
        self.chat_name = "default"
        self.connections = {}
        self.requests = {}
        self.responses = {}

    def __interfase(self):
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(800, 600)

        master_box = Gtk.Box()
        master_box.set_spacing(5)
        self.add(master_box)

        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_box.set_size_request(200, -1)
        master_box.pack_start(left_box, False, True, 0)
        separator = Gtk.VSeparator()
        master_box.pack_start(separator, False, True, 0)

        center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        master_box.pack_start(center_box, True, True, 0)
        separator = Gtk.VSeparator()
        master_box.pack_start(separator, False, True, 0)

        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        right_box.set_size_request(200, -1)
        master_box.pack_start(right_box, False, True, 0)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "Avatar.png"
            ),
            width=190,
            height=190,
            preserve_aspect_ratio=True,
        )
        avatar = Gtk.Image.new_from_pixbuf(pixbuf)
        left_box.pack_start(avatar, False, True, 5)
        separator = Gtk.HSeparator()
        left_box.pack_start(separator, False, True, 5)
        user_label = Gtk.Label(label="User name")
        # Проверить растягивание
        left_box.pack_start(user_label, False, True, 5)
        separator = Gtk.HSeparator()
        left_box.pack_start(separator, False, True, 5)

        l_space = Gtk.Alignment()
        left_box.pack_start(l_space, True, True, 5)

        separator = Gtk.HSeparator()
        left_box.pack_start(separator, False, True, 5)

        b_box = Gtk.ButtonBox()
        left_box.pack_start(b_box, False, True, 5)
        close_button = Gtk.Button(label="Close")
        close_button.connect("clicked", Gtk.main_quit)
        b_box.pack_start(close_button, True, True, 5)

        scroll_box = Gtk.ScrolledWindow()
        scroll_box.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        center_box.pack_start(scroll_box, True, True, 5)

        self.chat_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scroll_box.add(self.chat_box)
        separator = Gtk.HSeparator()
        center_box.pack_start(separator, False, False, 5)

        send_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        send_box.set_spacing(5)
        center_box.pack_start(send_box, False, True, 5)
        separator = Gtk.HSeparator()
        center_box.pack_start(separator, False, False, 5)

        smile_button = Gtk.Button(label=":-}")
        send_box.pack_start(smile_button, False, False, 0)
        self.message_entry = Gtk.Entry()
        # Проверить растягивание
        send_box.pack_start(self.message_entry, True, True, 0)
        send_button = Gtk.Button(label="Send")
        send_button.connect("clicked", self.on_send_message)
        send_box.pack_start(send_button, False, False, 0)

        favorit_label = Gtk.Label(label="Избранное")
        # Проверить растягивание
        right_box.pack_start(favorit_label, False, True, 5)

    def __add_message_box(self, data, input=True):
        message_frame = Gtk.Frame()
        message_box = Gtk.Box()
        message_frame.add(message_box)
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                f".contacts/{data['user']}.png" if input else "Avatar.png",
            ),
            width=100,
            height=100,
            preserve_aspect_ratio=True,
        )
        avatar = Gtk.Image.new_from_pixbuf(pixbuf)
        test_label = Gtk.Label()
        test_label.set_markup(data["message"])
        test_label.set_selectable(True)
        test_label.set_line_wrap(True)
        if input:
            message_box.pack_start(avatar, False, True, 5)
        else:
            message_box.pack_end(avatar, False, True, 5)
            test_label.set_justify(Gtk.Justification.RIGHT)
        message_box.pack_start(test_label, True, False, 5)
        self.chat_box.pack_start(message_frame, False, True, 5)

    def regy_date(self, *args, **kwargs):
        self.login_win.hide()
        self.storage = redis.StrictRedis()
        try:
            self.login = pickle.loads(self.storage.get("login"))
            self.password = pickle.loads(self.storage.get("password"))
        except redis.RedisError:
            print("Данных почему то нет!")
            Gtk.main_quit()
        else:
            self.__create_conntetion()
            self.show_all()

    def __create_conntetion(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connection.connect((HOST, PORT))
        response = self.connection.recv(2048)
        data = json.loads(response.decode("utf-8"))
        if data.get("status") != "OK":
            print(data.get("message"))
            Gtk.main_quit()
        else:
            request = json.dumps({"login": self.login, "password": self.password})
            request += "\r\n"
            self.connection.send(request.encode("utf-8"))
            response = self.connection.recv(2048)
            auth_data = json.loads(response.decode("utf-8"))
            if auth_data.get("status") == "OK":
                self.__run()
            else:
                print(data.get("message"))
                Gtk.main_quit()

    def __run(self):
        """TODO закрепить за соединениями имена (названия чатов).
        При отправке сообщения в чат запрашивать его имя"""
        self.epoll = select.epoll()
        self.connection.setblocking(0)
        self.epoll.register(self.connection.fileno(), select.EPOLLIN)
        self.connections[self.connection.fileno()] = self.connection

        # self.interval = GLib.timeout_add_seconds(1, self.on_recv_message)

        # while True:
        #     events = self.epoll.poll(1)
        #     for fileno, event in events:
        #         if event & select.EPOLLIN:
        #             with LOCK:
        #                 self.responses[fileno] = (
        #                     self.connections[fileno].recv(2048).decode("utf-8")
        #                 )
        #             self.epoll.modify(fileno, select.EPOLLOUT)
        #         elif event & select.EPOLLOUT:
        #             self.connections[fileno].send(self.requests[fileno].encode("utf-8"))
        #             # добавить проверку на отправление всего объема данных
        #             with LOCK:
        #                 del self.requests[fileno]

    def on_send_message(self, widget):
        message = self.message_entry.get_text()
        data = json.dumps(
            {"message": message, "user": self.login, "chat": self.chat_name}
        )
        with LOCK:
            self.requests[self.connection.fileno()] = data
        self.message_entry.set_text("")

    def on_recv_message(self, *args):
        data = None
        with LOCK:
            data = self.responses[self.connection.fileno()]
            del self.responses[self.connection.fileno()]
        print(data)


# test_input = {
#     "message": (
#         "Parses str which is marked up with the Pango text"
#         "markup language, setting the label’s text and attribute list "
#         "based on the parse results. If characters in str are "
#         "preceded by an underscore, they are underlined that they "
#         "indicating represent a keyboard accelerator called a mnemonic"
#     ),
#     "user": "Vasia"
# }
# test_output = {
#     "message": (
#         "If the label has been set so that it has an mnemonic"
#         "key (using i.e. Gtk.Label.set_markup_with_mnemonic(),"
#         "Gtk.Label.set_text_with_mnemonic(),"
#         "Gtk.Label.new_with_mnemonic() or"
#         "the “use_underline” property) the label"
#         "can be associated"
#     ),
#     "user": "User"
# }

# self.__add_message_box(test_input)
# self.__add_message_box(test_input)
# self.__add_message_box(test_output, False)
