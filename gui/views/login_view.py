import tkinter as tk
from tkinter import messagebox
from sqlalchemy.orm import sessionmaker
from database.connection import engine
from services.auth_service import bejelentkezes
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from gui.main_window import main_window

# SQLAlchemy session létrehozása
Session = sessionmaker(bind=engine)
session = Session()

def login_window():
    def on_login(event=None):
        username = username_entry.get()
        password = password_entry.get()
        felhasznalo = bejelentkezes(session, username, password)
        if felhasznalo:
            messagebox.showinfo("Sikeres belépés", f"Üdvözlünk, {felhasznalo.nev}!")
            root.destroy()
            # TODO: Itt megnyitható a főablak később (main_window.py)
            main_window(felhasznalo)
        else:
            messagebox.showerror("Hibás belépés", "Helytelen felhasználónév vagy jelszó.")

    root = tk.Tk()
    root.title("Belépés")
    root.geometry("300x180")

    tk.Label(root, text="Felhasználónév:").pack(pady=(20, 5))
    username_entry = tk.Entry(root)
    username_entry.pack()

    tk.Label(root, text="Jelszó:").pack(pady=(10, 5))
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    tk.Button(root, text="Bejelentkezés", command=on_login).pack(pady=20)

    root.bind('<Return>', on_login)

    root.mainloop()

if __name__ == "__main__":
    login_window()