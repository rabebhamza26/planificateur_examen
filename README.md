# Planificateur d'Examens 

Ce projet est une interface Python utilisant Tkinter pour générer un planning d'examens , en respectant toutes les contraintes du problème de satisfaction de contraintes (CSP).

## Contexte

Chaque examen doit être planifié :  
- À un horaire spécifique  
- Dans une salle particulière  
- En respectant les contraintes suivantes :  
  - Aucun étudiant ne peut avoir deux examens en même temps.  
  - Aucun enseignant ne peut surveiller deux examens en même temps.  
  - Les salles ont une capacité maximale et chaque examen doit être placé dans une salle appropriée.  
  - Certains examens ont des prérequis (doivent être planifiés avant un autre examen).  
  - Certains enseignants ont des disponibilités horaires.

## Fonctionnalités

- Saisie des examens (nom, durée, enseignants, étudiants)
- Saisie des salles (nom, capacité)
- Gestion des prérequis entre examens
- Résolution automatique via CSP
- Visualisation du planning dans un tableau
- Zone de messages pour indiquer la solution

## Installation

Installer les dépendances : pip install -r requirements.txt

Exécution : python interface.py


<img width="1280" height="679" alt="image" src="https://github.com/user-attachments/assets/d9738be5-4d48-4fef-b52a-7058597e6caf" />

