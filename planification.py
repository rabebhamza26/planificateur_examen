from constraint import Problem, AllDifferentConstraint, AllEqualConstraint
from datetime import time, timedelta
from dataclasses import dataclass
from typing import List, Dict, Set


@dataclass
class ExamenCSP:
    """Classe représentant un examen pour CSP"""
    nom: str
    duree: int  # en heures
    enseignants: List[str]
    etudiants: List[str]


@dataclass
class SalleCSP:
    """Classe représentant une salle pour CSP"""
    nom: str
    capacite: int
    disponibilites: List[tuple]  # [(8,0), (18,0)]


class PlanificateurCSP:
    """Planificateur d'examens utilisant CSP"""

    def __init__(self):
        self.problem = Problem()
        self.variables = []  # Noms des variables (examens)
        self.domains = {}  # Domaines pour chaque variable

    def creer_creneaux(self, debut: time, fin: time, duree_creneau: int = 2):
        """Crée les créneaux horaires"""
        creneaux = []
        current = debut.hour
        while current + duree_creneau <= fin.hour:
            creneaux.append((current, current + duree_creneau))
            current += duree_creneau
        return creneaux

    def preparer_domaines(self, examens: List[ExamenCSP],
                          salles: List[SalleCSP],
                          creneaux: List[tuple]):
        """Prépare les domaines pour chaque variable"""
        # Pour chaque examen, créer un domaine de tuples (creneau, salle, enseignant)
        for examen in examens:
            domaine = []

            for creneau in creneaux:
                heure_debut, heure_fin = creneau

                # Vérifier si l'examen peut tenir dans le créneau
                if heure_fin - heure_debut < examen.duree:
                    continue

                for salle in salles:
                    # Vérifier capacité de la salle
                    if salle.capacite < len(examen.etudiants):
                        continue

                    # Vérifier disponibilité de la salle
                    salle_disponible = False
                    for dispo in salle.disponibilites:
                        dispo_debut, dispo_fin = dispo
                        if heure_debut >= dispo_debut and heure_fin <= dispo_fin:
                            salle_disponible = True
                            break

                    if not salle_disponible:
                        continue

                    for enseignant in examen.enseignants:
                        domaine.append((creneau, salle.nom, enseignant))

            if domaine:
                self.variables.append(examen.nom)
                self.domains[examen.nom] = domaine

        return self.variables

    def ajouter_contraintes(self, examens: List[ExamenCSP], prerequis: List[tuple] = None):
        """Ajoute toutes les contraintes au problème CSP"""
        if prerequis is None:
            prerequis = []

        # Ajouter les variables avec leurs domaines
        for var_name in self.variables:
            self.problem.addVariable(var_name, self.domains[var_name])

        # 1. Contrainte: Pas deux examens dans la même salle au même créneau
        for i, exam1 in enumerate(examens):
            for j, exam2 in enumerate(examens):
                if i < j:
                    def salle_creneau_conflit(val1, val2, exam1=exam1, exam2=exam2):
                        creneau1, salle1, _ = val1
                        creneau2, salle2, _ = val2

                        # Même créneau et même salle = conflit
                        if creneau1 == creneau2 and salle1 == salle2:
                            return False
                        return True

                    self.problem.addConstraint(salle_creneau_conflit, [exam1.nom, exam2.nom])

        # 2. Contrainte: Un enseignant ne peut surveiller qu'un examen à la fois
        for i, exam1 in enumerate(examens):
            for j, exam2 in enumerate(examens):
                if i < j:
                    def enseignant_conflit(val1, val2, exam1=exam1, exam2=exam2):
                        creneau1, _, enseignant1 = val1
                        creneau2, _, enseignant2 = val2

                        # Même enseignant et même créneau = conflit
                        if creneau1 == creneau2 and enseignant1 == enseignant2:
                            return False
                        return True

                    self.problem.addConstraint(enseignant_conflit, [exam1.nom, exam2.nom])

        # 3. Contrainte: Un étudiant ne peut avoir deux examens en même temps
        for i, exam1 in enumerate(examens):
            for j, exam2 in enumerate(examens):
                if i < j:
                    # Vérifier s'il y a des étudiants en commun
                    etudiants_communs = set(exam1.etudiants) & set(exam2.etudiants)
                    if etudiants_communs:
                        def etudiant_conflit(val1, val2, exam1=exam1, exam2=exam2):
                            creneau1, _, _ = val1
                            creneau2, _, _ = val2

                            # Même créneau et étudiants en commun = conflit
                            if creneau1 == creneau2:
                                return False
                            return True

                        self.problem.addConstraint(etudiant_conflit, [exam1.nom, exam2.nom])

        # 4. Contrainte: Vérifier que l'enseignant est dans la liste des enseignants autorisés
        for examen in examens:
            def enseignant_autorise(val, examen=examen):
                _, _, enseignant = val
                return enseignant in examen.enseignants

            self.problem.addConstraint(enseignant_autorise, [examen.nom])

        # 5. Contraintes de prérequis (ex: Maths doit être avant Programmation)
        for prerequi in prerequis:
            examen_avant, examen_apres = prerequi

            # Trouver les objets examens correspondants
            exam_avant_obj = next((e for e in examens if e.nom == examen_avant), None)
            exam_apres_obj = next((e for e in examens if e.nom == examen_apres), None)

            if exam_avant_obj and exam_apres_obj:
                def contrainte_prerequis(val_avant, val_apres):
                    creneau_avant, _, _ = val_avant
                    creneau_apres, _, _ = val_apres

                    # L'examen "avant" doit finir avant ou au moment où l'examen "après" commence
                    heure_fin_avant = creneau_avant[1]  # heure de fin du créneau avant
                    heure_debut_apres = creneau_apres[0]  # heure de début du créneau après

                    return heure_fin_avant <= heure_debut_apres

                self.problem.addConstraint(contrainte_prerequis, [examen_avant, examen_apres])
                print(f"Contrainte ajoutée: {examen_avant} avant {examen_apres}")

    def resoudre(self):
        """Résout le problème CSP"""
        solutions = self.problem.getSolutions()
        return solutions

    def afficher_solution(self, solution: Dict, examens: List[ExamenCSP]):
        """Affiche une solution"""
        print("\n" + "=" * 60)
        print("SOLUTION CSP - PLANNING DES EXAMENS")
        print("=" * 60)

        # Trier par créneau
        sorted_items = sorted(solution.items(),
                              key=lambda x: x[1][0][0])  # tri par heure de début

        for examen_nom, (creneau, salle, enseignant) in sorted_items:
            heure_debut, heure_fin = creneau
            print(f"\n{examen_nom.upper()}")
            print(f"  Heure: {heure_debut:02d}:00 - {heure_fin:02d}:00")
            print(f"  Salle: {salle}")
            print(f"  Enseignant: {enseignant}")

            # Afficher les informations supplémentaires
            examen_obj = next((e for e in examens if e.nom == examen_nom), None)
            if examen_obj:
                print(f"  Durée: {examen_obj.duree}h")


            print("-" * 40)


