import tkinter as tk
from tkinter import ttk
from sqlalchemy.orm import sessionmaker
from database.connection import engine
from models import Alkatresz, Projekt, ProjektAlkatresz, Feladat
from datetime import datetime

Session = sessionmaker(bind=engine)
session = Session()

def summary_view():
    window = tk.Toplevel()
    window.title("Alkatrészösszesítő")
    window.geometry("1400x700")

    tk.Label(window, text="Alkatrészösszesítő nézet", font=("Arial", 12)).pack(pady=10)

    filter_frame = tk.Frame(window)
    filter_frame.pack(pady=5)

    tk.Label(filter_frame, text="Keresés név vagy projekt szerint:").pack(side=tk.LEFT)
    search_entry = tk.Entry(filter_frame)
    search_entry.pack(side=tk.LEFT, padx=5)

    filter_vars = {
        "Aktív": tk.BooleanVar(value=True),
        "Archív": tk.BooleanVar(value=False),
        "Blokkolt": tk.BooleanVar(value=False)
    }
    for label, var in filter_vars.items():
        tk.Checkbutton(filter_frame, text=label, variable=var).pack(side=tk.LEFT)

    sort_column = {"col": None, "reverse": False}

    def keres():
        frissit_lista(search_entry.get().lower())

    def reset_szures():
        search_entry.delete(0, tk.END)
        for key in filter_vars:
            filter_vars[key].set(key == "Aktív")
        frissit_lista("")

    tk.Button(filter_frame, text="Szűrés", command=keres).pack(side=tk.LEFT, padx=5)
    tk.Button(filter_frame, text="Szűrés törlése", command=reset_szures).pack(side=tk.LEFT, padx=5)

    tree_frame = tk.Frame(window)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    tree_scroll_x = tk.Scrollbar(tree_frame, orient="horizontal")
    tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    columns = ("munkaszam", "projekt_nev", "alkatresz_nev", "VV", "M", "E", "G", "L", "Elkeszult")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", xscrollcommand=tree_scroll_x.set)
    tree_scroll_x.config(command=tree.xview)

    def sort_by(col):
        sort_column["reverse"] = not sort_column["reverse"] if sort_column["col"] == col else False
        sort_column["col"] = col
        frissit_lista(search_entry.get().lower())

    for col in columns:
        anchor = "center" if col in ("VV", "M", "E", "G", "L", "Elkeszult") else "w"
        tree.heading(col, text=col, command=lambda c=col: sort_by(c))
        tree.column(col, width=120, anchor=anchor)

    tree.pack(fill=tk.BOTH, expand=True)

    also_frame = tk.Frame(window)
    also_frame.pack(pady=10)
    labels = {}
    for i, mezonév in enumerate(["Gyártandó db", "Tükör db", "Elkészült db", "Elkészült tükör db"]):
        tk.Label(also_frame, text=mezonév + ":").grid(row=0, column=2*i, sticky="e", padx=5)
        lbl = tk.Label(also_frame, text="0", width=10, anchor="w")
        lbl.grid(row=0, column=2*i+1, padx=5)
        labels[mezonév] = lbl

    def frissit_lista(szures):
        tree.delete(*tree.get_children())
        alkatreszek = session.query(Alkatresz).all()
        rows = []

        for a in alkatreszek:
            kapcsolat = session.query(ProjektAlkatresz).filter_by(alkatresz_id=a.id).first()
            if not kapcsolat:
                continue
            projekt = session.query(Projekt).get(kapcsolat.projekt_id)
            if not projekt:
                continue

            if not (
                (filter_vars["Aktív"].get() and projekt.statusz == "Aktív" and a.statusz == "Normál") or
                (filter_vars["Archív"].get() and projekt.statusz == "Archív") or
                (filter_vars["Blokkolt"].get() and projekt.statusz == "Blokkolva")
            ):
                continue

            if szures and szures not in (a.nev or '').lower() and \
               szures not in (projekt.projekt_megnevezes or '').lower() and \
               szures not in (projekt.munkaszam or '').lower():
                continue

            feladatok = session.query(Feladat).filter_by(alkatresz_id=a.id).all()
            tech_allapot = {}
            for f in feladatok:
                gyartando = (a.gyartando_darab or 0) + (a.gyartando_tukrozott_darab or 0)
                elkeszult = (f.elkeszult_darab or 0) + (f.elkeszult_tukrozott_darab or 0)
                if gyartando == 0:
                    tech_allapot[f.technologia_tipus] = "✅"
                elif elkeszult == 0:
                    tech_allapot[f.technologia_tipus] = "❌"
                elif elkeszult < gyartando:
                    tech_allapot[f.technologia_tipus] = "⏳"
                else:
                    tech_allapot[f.technologia_tipus] = "✅"

            tech_nevek = ["Vízsugaras vágás", "Marás", "Esztergálás", "Gravírozás", "Lemezmunka"]
            ikonok = [tech_allapot.get(t, '') for t in tech_nevek]

            elkeszult_status = "✅" if all(ikon not in ("❌", "⏳") for ikon in ikonok if ikon) else ""

            sor = [projekt.munkaszam, projekt.projekt_megnevezes, a.nev] + ikonok + [elkeszult_status]
            rows.append((a.id, sor))

        if sort_column["col"]:
            idx = columns.index(sort_column["col"])
            rows.sort(key=lambda r: r[1][idx] or "", reverse=sort_column["reverse"])

        for rid, values in rows:
            tree.insert("", "end", iid=str(rid), values=values)

    def on_select(event):
        selected = tree.focus()
        if selected:
            alk = session.query(Alkatresz).get(int(selected))
            if alk:
                feladatok = session.query(Feladat).filter_by(alkatresz_id=alk.id).all()
                tech_map = {}

                for f in feladatok:
                    tech = f.technologia_tipus
                    if tech not in tech_map:
                        tech_map[tech] = {"elkeszult": [], "elkeszult_tukor": []}
                    tech_map[tech]["elkeszult"].append(f.elkeszult_darab or 0)
                    tech_map[tech]["elkeszult_tukor"].append(f.elkeszult_tukrozott_darab or 0)

                # Minimumokat számolunk technológiánként
                teljes_elkeszult = min((sum(vals["elkeszult"]) for vals in tech_map.values()), default=0)
                teljes_tukor = min((sum(vals["elkeszult_tukor"]) for vals in tech_map.values()), default=0)

                labels["Gyártandó db"].config(text=str(alk.gyartando_darab or 0))
                labels["Tükör db"].config(text=str(alk.gyartando_tukrozott_darab or 0))
                labels["Elkészült db"].config(text=str(teljes_elkeszult))
                labels["Elkészült tükör db"].config(text=str(teljes_tukor))

    tree.bind("<<TreeviewSelect>>", on_select)
    frissit_lista("")
    window.mainloop()

if __name__ == "__main__":
    summary_view()
