import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import sessionmaker
from database.connection import engine
from models import Projekt, Felhasznalo

Session = sessionmaker(bind=engine)
session = Session()

def project_view():
    window = tk.Toplevel()
    window.title("Projektek kezelése")
    window.geometry("1000x700")

    tk.Label(window, text="Projektek listája", font=("Arial", 12)).pack(pady=10)

    # Keresés és szűrés
    search_frame = tk.Frame(window)
    search_frame.pack(pady=5)

    tk.Label(search_frame, text="Keresés: ").grid(row=0, column=0)
    search_entry = tk.Entry(search_frame)
    search_entry.grid(row=0, column=1)

    tk.Label(search_frame, text="Státusz szűrés: ").grid(row=0, column=2)
    statusz_filter = ttk.Combobox(search_frame, values=["", "Aktív", "Archív", "Blokkolva"], width=12)
    statusz_filter.grid(row=0, column=3)

    felhasznalok = session.query(Felhasznalo).all()
    tk.Label(search_frame, text="Projektvezető szűrés: ").grid(row=0, column=4)
    projektvezeto_filter = ttk.Combobox(search_frame, values=[""] + [f.nev for f in felhasznalok], width=20)
    projektvezeto_filter.grid(row=0, column=5)

    # Treeview
    tree = ttk.Treeview(window, columns=("munkaszam", "megnevezes", "projektvezeto", "statusz"), show="headings")
    tree.heading("munkaszam", text="Munkaszám", command=lambda: rendezes("munkaszam"))
    tree.heading("megnevezes", text="Megnevezés", command=lambda: rendezes("projekt_megnevezes"))
    tree.heading("projektvezeto", text="Projektvezető", command=lambda: rendezes("projektvezeto"))
    tree.heading("statusz", text="Státusz", command=lambda: rendezes("statusz"))
    tree.pack(pady=5, fill=tk.BOTH, expand=True)

    form_frame = tk.Frame(window)
    form_frame.pack(pady=10)

    tk.Label(form_frame, text="Munkaszám:").grid(row=0, column=0, sticky="e")
    munkaszam_entry = tk.Entry(form_frame)
    munkaszam_entry.grid(row=0, column=1)

    tk.Label(form_frame, text="Projekt sorszám:").grid(row=1, column=0, sticky="e")
    sorszam_entry = tk.Entry(form_frame)
    sorszam_entry.grid(row=1, column=1)

    tk.Label(form_frame, text="Megnevezés:").grid(row=2, column=0, sticky="e")
    megnev_entry = tk.Entry(form_frame)
    megnev_entry.grid(row=2, column=1)

    tk.Label(form_frame, text="Projektvezető:").grid(row=3, column=0, sticky="e")
    vezeto_combo = ttk.Combobox(form_frame, values=[f"{f.id} - {f.nev}" for f in felhasznalok])
    vezeto_combo.grid(row=3, column=1)

    tk.Label(form_frame, text="Státusz:").grid(row=4, column=0, sticky="e")
    statusz_combo = ttk.Combobox(form_frame, values=["Aktív", "Archív", "Blokkolva"])
    statusz_combo.grid(row=4, column=1)

    tk.Label(form_frame, text="Utalt idő:").grid(row=5, column=0, sticky="e")
    utalt_entry = tk.Entry(form_frame)
    utalt_entry.grid(row=5, column=1)

    tk.Label(form_frame, text="Alakadó felszín:").grid(row=6, column=0, sticky="e")
    felszin_entry = tk.Entry(form_frame)
    felszin_entry.grid(row=6, column=1)

    selected_id = None
    aktualis_projektek = []
    szurt_lista = []
    rendezes_irany = True

    def frissit_lista(szures=False):
        nonlocal aktualis_projektek, szurt_lista
        tree.delete(*tree.get_children())
        projektek = session.query(Projekt).all()
        aktualis_projektek = projektek

        szoveg = search_entry.get().lower()
        statusz_szurt = statusz_filter.get()
        vezeto_szurt = projektvezeto_filter.get()

        eredmeny = []
        for p in projektek:
            projektvezeto = session.query(Felhasznalo).filter_by(id=p.projektvezeto_id).first()
            nev = projektvezeto.nev if projektvezeto else ""
            if szoveg and szoveg not in (p.munkaszam or '').lower() and szoveg not in (p.projekt_megnevezes or '').lower():
                continue
            if statusz_szurt and p.statusz != statusz_szurt:
                continue
            if vezeto_szurt and nev != vezeto_szurt:
                continue
            eredmeny.append(p)

        szurt_lista = eredmeny if szures else projektek

        for p in szurt_lista:
            projektvezeto = session.query(Felhasznalo).filter_by(id=p.projektvezeto_id).first()
            nev = projektvezeto.nev if projektvezeto else "-"
            tree.insert("", "end", iid=p.id, values=(p.munkaszam, p.projekt_megnevezes, nev, p.statusz))

    def on_tree_select(event):
        nonlocal selected_id
        selected_item = tree.focus()
        if selected_item:
            selected_id = int(selected_item)
            projekt = session.query(Projekt).get(selected_id)
            munkaszam_entry.delete(0, tk.END)
            munkaszam_entry.insert(0, projekt.munkaszam)
            sorszam_entry.delete(0, tk.END)
            sorszam_entry.insert(0, projekt.projekt_sorszam)
            megnev_entry.delete(0, tk.END)
            megnev_entry.insert(0, projekt.projekt_megnevezes)
            vezeto = session.query(Felhasznalo).filter_by(id=projekt.projektvezeto_id).first()
            vezeto_combo.set(f"{vezeto.id} - {vezeto.nev}" if vezeto else "")
            statusz_combo.set(projekt.statusz or "")
            utalt_entry.delete(0, tk.END)
            utalt_entry.insert(0, projekt.utalt_ido or "")
            felszin_entry.delete(0, tk.END)
            felszin_entry.insert(0, projekt.alakado_felszin or "")

    def ment():
        nonlocal selected_id
        if selected_id is not None:
            projekt = session.query(Projekt).get(selected_id)
            projekt.munkaszam = munkaszam_entry.get()
            projekt.projekt_sorszam = sorszam_entry.get()
            projekt.projekt_megnevezes = megnev_entry.get()
            projekt.projektvezeto_id = int(vezeto_combo.get().split(" - ")[0])
            uj_statusz = statusz_combo.get()
            projekt.statusz = uj_statusz
            projekt.utalt_ido = float(utalt_entry.get() or 0)
            projekt.alakado_felszin = float(felszin_entry.get() or 0)
            session.commit()

            # Friss lekérdezés után kezdjük a státuszlogikát
            projekt = session.query(Projekt).get(selected_id)
            for kapcsolat in projekt.projekt_alkatreszek:
                alkatresz = kapcsolat.alkatresz
                if not alkatresz.felulirt_statusz:
                    alkatresz.statusz = "Blokkolva" if uj_statusz == "Blokkolva" else "Normál"
                for feladat in alkatresz.feladatok:
                    if not feladat.felulirt_statusz:
                        feladat.statusz = "Blokkolva" if uj_statusz == "Blokkolva" else "Normál"

            session.commit()
            messagebox.showinfo("Mentve", "A projekt frissítve lett.")
            frissit_lista()

    def hozzaad():
        uj = Projekt(
            munkaszam=munkaszam_entry.get(),
            projekt_sorszam=sorszam_entry.get(),
            projekt_megnevezes=megnev_entry.get(),
            projektvezeto_id=int(vezeto_combo.get().split(" - ")[0]),
            statusz=statusz_combo.get(),
            utalt_ido=float(utalt_entry.get() or 0),
            alakado_felszin=float(felszin_entry.get() or 0)
        )
        session.add(uj)
        session.commit()
        frissit_lista()

        for kapcsolat in uj.projekt_alkatreszek:
            alkatresz = kapcsolat.alkatresz
            alkatresz.statusz = "Blokkolva"
            alkatresz.felulirt_statusz = False
            for feladat in alkatresz.feladatok:
                feladat.statusz = "Blokkolva"
                feladat.felulirt_statusz = False

        for kapcsolat in uj.projekt_alkatreszek:
            alkatresz = kapcsolat.alkatresz
            if not alkatresz.felulirt_statusz:
                alkatresz.statusz = "Normál"
            for feladat in alkatresz.feladatok:
                if not feladat.felulirt_statusz:
                    feladat.statusz = "Normál"

    def torol():
        nonlocal selected_id
        if selected_id is not None:
            if messagebox.askyesno("Törlés megerősítése", "Biztosan törölni szeretnéd ezt a projektet?"):
                projekt = session.query(Projekt).get(selected_id)
                session.delete(projekt)
                session.commit()
                selected_id = None
                frissit_lista()

    def keres():
        frissit_lista(szures=True)

    def szurok_torlese():
        search_entry.delete(0, tk.END)
        statusz_filter.set("")
        projektvezeto_filter.set("")
        frissit_lista()

    def rendezes(mezo):
        nonlocal szurt_lista, rendezes_irany

        def kulcs(p):
            if mezo == "projektvezeto":
                f = session.query(Felhasznalo).filter_by(id=p.projektvezeto_id).first()
                return f.nev if f else ""
            return getattr(p, mezo, "") or ""

        szurt_lista.sort(key=kulcs, reverse=not rendezes_irany)
        rendezes_irany = not rendezes_irany

        tree.delete(*tree.get_children())
        for p in szurt_lista:
            projektvezeto = session.query(Felhasznalo).filter_by(id=p.projektvezeto_id).first()
            nev = projektvezeto.nev if projektvezeto else "-"
            tree.insert("", "end", iid=p.id, values=(p.munkaszam, p.projekt_megnevezes, nev, p.statusz))

    tk.Button(search_frame, text="Szűrés", command=keres).grid(row=0, column=6, padx=10)
    tk.Button(search_frame, text="Szűrők törlése", command=szurok_torlese).grid(row=0, column=7)

    button_frame = tk.Frame(window)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Mentés", command=ment).grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="Hozzáadás", command=hozzaad).grid(row=0, column=1, padx=5)
    tk.Button(button_frame, text="Törlés", command=torol).grid(row=0, column=2, padx=5)

    tree.bind("<<TreeviewSelect>>", on_tree_select)

    frissit_lista()
    window.mainloop()

if __name__ == "__main__":
    project_view()