def exemple_utilisation_csp():
    """Exemple d'utilisation du planificateur CSP"""

    # Création des examens
    examens = [
        ExamenCSP(
            nom="Maths",
            duree=2,
            enseignants=["Dr_Ali", "Dr_Salem"],
            etudiants=["ET001", "ET002", "ET003", "ET004", "ET005"]
        ),
        ExamenCSP(
            nom="Programmation",
            duree=2,
            enseignants=["Dr_Salma", "Dr_Mehdi"],
            etudiants=["ET001", "ET002", "ET006", "ET007", "ET008"]
        ),
        ExamenCSP(
            nom="Bases_Donnees",
            duree=2,
            enseignants=["Dr_Mehdi", "Dr_Ali"],
            etudiants=["ET003", "ET004", "ET006", "ET009", "ET010"]
        ),
        ExamenCSP(
            nom="Genie_Logiciel",
            duree=2,
            enseignants=["Dr_Ali", "Dr_Salma"],
            etudiants=["ET005", "ET007", "ET008", "ET009", "ET010"]
        )
    ]

    # Création des salles
    salles = [
        SalleCSP(nom="Salle_A", capacite=30, disponibilites=[(8, 18)]),
        SalleCSP(nom="Salle_B", capacite=25, disponibilites=[(8, 18)]),
        SalleCSP(nom="Salle_C", capacite=20, disponibilites=[(8, 18)]),
        SalleCSP(nom="Salle_D", capacite=15, disponibilites=[(8, 18)])
    ]

    # Définir les prérequis: Maths doit être avant Programmation
    prerequis = [("Maths", "Programmation")]

    # Créer le planificateur CSP
    planificateur = PlanificateurCSP()

    # Créer les créneaux (8h-18h, créneaux de 2h)
    creneaux = planificateur.creer_creneaux(time(8, 0), time(18, 0), 2)
    print(f"Creneaux disponibles: {creneaux}")

    # Préparer les domaines
    variables = planificateur.preparer_domaines(examens, salles, creneaux)
    print(f"Variables (examens) à planifier: {variables}")

    # Ajouter les contraintes AVEC prérequis
    print("\nAjout des contraintes...")
    planificateur.ajouter_contraintes(examens, prerequis)

    # Résoudre le problème
    print("\nRecherche de solutions CSP...")
    solutions = planificateur.resoudre()

    if solutions:
        print(f"\n✅ {len(solutions)} solution(s) trouvée(s)")

        # Afficher la première solution
        planificateur.afficher_solution(solutions[0], examens)

        # Vérifier que la contrainte de prérequis est respectée
        print("\n" + "=" * 60)
        print("VÉRIFICATION DES PRÉREQUIS")
        print("=" * 60)

        solution = solutions[0]
        creneau_maths = solution["Maths"][0]
        creneau_prog = solution["Programmation"][0]

        print(f"Maths: {creneau_maths[0]:02d}:00-{creneau_maths[1]:02d}:00")
        print(f"Programmation: {creneau_prog[0]:02d}:00-{creneau_prog[1]:02d}:00")

        if creneau_maths[1] <= creneau_prog[0]:
            print("✅ Contrainte respectée: Maths avant Programmation")
        else:
            print("❌ ERREUR: Contrainte non respectée!")

        # Option: afficher d'autres solutions
        if len(solutions) > 1:
            print(f"\nAutres solutions disponibles ({len(solutions) - 1} au total)")
            reponse = input("Voulez-vous voir une autre solution? (o/n): ")
            if reponse.lower() == 'o':
                planificateur.afficher_solution(solutions[1], examens)
    else:
        print("\n❌ Aucune solution trouvée avec les contraintes actuelles")

        # Suggestions pour relâcher les contraintes
        print("\nSuggestions:")
        print("1. Ajouter plus de salles")
        print("2. Ajouter plus de créneaux horaires")
        print("3. Ajouter plus d'enseignants disponibles")
        print("4. Réduire le nombre d'étudiants par examen")
        print("5. Relâcher les contraintes de prérequis")


