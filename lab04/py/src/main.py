import tkinter as tk

from db import DB
from models import User


def reg_user():
    username = username_entry.get()
    if username:
        user = User(username=username)
        user = DB.get_instance().register_user(user)
        show_user(user)
    username_entry.delete(0, tk.END)


def show_user(user: User) -> None:
    user_frame = tk.Frame(root, relief=tk.RAISED, borderwidth=1)
    user_frame.pack(fill=tk.X, pady=2, padx=5)

    user_label = tk.Label(
        user_frame,
        text=f"ID: {user.id} | Username: {user.username}",
        anchor="w",
    )
    user_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))


root = tk.Tk()
root.title("DBManager")
root.geometry("350x200")

enter_label = tk.Label(root, text="Enter username:")
enter_label.pack(side=tk.TOP, fill=tk.X, padx=5)
username_entry = tk.Entry(root)
username_entry.pack(side=tk.TOP, fill=tk.X, padx=5)
add_button = tk.Button(root, text="reg user", command=reg_user)
add_button.pack(side=tk.TOP, fill=tk.X, padx=5)


for user in DB.get_instance().get_all_users():
    show_user(user)

root.mainloop()
