import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import sessionmaker
from database.connection import engine
from models import Alkatresz, Projekt, ProjektAlkatresz, Feladat
from datetime import datetime

Session = sessionmaker(bind=engine)
session = Session()

def task_view():
    window = tk.Toplevel()
    window.title("Feladatok kezelése")
    window.geometry("1300x700")

    tk.Label(window, text="Feladatok listája", font=("Arial", 12)).pack(pady=10)

    search_frame = tk.Frame(window)
    search_frame.pack(pady=5)

    tk.Label(search_frame, text="Keresés név vagy projekt szerint: ").pack(side=tk.LEFT)
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, padx=5)

    statusz_filter = tk.StringVar(value="")
    ttk.Combobox(search_frame, textvariable=statusz_filter, values=["", "Normál", "Blokkolva"], width=10).pack(side=tk.LEFT, padx=5)

    technologia_szurok = {}
    for tech in ["Vízsugaras vágás", "Marás", "Esztergálás", "Gravírozás", "Lemezmunka"]:
        var = tk.BooleanVar(value=True)
        technologia_szurok[tech] = var
        tk.Checkbutton(search_frame, text=tech, variable=var).pack(side=tk.LEFT)

    def keres():
        frissit_lista(search_entry.get().lower(), statusz_filter.get())

    tk.Button(search_frame, text="Szűrés", command=keres).pack(side=tk.LEFT, padx=5)
    tk.Button(search_frame, text="Szűrők törlése", command=lambda: reset_szurok()).pack(side=tk.LEFT, padx=5)

    tree_frame = tk.Frame(window)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    tree_scroll_x = tk.Scrollbar(tree_frame, orient="horizontal")
    tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    columns = ("hatarido", "alkatresz_nev", "technologia", "munkaszam", "sorszam", "megnevezes", "gyartando_db", "elkeszult_db", "gyartando_tukor", "elkeszult_tukor", "statusz", "irodai_megjegyzes", "dolgozoi_megjegyzes")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", xscrollcommand=tree_scroll_x.set)
    tree_scroll_x.config(command=tree.xview)

    sort_column = {"col": None, "reverse": False}

    def sort_by(col):
        sort_column["reverse"] = not sort_column["reverse"] if sort_column["col"] == col else False
        sort_column["col"] = col
        frissit_lista(search_entry.get().lower(), statusz_filter.get())

    for col in columns:
        tree.heading(col, text=col.replace("_", " ").capitalize(), command=lambda c=col: sort_by(c))
        tree.column(col, width=120)

    tree.pack(fill=tk.BOTH, expand=True)

    selected_id = None

    def reset_szurok():
        search_entry.delete(0, tk.END)
        statusz_filter.set("")
        for var in technologia_szurok.values():
            var.set(True)
        frissit_lista("", "")

    def frissit_lista(szures, statusz):
        nonlocal selected_id
        tree.delete(*tree.get_children())
        feladatok = session.query(Feladat).join(Alkatresz).all()

        records = []
        for f in feladatok:
            kapcsolat = session.query(ProjektAlkatresz).filter_by(alkatresz_id=f.alkatresz_id).first()
            projekt = session.query(Projekt).get(kapcsolat.projekt_id) if kapcsolat else None

            if not technologia_szurok.get(f.technologia_tipus, tk.BooleanVar(value=False)).get():
                continue
            if szures and szures not in (f.alkatresz.nev or '').lower() and szures not in (projekt.projekt_megnevezes or '').lower():
                continue
            if statusz and f.statusz != statusz:
                continue

            records.append((
                f.alkatresz.hatarido,
                f.alkatresz.nev,
                f.technologia_tipus,
                projekt.munkaszam if projekt else "",
                projekt.projekt_sorszam if projekt else "",
                projekt.projekt_megnevezes if projekt else "",
                f.alkatresz.gyartando_darab,
                f.elkeszult_darab,
                f.alkatresz.gyartando_tukrozott_darab,
                f.elkeszult_tukrozott_darab,
                f.statusz,
                f.alkatresz.irodai_megjegyzes,
                f.dolgozoi_megjegyzes
            ))

        if sort_column["col"]:
            idx = columns.index(sort_column["col"])

            def sort_key(r):
                val = r[idx]
                if isinstance(val, datetime):
                    return val or datetime.min
                elif isinstance(val, (int, float)):
                    return val if val is not None else float("-inf")
                elif isinstance(val, str):
                    return val.lower()
                elif val is None:
                    return ""
                return str(val)

            records.sort(key=sort_key, reverse=sort_column["reverse"])

        for i, row in enumerate(records):
            tree.insert("", "end", iid=i, values=row)

    def on_select(event):
        nonlocal selected_id
        selected = tree.focus()
        if selected:
            selected_id = int(selected)
            f = session.query(Feladat).get(selected_id)
            if not f:
                return
            statusz_combo.set(f.statusz or "")
            elkeszult_entry.delete(0, tk.END)
            elkeszult_entry.insert(0, f.elkeszult_darab or 0)
            elkeszult_tukor_entry.delete(0, tk.END)
            elkeszult_tukor_entry.insert(0, f.elkeszult_tukrozott_darab or 0)
            dolgozoi_megjegyzes_text.delete("1.0", tk.END)
            dolgozoi_megjegyzes_text.insert("1.0", f.dolgozoi_megjegyzes or "")

    form_frame = tk.Frame(window)
    form_frame.pack(pady=10)

    tk.Label(form_frame, text="Státusz:").grid(row=0, column=0, sticky="e")
    statusz_combo = ttk.Combobox(form_frame, values=["Normál", "Blokkolva"])
    statusz_combo.grid(row=0, column=1)

    tk.Label(form_frame, text="Elkészült db:").grid(row=1, column=0, sticky="e")
    elkeszult_entry = tk.Entry(form_frame)
    elkeszult_entry.grid(row=1, column=1)

    tk.Label(form_frame, text="Elkészült tükör db:").grid(row=2, column=0, sticky="e")
    elkeszult_tukor_entry = tk.Entry(form_frame)
    elkeszult_tukor_entry.grid(row=2, column=1)

    tk.Label(form_frame, text="Dolgozói megjegyzés:").grid(row=3, column=0, sticky="ne")
    dolgozoi_megjegyzes_text = tk.Text(form_frame, height=4, width=40)
    dolgozoi_megjegyzes_text.grid(row=3, column=1)

    def ment():
        if selected_id is not None:
            f = session.query(Feladat).get(selected_id)
            if not messagebox.askyesno("Megerősítés", f"Biztosan frissíteni szeretnéd a(z) '{f.alkatresz.nev}' alkatrész '{f.technologia_tipus}' feladatát?"):
                return

            try:
                elkeszult = int(elkeszult_entry.get() or 0)
                elkeszult_tukor = int(elkeszult_tukor_entry.get() or 0)
            except ValueError:
                messagebox.showerror("Hiba", "Az elkészült darabszám mezőkben csak szám szerepelhet.")
                return

            if elkeszult > f.alkatresz.gyartando_darab or elkeszult_tukor > f.alkatresz.gyartando_tukrozott_darab:
                messagebox.showerror("Hiba", "Az elkészült darabszám nem lehet nagyobb, mint a gyártandó mennyiség!")
                return

            f.statusz = statusz_combo.get()
            f.elkeszult_darab = elkeszult
            f.elkeszult_tukrozott_darab = elkeszult_tukor
            f.dolgozoi_megjegyzes = dolgozoi_megjegyzes_text.get("1.0", tk.END).strip()
            session.commit()
            frissit_lista(search_entry.get().lower(), statusz_filter.get())
            messagebox.showinfo("Mentve", "A módosítások elmentve.")

    def torol():
        if selected_id is not None:
            if messagebox.askyesno("Törlés", "Biztosan törölni szeretnéd a kiválasztott feladatot?"):
                session.delete(session.query(Feladat).get(selected_id))
                session.commit()
                frissit_lista(search_entry.get().lower(), statusz_filter.get())

    tree.bind("<<TreeviewSelect>>", on_select)

    btn_frame = tk.Frame(window)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Mentés", command=ment).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Törlés", command=torol).grid(row=0, column=1, padx=5)

    frissit_lista("", "")
    window.mainloop()

if __name__ == "__main__":
    task_view()
