import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import sessionmaker
from database.connection import engine
from models import Alkatresz, Projekt, ProjektAlkatresz, Feladat
from datetime import datetime

Session = sessionmaker(bind=engine)
session = Session()

def part_view():
    window = tk.Toplevel()
    window.title("Alkatrészek kezelése")
    window.geometry("1350x900")

    tk.Label(window, text="Alkatrészek listája", font=("Arial", 12)).pack(pady=10)

    search_frame = tk.Frame(window)
    search_frame.pack(pady=5)

    tk.Label(search_frame, text="Keresés név szerint: ").pack(side=tk.LEFT)
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, padx=5)

    show_archived = tk.BooleanVar(value=True)
    show_archived_cb = tk.Checkbutton(search_frame, text="Archív alkatrészek elrejtése", variable=show_archived, command=lambda: frissit_lista(szures=search_entry.get().lower()))
    show_archived_cb.pack(side=tk.LEFT, padx=5)

    def keres():
        szoveg = search_entry.get().lower()
        frissit_lista(szures=szoveg)

    tk.Button(search_frame, text="Szűrés", command=keres).pack(side=tk.LEFT, padx=5)

    tree_frame = tk.Frame(window)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    tree_scroll_x = tk.Scrollbar(tree_frame, orient="horizontal")
    tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    columns = ("nev", "hatarido", "statusz", "lemezvastagsag", "anyag", "tipus", "gyartando_darab", "gyartando_tukrozott_darab")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", xscrollcommand=tree_scroll_x.set)
    tree_scroll_x.config(command=tree.xview)

    sort_column = {"col": None, "reverse": False}

    def sort_by(col):
        reverse = not sort_column["reverse"] if sort_column["col"] == col else False
        sort_column["col"] = col
        sort_column["reverse"] = reverse
        frissit_lista(szures=search_entry.get().lower())

    for col in columns:
        tree.heading(col, text=col.replace("_", " ").capitalize(), command=lambda c=col: sort_by(c))

    tree.pack(fill=tk.BOTH, expand=True)

    form_frame = tk.Frame(window)
    form_frame.pack(pady=10)

    statuszok = ["Normál", "Blokkolva"]
    lemezvastagsagok = ["-", "1mm", "1,5mm", "2mm", "2,5mm", "3mm", "4mm", "5mm", "6mm", "8mm", "10mm", "12mm", "15mm", "20mm", "25mm", "30mm", "40 mm", "50 mm", "60 mm"]
    anyagok = ["DC01", "S235", "PE", "PP", "Vegyes (rajz szerint)", "Rozsdamentes acél", "Cseppmintás", "Alumínium", "PTFE", "S355", "Perforált", "Gyémántmintás"]
    tipusok = ["Alakadó felület", "Beépülő, nem alakadó", "Leütő", "Görgő", "Prés", "Készülék", "Sablon"]
    technologiak = ["Vízsugaras vágás", "Marás", "Esztergálás", "Gravírozás", "Lemezmunka"]

    entries = {}
    widgets = {}

    def add_entry(label, row):
        tk.Label(form_frame, text=label + ":").grid(row=row, column=0, sticky="e")
        entry = tk.Entry(form_frame)
        entry.grid(row=row, column=1)
        entries[label.lower()] = entry
        return entry

    add_entry("Név", 0)
    add_entry("Határidő (ÉÉÉÉ-HH-NN)", 1)
    add_entry("Határidő idő (ÓÓ:PP:MM)", 2)

    tk.Label(form_frame, text="Státusz:").grid(row=3, column=0, sticky="e")
    statusz_combo = ttk.Combobox(form_frame, values=statuszok)
    statusz_combo.grid(row=3, column=1)
    widgets["statusz"] = statusz_combo

    tk.Label(form_frame, text="Lemezvastagság:").grid(row=4, column=0, sticky="e")
    lv_combo = ttk.Combobox(form_frame, values=lemezvastagsagok)
    lv_combo.grid(row=4, column=1)
    widgets["lemezvastagsag"] = lv_combo

    tk.Label(form_frame, text="Anyag:").grid(row=5, column=0, sticky="e")
    anyag_combo = ttk.Combobox(form_frame, values=anyagok)
    anyag_combo.grid(row=5, column=1)
    widgets["anyag"] = anyag_combo

    tk.Label(form_frame, text="Típus:").grid(row=6, column=0, sticky="e")
    tipus_combo = ttk.Combobox(form_frame, values=tipusok)
    tipus_combo.grid(row=6, column=1)
    widgets["tipus"] = tipus_combo

    add_entry("Gyártandó db", 7)
    add_entry("Tükör db", 8)
    add_entry("Profil hossz", 9)
    add_entry("Felszín", 10)
    add_entry("Tömeg", 11)

    checkbox_vars = {}
    oldal_frame = tk.Frame(form_frame)
    oldal_frame.grid(row=12, column=1, sticky="w")
    for i, oldal in enumerate(["a_oldal", "b_oldal", "c_oldal", "d_oldal"]):
        var = tk.BooleanVar()
        checkbox_vars[oldal] = var
        cb = tk.Checkbutton(oldal_frame, text=oldal.upper(), variable=var)
        cb.grid(row=0, column=i)

    rajz_frame = tk.Frame(form_frame)
    rajz_frame.grid(row=13, column=1, sticky="w")
    for i, rajz in enumerate(["rajz_3d", "rajz_2d", "kiadva"]):
        var = tk.BooleanVar()
        checkbox_vars[rajz] = var
        cb = tk.Checkbutton(rajz_frame, text=rajz.replace("_", " ").upper(), variable=var)
        cb.grid(row=0, column=i)

    tk.Label(form_frame, text="Technológiák:").grid(row=14, column=0, sticky="ne")
    tech_frame = tk.Frame(form_frame)
    tech_frame.grid(row=14, column=1, sticky="w")
    tech_vars = {}
    for i, tech in enumerate(technologiak):
        var = tk.BooleanVar()
        tech_vars[tech] = var
        cb = tk.Checkbutton(tech_frame, text=tech, variable=var)
        cb.grid(row=i//3, column=i%3, sticky="w")

    tk.Label(form_frame, text="Irodai megjegyzés:").grid(row=15, column=0, sticky="ne")
    megjegyzes_text = tk.Text(form_frame, height=4, width=40)
    megjegyzes_text.grid(row=15, column=1)

    tk.Label(form_frame, text="Projekt munkaszám:").grid(row=16, column=0, sticky="e")
    aktiv_projektek = session.query(Projekt).filter(Projekt.statusz != "Archív").all()
    projekt_valaszto = ttk.Combobox(form_frame,values=[f"{p.id} - {p.munkaszam} - {p.projekt_sorszam or ''} - {p.projekt_megnevezes or ''}" for p in aktiv_projektek],width=50)
    projekt_valaszto.grid(row=16, column=1)

    selected_id = None

    def frissit_lista(szures=""):
        tree.delete(*tree.get_children())
        query = session.query(Alkatresz)

        if show_archived.get():
            query = query.join(ProjektAlkatresz).join(Projekt).filter(Projekt.statusz != "Archív")

        alkatreszek = query.all()

        if sort_column["col"]:
            def sort_key(a):
                value = getattr(a, sort_column["col"])
                if isinstance(value, datetime):
                    return value or datetime.min
                elif isinstance(value, (int, float)):
                    return value if value is not None else float("-inf")
                elif isinstance(value, str):
                    return value.lower()
                elif value is None:
                    return ""  # végső fallback, üres string
                return str(value).lower()  # ha semmi nem illik, próbáljuk stringgé konvertálni
            try:
                alkatreszek.sort(key=sort_key, reverse=sort_column["reverse"])
            except TypeError as e:
                print(f"Hiba a rendezés során: {e}")


        for a in alkatreszek:
            if szures and szures not in (a.nev or '').lower():
                continue
            tree.insert("", "end", iid=a.id, values=(
                a.nev, a.hatarido, a.statusz, a.lemezvastagsag, a.anyag, a.tipus,
                a.gyartando_darab, a.gyartando_tukrozott_darab
            ))

    def on_select(event):
        nonlocal selected_id
        selected = tree.focus()
        if selected:
            a = session.query(Alkatresz).get(int(selected))
            selected_id = a.id
            entries["név"].delete(0, tk.END)
            entries["név"].insert(0, a.nev or "")
            entries["határidő (éééé-hh-nn)"].delete(0, tk.END)
            entries["határidő (éééé-hh-nn)"].insert(0, a.hatarido.strftime("%Y-%m-%d") if a.hatarido else "")
            entries["határidő idő (óó:pp:mm)"].delete(0, tk.END)
            entries["határidő idő (óó:pp:mm)"].insert(0, a.hatarido.strftime("%H:%M:%S") if a.hatarido else "")
            widgets["statusz"].set(a.statusz or "")
            widgets["lemezvastagsag"].set(a.lemezvastagsag or "")
            widgets["anyag"].set(a.anyag or "")
            widgets["tipus"].set(a.tipus or "")
            entries["gyártandó db"].delete(0, tk.END)
            entries["gyártandó db"].insert(0, a.gyartando_darab)
            entries["tükör db"].delete(0, tk.END)
            entries["tükör db"].insert(0, a.gyartando_tukrozott_darab)
            entries["profil hossz"].delete(0, tk.END)
            entries["profil hossz"].insert(0, a.profil_hossz or 0)
            entries["felszín"].delete(0, tk.END)
            entries["felszín"].insert(0, a.felszin or 0)
            entries["tömeg"].delete(0, tk.END)
            entries["tömeg"].insert(0, a.tomeg or 0)
            for k in checkbox_vars:
                checkbox_vars[k].set(getattr(a, k) == "Igen")
            megjegyzes_text.delete("1.0", tk.END)
            megjegyzes_text.insert("1.0", a.irodai_megjegyzes or "")

            # Technológiák
            feladatok = session.query(Feladat).filter_by(alkatresz_id=a.id).all()
            for tech in tech_vars:
                tech_vars[tech].set(False)
            for f in feladatok:
                if f.technologia_tipus in tech_vars:
                    tech_vars[f.technologia_tipus].set(True)

            # Projekt munkaszám (ez volt a hibás rész!)
            kapcsolat = session.query(ProjektAlkatresz).filter_by(alkatresz_id=a.id).first()
            if kapcsolat:
                projekt = session.query(Projekt).get(kapcsolat.projekt_id)
                projekt_valaszto.set(f"{projekt.id} - {projekt.munkaszam} - {projekt.projekt_sorszam or ''} - {projekt.projekt_megnevezes or ''}")
            else:
                projekt_valaszto.set("")


    # a további függvények (ment, hozzaad, torol, stb.) maradnak ahogy voltak

    def ment():
        if selected_id:
            a = session.query(Alkatresz).get(selected_id)  # <- EZT ELŐRE HOZZUK
            if not messagebox.askyesno("Megerősítés", f"Biztosan felül szeretnéd írni a(z) \"{a.nev}\" nevű alkatrészt?"):
                return
            a.nev = entries["név"].get()
            datum_str = entries["határidő (éééé-hh-nn)"].get()
            ido_str = entries["határidő idő (óó:pp:mm)"].get() or "00:00:00"
            try:
                a.hatarido = datetime.strptime(f"{datum_str} {ido_str}", "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror("Hiba", "Hibás dátum vagy idő formátum. Elvárt: ÉÉÉÉ-HH-NN és ÓÓ:PP:MM")
                return
            a.statusz = widgets["statusz"].get()
            a.lemezvastagsag = widgets["lemezvastagsag"].get()
            a.anyag = widgets["anyag"].get()
            a.tipus = widgets["tipus"].get()
            a.gyartando_darab = int(entries["gyártandó db"].get() or 0)
            a.gyartando_tukrozott_darab = int(entries["tükör db"].get() or 0)
            a.profil_hossz = float(entries["profil hossz"].get() or 0)
            a.felszin = float(entries["felszín"].get() or 0)
            a.tomeg = float(entries["tömeg"].get() or 0)
            for k, v in checkbox_vars.items():
                setattr(a, k, "Igen" if v.get() else "Nem")
            a.irodai_megjegyzes = megjegyzes_text.get("1.0", tk.END).strip()

            session.query(Feladat).filter_by(alkatresz_id=a.id).delete()
            for tech, val in tech_vars.items():
                if val.get():
                    session.add(Feladat(alkatresz_id=a.id, technologia_tipus=tech, statusz="Normál"))

            session.commit()
            frissit_lista()
            messagebox.showinfo("Mentve", "A módosítások elmentve.")

    def hozzaad():
        try:
            datum_str = entries["határidő (éééé-hh-nn)"].get()
            ido_str = entries["határidő idő (óó:pp:mm)"].get() or "00:00:00"
            try:
                hatarido = datetime.strptime(f"{datum_str} {ido_str}", "%Y-%m-%d %H:%M:%S") if datum_str else None
            except ValueError:
                messagebox.showerror("Hiba", "Hibás dátum vagy idő formátum. Elvárt: ÉÉÉÉ-HH-NN és ÓÓ:PP:MM")
                return

            uj = Alkatresz(
                nev=entries["név"].get(),
                hatarido=hatarido,
                rogzitett_datum=datetime.now(),
                statusz=widgets["statusz"].get(),
                lemezvastagsag=widgets["lemezvastagsag"].get(),
                anyag=widgets["anyag"].get(),
                tipus=widgets["tipus"].get(),
                gyartando_darab=int(entries["gyártandó db"].get() or 0),
                gyartando_tukrozott_darab=int(entries["tükör db"].get() or 0),
                profil_hossz=float(entries["profil hossz"].get() or 0),
                felszin=float(entries["felszín"].get() or 0),
                tomeg=float(entries["tömeg"].get() or 0),
                irodai_megjegyzes=megjegyzes_text.get("1.0", tk.END).strip(),
                **{k: "Igen" if v.get() else "Nem" for k, v in checkbox_vars.items()}
            )
            session.add(uj)
            session.commit()

            projekt_szoveg = projekt_valaszto.get()
            if projekt_szoveg:
                projekt_id = int(projekt_szoveg.split(" - ")[0].strip())
                kapcsolat = ProjektAlkatresz(projekt_id=projekt_id, alkatresz_id=uj.id)
                session.add(kapcsolat)

            for tech, val in tech_vars.items():
                if val.get():
                    session.add(Feladat(alkatresz_id=uj.id, technologia_tipus=tech, statusz="Normál"))

            session.commit()
            frissit_lista()
            messagebox.showinfo("Siker", "Alkatrész rögzítve és projekthez rendelve.")
        except Exception as e:
            messagebox.showerror("Hiba", str(e))

    def torol():
        nonlocal selected_id
        if selected_id:
            alkatresz = session.query(Alkatresz).get(selected_id)
            if not alkatresz:
                messagebox.showerror("Hiba", "A kiválasztott alkatrész nem található.")
                return

            if not messagebox.askyesno("Törlés megerősítése", f"Biztosan törölni szeretnéd a(z) \"{alkatresz.nev}\" nevű alkatrészt?"):
                return

            session.query(Feladat).filter_by(alkatresz_id=selected_id).delete()
            kapcsolat = session.query(ProjektAlkatresz).filter_by(alkatresz_id=selected_id).first()
            if kapcsolat:
                session.delete(kapcsolat)
            session.delete(alkatresz)
            session.commit()
            frissit_lista()
            selected_id = None


    tree.bind("<<TreeviewSelect>>", on_select)

    btn_frame = tk.Frame(window)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Mentés", command=ment).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Hozzáadás", command=hozzaad).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Törlés", command=torol).grid(row=0, column=2, padx=5)

    frissit_lista()
    window.mainloop()

if __name__ == "__main__":
    part_view()
