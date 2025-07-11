import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import sessionmaker
from database.connection import engine
from models import Felhasznalo, Jogosultsag

Session = sessionmaker(bind=engine)
session = Session()

def user_view():
    window = tk.Toplevel()
    window.title("Felhasználók kezelése")
    window.geometry("600x550")

    tk.Label(window, text="Felhasználók listája", font=("Arial", 12)).pack(pady=10)

    user_listbox = tk.Listbox(window, width=60)
    user_listbox.pack(pady=5)

    # Mezők
    form_frame = tk.Frame(window)
    form_frame.pack(pady=10)

    tk.Label(form_frame, text="Név:").grid(row=0, column=0, sticky="e")
    nev_entry = tk.Entry(form_frame)
    nev_entry.grid(row=0, column=1)

    tk.Label(form_frame, text="Felhasználónév:").grid(row=1, column=0, sticky="e")
    fnev_entry = tk.Entry(form_frame)
    fnev_entry.grid(row=1, column=1)

    tk.Label(form_frame, text="Jelszó:").grid(row=2, column=0, sticky="e")
    jelszo_entry = tk.Entry(form_frame, show="*")
    jelszo_entry.grid(row=2, column=1)

    tk.Label(form_frame, text="Jogosultság:").grid(row=3, column=0, sticky="e")
    jogosultsag_combo = ttk.Combobox(form_frame, values=["1 - Admin", "2 - Projektmenedzser", "3 - Technológus", "4 - Operátor"])
    jogosultsag_combo.grid(row=3, column=1)

    tk.Label(form_frame, text="Munkakör:").grid(row=4, column=0, sticky="e")
    munkakor_entry = tk.Entry(form_frame)
    munkakor_entry.grid(row=4, column=1)

    selected_user = None

    def frissit_lista():
        user_listbox.delete(0, tk.END)
        felhasznalok = session.query(Felhasznalo).all()
        for f in felhasznalok:
            jog = session.query(Jogosultsag).filter_by(id=f.jogosultsag_id).first()
            jog_nev = jog.nev if jog else "Ismeretlen"
            user_listbox.insert(tk.END, f"{f.id}: {f.nev} ({f.felhasznalonev}) - {jog_nev}")

    def on_select(event):
        nonlocal selected_user
        try:
            index = user_listbox.curselection()[0]
            user_id = int(user_listbox.get(index).split(":")[0])
            selected_user = session.query(Felhasznalo).get(user_id)
            nev_entry.delete(0, tk.END)
            nev_entry.insert(0, selected_user.nev)
            fnev_entry.delete(0, tk.END)
            fnev_entry.insert(0, selected_user.felhasznalonev)
            jelszo_entry.delete(0, tk.END)
            jelszo_entry.insert(0, selected_user.jelszo)
            jog = session.query(Jogosultsag).filter_by(id=selected_user.jogosultsag_id).first()
            jog_nev = jog.nev if jog else "Ismeretlen"
            jogosultsag_combo.set(f"{selected_user.jogosultsag_id} - {jog_nev}")
            munkakor_entry.delete(0, tk.END)
            munkakor_entry.insert(0, selected_user.munkakor or "")
        except IndexError:
            pass

    def ment():
        if selected_user:
            selected_user.nev = nev_entry.get()
            selected_user.felhasznalonev = fnev_entry.get()
            selected_user.jelszo = jelszo_entry.get()
            selected_user.jogosultsag_id = int(jogosultsag_combo.get().split(" - ")[0])
            selected_user.munkakor = munkakor_entry.get()
            session.commit()
            messagebox.showinfo("Mentve", "A módosítások elmentve.")
            frissit_lista()

    def hozzaad():
        uj = Felhasznalo(
            nev=nev_entry.get(),
            felhasznalonev=fnev_entry.get(),
            jelszo=jelszo_entry.get(),
            jogosultsag_id=int(jogosultsag_combo.get().split(" - ")[0]),
            munkakor=munkakor_entry.get()
        )
        session.add(uj)
        session.commit()
        frissit_lista()

    def torol():
        if selected_user:
            if messagebox.askyesno("Törlés megerősítése", f"Valóban törölni szeretnéd: {selected_user.nev}?"):
                session.delete(selected_user)
                session.commit()
                frissit_lista()

    button_frame = tk.Frame(window)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Mentés", command=ment).grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="Hozzáadás", command=hozzaad).grid(row=0, column=1, padx=5)
    tk.Button(button_frame, text="Törlés", command=torol).grid(row=0, column=2, padx=5)

    user_listbox.bind('<<ListboxSelect>>', on_select)

    frissit_lista()
    window.mainloop()

if __name__ == "__main__":
    user_view()
