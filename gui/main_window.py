import tkinter as tk
from tkinter import messagebox

from gui.views.user_view import user_view
from gui.views.project_view import project_view
from gui.views.part_view import part_view
from gui.views.task_view import task_view
from gui.views.prod_view import prod_view
from gui.views.summary_view import summary_view

def main_window(felhasznalo):
    print(f"Név: {felhasznalo.nev}, Jogosultság ID: {felhasznalo.jogosultsag_id}")
    root = tk.Tk()
    root.title("Gyártáskövető rendszer")
    root.geometry("400x450")

    welcome_label = tk.Label(root, text=f"Üdvözlünk, {felhasznalo.nev}!", font=("Arial", 14))
    welcome_label.pack(pady=20)

    def not_implemented(name):
        messagebox.showinfo("Info", f"A(z) '{name}' funkció még nincs megvalósítva.")

    jogosultsag = felhasznalo.jogosultsag_id

    if jogosultsag <= 2:
        tk.Button(root, text="Projektek", width=25, command=project_view).pack(pady=5)

    if jogosultsag <= 3:
        tk.Button(root, text="Alkatrészek", width=25, command=part_view).pack(pady=5)
        tk.Button(root, text="Feladatok", width=25, command=task_view).pack(pady=5)

    if jogosultsag <= 4:
        tk.Button(root, text="Gyártási felület", width=25, command=prod_view).pack(pady=5)
        tk.Button(root, text="Alkatrész összesítő", width=25, command=summary_view).pack(pady=5)

    if jogosultsag == 1:
        tk.Button(root, text="Felhasználók", width=25, command=user_view).pack(pady=5)

    tk.Button(root, text="Kilépés", width=25, command=lambda: [root.destroy(), import_login()]).pack(pady=20)

    root.mainloop()

def import_login():
    from gui.views.login_view import login_window
    login_window()

if __name__ == "__main__":
    from models import Felhasznalo
    dummy_user = Felhasznalo(nev="Teszt Felhasználó", jogosultsag_id=2)
    main_window(dummy_user)