def exemple_avec_plusieurs_prerequis():
    """Exemple avec plusieurs contraintes de prérequis"""
    print("\n" + "=" * 60)
    print("EXEMPLE AVEC PLUSIEURS PRÉREQUIS")
    print("=" * 60)

    examens = [
        ExamenCSP("Algebre", 2, ["Dr_Ali"], ["ET001", "ET002", "ET003"]),
        ExamenCSP("Analyse", 2, ["Dr_Salem"], ["ET001", "ET004", "ET005"]),
        ExamenCSP("Programmation", 2, ["Dr_Salma"], ["ET002", "ET004", "ET006"]),
        ExamenCSP("Bases_Donnees", 2, ["Dr_Mehdi"], ["ET003", "ET005", "ET006"]),
        ExamenCSP("Reseaux", 2, ["Dr_Ali", "Dr_Salma"], ["ET001", "ET003", "ET005"])
    ]

    salles = [
        SalleCSP("Salle_A", 30, [(8, 18)]),
        SalleCSP("Salle_B", 25, [(8, 18)]),
        SalleCSP("Salle_C", 20, [(8, 18)])
    ]

    # Plusieurs prérequis: Algèbre avant Programmation ET Analyse avant Bases de Données
    prerequis = [
        ("Algebre", "Programmation"),
        ("Analyse", "Bases_Donnees")
    ]

    planificateur = PlanificateurCSP()
    creneaux = planificateur.creer_creneaux(time(8, 0), time(18, 0), 2)

    planificateur.preparer_domaines(examens, salles, creneaux)
    planificateur.ajouter_contraintes(examens, prerequis)

    solutions = planificateur.resoudre()

    if solutions:
        print(f"✅ {len(solutions)} solution(s) avec prérequis multiples")
        planificateur.afficher_solution(solutions[0], examens)

        # Vérification des prérequis
        solution = solutions[0]
        print("\nVérification des prérequis:")

        for avant, apres in prerequis:
            creneau_avant = solution[avant][0]
            creneau_apres = solution[apres][0]

            if creneau_avant[1] <= creneau_apres[0]:
                print(f"✅ {avant} ({creneau_avant[0]:02d}:00) avant {apres} ({creneau_apres[0]:02d}:00)")
            else:
                print(f"❌ {avant} N'EST PAS avant {apres}")
    else:
        print("❌ Aucune solution avec ces prérequis")


