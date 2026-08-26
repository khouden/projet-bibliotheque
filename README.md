# projet-bibliotheque

Application de bureau de **gestion de bibliothèque** — Python / Tkinter / SQLite.
Projet réalisé par Abdellah Khouden, Abderrahim Bensaid et Othman Elhyane (encadré par Mr. Abdellah Sair).

## Fonctionnalités

- **Connexion** sécurisée (mot de passe haché PBKDF2-SHA256)
- **Livres** : ajouter, lister / rechercher / trier, modifier, supprimer
- **Adhérents** : ajouter, lister / rechercher / trier, modifier, supprimer
- **Emprunts** : prendre un livre, retourner un livre, lister / rechercher

Aucun serveur requis : la base SQLite `bibliotheque.db` est créée automatiquement au premier lancement.

## Prérequis

- [Python 3.10+](https://www.python.org/downloads/) (cocher *Add to PATH* à l'installation)

## Installation et lancement

```powershell
pip install -r requirements.txt
python main.py
```

Identifiants par défaut : **admin** / **admin**

> Pour réinitialiser l'application : supprimer `bibliotheque.db`, elle sera recréée au prochain démarrage.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `main.py` | Point d'entrée : initialise la base puis lance l'écran de connexion |
| `login.py` | Écran de connexion |
| `mainMenu.py` | Menu principal et navigation entre les pages |
| `livre.py` | Pages livres (afficher / ajouter / modifier) |
| `adherent.py` | Pages adhérents (afficher / ajouter / modifier) |
| `emprunt.py` | Pages emprunts (lister / prendre / retourner) |
| `db.py` | Couche base de données SQLite + hachage des mots de passe |
| `paths.py` | Résolution des chemins d'images (compatible exécutable PyInstaller) |
