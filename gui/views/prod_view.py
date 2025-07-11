import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import sessionmaker
from database.connection import engine
from models import Alkatresz, Projekt, ProjektAlkatresz, Feladat
from datetime import datetime

Session = sessionmaker(bind=engine)
session = Session()

def prod_view():
    def indit_uzem_nezettel(uzem):
        tech_map = {
            "Forgácsoló üzem": ["Marás", "Esztergálás", "Gravírozás"],
            "Lemezalakító üzem": ["Lemezmunka"],
            "Vízsugaras vágó üzem": ["Vízsugaras vágás"]
        }
        valasztott_tech = tech_map[uzem]
        uzem_valaszto.destroy()
        gyartasi_felulet(valasztott_tech)

    uzem_valaszto = tk.Toplevel()
    uzem_valaszto.title("Válassz üzemet")
    tk.Label(uzem_valaszto, text="Kérlek válassz üzemet:", font=("Arial", 12)).pack(pady=10)

    for uzem in ["Forgácsoló üzem", "Lemezalakító üzem", "Vízsugaras vágó üzem"]:
        tk.Button(uzem_valaszto, text=uzem, width=25, command=lambda u=uzem: indit_uzem_nezettel(u)).pack(pady=5)


def gyartasi_felulet(engedelyezett_technologiak):
    window = tk.Toplevel()
    window.title("Gyártási feladatok")
    window.geometry("1300x700")

    # Vissza gomb az üzemválasztóhoz
    back_frame = tk.Frame(window)
    back_frame.pack(anchor="w", padx=10, pady=5)
    tk.Button(back_frame, text="Vissza az üzemekhez", command=lambda: (window.destroy(), prod_view())).pack()

    tk.Label(window, text="Gyártási feladatok", font=("Arial", 12)).pack(pady=10)

    search_frame = tk.Frame(window)
    search_frame.pack(pady=5)

    tk.Label(search_frame, text="Keresés név vagy projekt szerint: ").pack(side=tk.LEFT)
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, padx=5)

    technologia_szurok = {}
    if len(engedelyezett_technologiak) > 1:
        for tech in engedelyezett_technologiak:
            var = tk.BooleanVar(value=True)
            technologia_szurok[tech] = var
            tk.Checkbutton(search_frame, text=tech, variable=var).pack(side=tk.LEFT)

    def keres():
        frissit_lista(search_entry.get().lower())

    tk.Button(search_frame, text="Szűrés", command=keres).pack(side=tk.LEFT, padx=5)
    tk.Button(search_frame, text="Szűrők törlése", command=lambda: reset_szurok()).pack(side=tk.LEFT, padx=5)

    tree_frame = tk.Frame(window)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    tree_scroll_x = tk.Scrollbar(tree_frame, orient="horizontal")
    tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    columns = ("hatarido", "alkatresz_nev", "technologia", "munkaszam", "sorszam", "megnevezes", "gyartando_db", "elkeszult_db", "gyartando_tukor", "elkeszult_tukor", "irodai_megjegyzes", "dolgozoi_megjegyzes")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", xscrollcommand=tree_scroll_x.set)
    tree_scroll_x.config(command=tree.xview)

    sort_column = {"col": None, "reverse": False}

    def sort_by(col):
        sort_column["reverse"] = not sort_column["reverse"] if sort_column["col"] == col else False
        sort_column["col"] = col
        frissit_lista(search_entry.get().lower())

    for col in columns:
        tree.heading(col, text=col.replace("_", " ").capitalize(), command=lambda c=col: sort_by(c))
        tree.column(col, width=120)

    tree.pack(fill=tk.BOTH, expand=True)

    selected_id = None
    feladat_map = {}

    def reset_szurok():
        search_entry.delete(0, tk.END)
        for var in technologia_szurok.values():
            var.set(True)
        frissit_lista("")

    def frissit_lista(szures):
        nonlocal selected_id, feladat_map
        tree.delete(*tree.get_children())
        feladatok = session.query(Feladat).join(Alkatresz).filter(Feladat.statusz == "Normál").all()

        records = []
        feladat_map = {}

        for f in feladatok:
            if f.technologia_tipus not in engedelyezett_technologiak:
                continue
            if technologia_szurok and not technologia_szurok.get(f.technologia_tipus, tk.BooleanVar(value=False)).get():
                continue
            kapcsolat = session.query(ProjektAlkatresz).filter_by(alkatresz_id=f.alkatresz_id).first()
            projekt = session.query(Projekt).get(kapcsolat.projekt_id) if kapcsolat else None
            if szures and szures not in (f.alkatresz.nev or '').lower() and \
            szures not in (projekt.munkaszam or '').lower() and \
            szures not in (projekt.projekt_megnevezes or '').lower():
                continue

            row = (
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
                f.alkatresz.irodai_megjegyzes,
                f.dolgozoi_megjegyzes
            )
            records.append(row)
            feladat_map[len(records)-1] = f.id

        if sort_column["col"]:
            idx = columns.index(sort_column["col"])
            try:
                records.sort(key=lambda r: (r[idx] if isinstance(r[idx], (int, float, datetime)) else str(r[idx])) if r[idx] is not None else "", reverse=sort_column["reverse"])
            except Exception:
                pass

        for i, row in enumerate(records):
            tree.insert("", "end", iid=i, values=row)

    def on_select(event):
        nonlocal selected_id
        selected = tree.focus()
        if selected:
            idx = int(selected)
            selected_id = feladat_map.get(idx)
            if selected_id:
                f = session.query(Feladat).get(selected_id)
                if f:
                    elkeszult_entry.delete(0, tk.END)
                    elkeszult_entry.insert(0, f.elkeszult_darab or 0)
                    elkeszult_tukor_entry.delete(0, tk.END)
                    elkeszult_tukor_entry.insert(0, f.elkeszult_tukrozott_darab or 0)
                    dolgozoi_megjegyzes_text.delete("1.0", tk.END)
                    dolgozoi_megjegyzes_text.insert("1.0", f.dolgozoi_megjegyzes or "")

    form_frame = tk.Frame(window)
    form_frame.pack(pady=10)

    tk.Label(form_frame, text="Elkészült db:").grid(row=0, column=0, sticky="e")
    elkeszult_entry = tk.Entry(form_frame)
    elkeszult_entry.grid(row=0, column=1)

    tk.Label(form_frame, text="Elkészült tükör db:").grid(row=1, column=0, sticky="e")
    elkeszult_tukor_entry = tk.Entry(form_frame)
    elkeszult_tukor_entry.grid(row=1, column=1)

    tk.Label(form_frame, text="Dolgozói megjegyzés:").grid(row=2, column=0, sticky="ne")
    dolgozoi_megjegyzes_text = tk.Text(form_frame, height=4, width=40)
    dolgozoi_megjegyzes_text.grid(row=2, column=1)

    def ment():
        if selected_id is not None:
            f = session.query(Feladat).get(selected_id)
            if not f:
                messagebox.showerror("Hiba", "Nem található a kiválasztott feladat.")
                return
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
            f.elkeszult_darab = elkeszult
            f.elkeszult_tukrozott_darab = elkeszult_tukor
            f.dolgozoi_megjegyzes = dolgozoi_megjegyzes_text.get("1.0", tk.END).strip()
            session.commit()
            frissit_lista(search_entry.get().lower())
            messagebox.showinfo("Mentve", "A módosítások elmentve.")

    tree.bind("<<TreeviewSelect>>", on_select)

    btn_frame = tk.Frame(window)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Mentés", command=ment).grid(row=0, column=0, padx=5)

    frissit_lista("")
    window.mainloop()

if __name__ == "__main__":
    prod_view()
