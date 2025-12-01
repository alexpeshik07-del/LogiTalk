from customtkinter import *
from socket import *
import threading

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.title("LogiTalk")
        self.geometry("500x500")
        self.menu_frame = CTkFrame(self, width = 30, height = 300)
        self.menu_frame.place(x = 0, y = 0, relwidth = 0, relheight = 1)
        self.logitalk_label = CTkLabel(self.menu_frame, text = "Вхід в LogiTalk", font = ("Arial", 24, "bold"))
        self.logitalk_label.place(relx = 0.2, rely = 0.3)
        self.name_entry = CTkEntry(self.menu_frame, placeholder_text = "Введіть ім'я")
        self.name_entry.place(relx = 0.25, rely = 0.5)
        self.host_entry = CTkEntry(self.menu_frame, placeholder_text = "Введіть ХОСТ серверу")
        self.host_entry.place(relx = 0.25, rely = 0.6)
        self.port_entry = CTkEntry(self.menu_frame, placeholder_text = "Введіть ПОРТ серверу")
        self.port_entry.place(relx = 0.25, rely = 0.7)
        self.button_register = CTkButton(self.menu_frame, text = "Зареєструватися", command = self.register)
        self.button_register.place(relx = 0.25, rely = 0.8)
        self.button = CTkButton(self, text = "▶", width = 30, command = self.toggle_menu)
        self.button.place(x = 0, y = 0)
        self.is_menu_show = False
        self.username = "phantom"
        self.host = "" 
        self.port = 0

        self.message_frame = CTkFrame(self)
        self.message_frame.place(relx = 0.01, rely = 0.89, relwidth = 0.98, relheight = 0.1)
        self.message_entry = CTkEntry(self.message_frame, placeholder_text = "Введіть повідомлення")
        self.message_entry.place(relx = 0.01, rely = 0.05, relwidth = 0.78, relheight = 0.9)
        self.message_button = CTkButton(self.message_frame, text = "✉", font = ("Arial", 40, "normal"), command = self.send_message)
        self.message_button.place(relx = 0.8, rely = 0.05, relwidth = 0.19, relheight = 0.9)

        self.chat_frame = CTkScrollableFrame(self)
        self.chat_frame.place(relx = 0.01, rely = 0.06, relwidth = 0.98, relheight = 0.82)


      
    
    def toggle_menu(self):
        if self.is_menu_show :
            self.is_menu_show = False
            self.button.configure(text = "▶")
            self.hide_menu()
        else:
            self.is_menu_show = True
            self.button.configure(text = "◀")
            self.show_menu()
            # self.speed_animation_menu *= -1
            # self.show_menu()
            # self.label = CTkLabel(self.menu_frame, text = "Ім'я")
            # self.label.pack(pady = 30)
            # self.entry = CTkEntry(self.menu_frame)
            # self.entry.pack()


            

    def show_menu(self):
        self.menu_frame.place(x = 0, y = 0, relwidth = 0.5, relheight = 1)
        self.message_frame.place(relx = 0.51, relwidth = 0.47)
        self.chat_frame.place(relx = 0.51, rely = 0.01, relwidth = 0.48, relheight = 0.87)
    
    def hide_menu(self):
        self.menu_frame.place(x = 0, y = 0, relwidth = 0, relheight = 1)
        self.message_frame.place(relx = 0.01, relwidth = 0.98)
        self.chat_frame.place(relx = 0.01, rely = 0.06, relwidth = 0.98, relheight = 0.82)

    def show_new_message(self, message, username = "system"):
        message_frame_side = "left"
        message_frame_color = "lightblue"
        if username == self.username:
            message_frame_side = "right"
            message_frame_color = "lightgreen"
        elif username == "system":
            message_frame_side = "top"
            message_frame_color = "lightgray"

        message_conteiner = CTkFrame(self.chat_frame, fg_color = "transparent")
        message_conteiner.pack(side = "top", fill = "x")
        new_message_frame = CTkFrame(message_conteiner, fg_color = message_frame_color)
        new_message_frame.pack(side = message_frame_side, pady = 5)
        name_label = CTkLabel(new_message_frame, text = username, font = ("Arial", 12, "bold"), text_color = "black", fg_color = "transparent")
        name_label.pack(padx = 10, anchor = "w")
        message_label = CTkLabel(new_message_frame, text = message, font = ("Arial", 13, "normal"), text_color = "black", fg_color = "transparent", justify = "left", wraplength = 100)
        message_label.pack(padx = 10, pady = (0,5), anchor = "w")
        # Оновлюємо wraplength по ширині контейнера через подію Configure
        def on_config(event):
            padding = 400  # відступи всередині контейнера
            print("Container width:", event.width)
            print(self.chat_frame.winfo_width())
            new_wrap = max(100, event.width - padding)
            message_label.configure(wraplength=new_wrap)

        # прив'язати до message_container (викликається коли змінюється реальна ширина)
        message_conteiner.bind("<Configure>", on_config)
        self.update_idletasks()

    def register(self):
        new_name = self.name_entry.get().strip()
        new_host = self.host_entry.get().strip()
        new_port = self.port_entry.get().strip()

        if not new_name or not new_host or not new_port:
            self.show_new_message("Для реєстрації в додатку - заповніть всі три поля!")
            return
        
        self.username = new_name
        self.host = new_host
        self.port = int(new_port)

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode("utf-8"))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.show_new_message(f"Не вдалося підключитися до сервера: {e}")


    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode("utf-8", errors="ignore")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())

            except:
                break
        self.sock.close()

    def send_message(self):
        message = self.message_entry.get().strip()
        if message:
            self.show_new_message(message, self.username)
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.message_entry.delete(0, END)

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.show_new_message(message, author)
        else:
            self.show_new_message(line)

        

window = MainWindow()

window.mainloop()




