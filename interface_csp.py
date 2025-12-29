import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import time

from projet_csp.planification import ExamenCSP, SalleCSP, PlanificateurCSP

class CSPInterface(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Planificateur d'Examens")
        self.geometry("950x750")
        self.configure(bg="#f0f2f5")

        tk.Label(self, text="Planificateur d’Examens", font=("Arial", 20, "bold"), bg="#f0f2f5").pack(pady=10)

        # ================== EXAMENS ==================
        frame_exam = tk.LabelFrame(self, text="Examens", font=("Arial", 12, "bold"), padx=10, pady=10, bg="#f0f2f5")
        frame_exam.pack(pady=10, fill="x", padx=20)

        tk.Label(frame_exam, text="Nom", bg="#f0f2f5").grid(row=0, column=0, sticky="w")
        self.exam_nom = tk.Entry(frame_exam, width=20)
        self.exam_nom.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_exam, text="Durée (h)", bg="#f0f2f5").grid(row=0, column=2, sticky="w")
        self.exam_duree = tk.Entry(frame_exam, width=10)
        self.exam_duree.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(frame_exam, text="Enseignants (séparés par '|')", bg="#f0f2f5").grid(row=1, column=0, sticky="w")
        self.exam_ens = tk.Entry(frame_exam, width=50)
        self.exam_ens.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        tk.Label(frame_exam, text="Étudiants (séparés par '|')", bg="#f0f2f5").grid(row=2, column=0, sticky="w")
        self.exam_etu = tk.Entry(frame_exam, width=50)
        self.exam_etu.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        # ================== SALLES ==================
        frame_salle = tk.LabelFrame(self, text="Salles", font=("Arial", 12, "bold"), padx=10, pady=10, bg="#f0f2f5")
        frame_salle.pack(pady=10, fill="x", padx=20)

        tk.Label(frame_salle, text="Nom Salle", bg="#f0f2f5").grid(row=0, column=0, sticky="w")
        self.salle_nom = tk.Entry(frame_salle, width=20)
        self.salle_nom.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_salle, text="Capacité", bg="#f0f2f5").grid(row=0, column=2, sticky="w")
        self.salle_cap = tk.Entry(frame_salle, width=10)
        self.salle_cap.grid(row=0, column=3, padx=5, pady=5)

        # ================== PRÉREQUIS ==================
        frame_pre = tk.LabelFrame(self, text="Prérequis", font=("Arial", 12, "bold"), padx=10, pady=10, bg="#f0f2f5")
        frame_pre.pack(pady=10, fill="x", padx=20)

        tk.Label(frame_pre, text="Format: Examen1>Examen2", bg="#f0f2f5").grid(row=0, column=0, sticky="w")
        self.prerequis = tk.Text(frame_pre, height=3, width=80)
        self.prerequis.grid(row=1, column=0, padx=5, pady=5)

        # ================== BOUTON ==================
        self.btn_resoudre = tk.Button(self, text="Résoudre le CSP", font=("Arial", 14, "bold"),
                                     bg="#4CAF50", fg="white", activebackground="#45a049",
                                     command=self.executer_csp)
        self.btn_resoudre.pack(pady=10)

        # ================== TABLEAU ==================
        frame_table = tk.Frame(self)
        frame_table.pack(pady=10, fill="both", expand=True, padx=20)

        columns = ("Examen", "Créneau", "Salle", "Enseignant")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200, anchor="center")
        self.tree.pack(fill="both", expand=True)

        # ================== MESSAGES ==================
        tk.Label(self, text="Messages:", font=("Arial", 12), bg="#f0f2f5").pack(pady=5)
        self.resultat = scrolledtext.ScrolledText(self, width=100, height=6)
        self.resultat.pack(pady=5, padx=20)

    def executer_csp(self):
        try:
            examens = []
            salles = []
            prerequis = []

            # ----- Examens -----
            nom = self.exam_nom.get().strip()
            duree = self.exam_duree.get().strip()
            ens = self.exam_ens.get().strip()
            etu = self.exam_etu.get().strip()
            if nom and duree and ens and etu:
                examens.append(
                    ExamenCSP(
                        nom=nom,
                        duree=int(duree),
                        enseignants=ens.split("|"),
                        etudiants=etu.split("|")
                    )
                )

            # ----- Salles -----
            nom_salle = self.salle_nom.get().strip()
            capacite = self.salle_cap.get().strip()
            if nom_salle and capacite:
                salles.append(SalleCSP(nom_salle, int(capacite), [(8, 18)]))

            # ----- Prérequis -----
            for ligne in self.prerequis.get("1.0", tk.END).strip().split("\n"):
                if ">" in ligne:
                    a, b = ligne.split(">")
                    prerequis.append((a.strip(), b.strip()))

            # ----- CSP -----
            planificateur = PlanificateurCSP()
            creneaux = planificateur.creer_creneaux(time(8, 0), time(18, 0), 2)
            planificateur.preparer_domaines(examens, salles, creneaux)
            planificateur.ajouter_contraintes(examens, prerequis)
            solutions = planificateur.resoudre()

            self.resultat.delete("1.0", tk.END)
            for i in self.tree.get_children():
                self.tree.delete(i)

            if not solutions:
                self.resultat.insert(tk.END, "❌ Aucune solution trouvée\n")
                return

            sol = solutions[0]
            self.resultat.insert(tk.END, "✅ SOLUTION TROUVÉE\n\n")
            for exam, (creneau, salle, enseignant) in sol.items():
                self.tree.insert("", "end", values=(exam, f"{creneau[0]}h-{creneau[1]}h", salle, enseignant))
                self.resultat.insert(tk.END, f"{exam} : {creneau[0]}h-{creneau[1]}h | {salle} | {enseignant}\n")

        except Exception as e:
            messagebox.showerror("Erreur", str(e))


if __name__ == "__main__":
    app = CSPInterface()
    app.mainloop()