def main_csp():
    """Fonction principale pour CSP"""
    print("=" * 60)
    print("PLANIFICATEUR D'EXAMENS AVEC CSP (Constraint Satisfaction Problem)")
    print("Polytech Monastir - Paradigmes de Programmation")
    print("=" * 60)

    exemple_utilisation_csp()

    exemple_avec_plusieurs_prerequis()

    # Exemple plus complexe
    print("\n" + "=" * 60)
    print("EXEMPLE AVEC PLUS DE CONTRAINTES")
    print("=" * 60)

    # Ajouter une contrainte: certains examens ne peuvent pas être à certaines heures
    examens_supp = [
        ExamenCSP(
            nom="Reseaux",
            duree=2,
            enseignants=["Dr_Ali"],
            etudiants=["ET011", "ET012", "ET013"]
        ),
        ExamenCSP(
            nom="Securite",
            duree=2,
            enseignants=["Dr_Salma"],
            etudiants=["ET014", "ET015", "ET016"]
        )
    ]

    salles_supp = [
        SalleCSP(nom="Amphi", capacite=100, disponibilites=[(8, 12)]),  # Dispo seulement le matin
        SalleCSP(nom="Labo", capacite=20, disponibilites=[(14, 18)])  # Dispo seulement l'après-midi
    ]

    planificateur2 = PlanificateurCSP()
    creneaux2 = planificateur2.creer_creneaux(time(8, 0), time(18, 0), 2)

    # Ajouter une contrainte supplémentaire: l'amphi ne peut pas être utilisé après 12h
    def contrainte_amphi_matin(val):
        creneau, salle, _ = val
        heure_debut, _ = creneau
        if salle == "Amphi" and heure_debut >= 12:
            return False
        return True

    for examen in examens_supp:
        planificateur2.problem.addVariable(examen.nom,
                                           [(c, s.nom, e)
                                            for c in creneaux2
                                            for s in salles_supp
                                            for e in examen.enseignants])
        planificateur2.problem.addConstraint(contrainte_amphi_matin, [examen.nom])

    print("\nAvec contraintes supplémentaires (amphi seulement le matin)...")
    solutions2 = planificateur2.resoudre()
    print(f"Solutions trouvées: {len(solutions2)}")


if __name__ == "__main__":
    main_csp()