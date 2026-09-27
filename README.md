# MailForge — Envoi de mails à partir de templates HTML

Petit outil Python pour envoyer des mails HTML personnalisés (CLI ou interface graphique) à partir de templates, avec deux fournisseurs d'envoi au choix : **Resend** (API) ou **Gmail** (Gmail API + OAuth 2.0).

## Fonctionnalités

- Templates HTML avec placeholders `{{ champ }}` détectés automatiquement.
- Deux fournisseurs d'envoi interchangeables via une simple variable d'environnement : `resend` ou `gmail`.
- Interface en ligne de commande (`main.py`) et interface graphique Tkinter (`gui.py`), toutes deux basées sur la même logique d'envoi.
- Logs applicatifs avec rotation automatique (`logs/app.log`).

## Structure du projet

```
.
├── main.py                 # Point d'entrée CLI
├── gui.py                  # Point d'entrée interface graphique (Tkinter)
├── templates/               # Templates HTML des mails ({{ champ }} = placeholder)
├── utils/
│   ├── config.py            # Lecture de la configuration (.env)
│   ├── logger.py             # Logger applicatif (fichier + console)
│   ├── template.py           # Détection des templates et de leurs champs
│   ├── mail.py                # Dispatch de l'envoi (Resend / Gmail)
│   ├── gmail.py                # Envoi via l'API Gmail
│   └── googleAuth.py           # Authentification OAuth 2.0 Gmail
├── .env.example              # Exemple de configuration
└── requirements.txt
```

## Prérequis

- Python 3.10+
- Un compte [Resend](https://resend.com) **ou** un projet [Google Cloud](https://console.cloud.google.com) avec la Gmail API activée (selon le fournisseur choisi)

## Installation rapide (Windows)

Double-clique sur `Installer_et_Lancer.bat` :

- Premier lancement : crée le `.venv`, installe les dépendances, demande le fournisseur d'envoi (**Resend** *ou* **Gmail**, pas les deux), le domaine d'expédition, le fichier `credentials.json` (si Gmail) et propose un dossier de templates personnalisé (ex. sur `C:\`). Écrit tout ça dans `.env`.
- Lancements suivants : détecte que tout est déjà configuré et ouvre directement l'interface graphique.

## Installation (manuelle / autres OS)

```bash
git clone <url-du-repo>
cd MailForge

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

Copie ensuite le fichier d'exemple de configuration :

```bash
cp .env.example .env
```

## Configuration (`.env`)

| Variable | Description |
|---|---|
| `MAIL_PROVIDER` | Fournisseur d'envoi : `resend` ou `gmail` |
| `RESEND_API_KEY` | Clé API Resend (si `MAIL_PROVIDER=resend`) |
| `MAIL_DOMAINE` | Domaine utilisé pour construire l'adresse expéditeur (`nom@domaine`) |
| `GMAIL_CREDENTIALS_FILE` | Chemin du fichier client OAuth (défaut : `credentials.json`) |
| `GMAIL_TOKEN_FILE` | Chemin du token généré après autorisation (défaut : `token.json`) |
| `LOG_MAX_SIZE_MB` | Taille max d'un fichier de log avant rotation |
| `LOG_BACKUP_COUNT` | Nombre de fichiers de log conservés (`-1` = illimité) |
| `TEMPLATES_DIR` | Dossier contenant les templates HTML |

### Option A — Fournisseur Resend

1. Crée un compte sur [resend.com](https://resend.com) et récupère une clé API.
2. Renseigne `RESEND_API_KEY` et `MAIL_DOMAINE` dans `.env`.
3. `MAIL_PROVIDER=resend`.

### Option B — Fournisseur Gmail (API + OAuth 2.0)

L'envoi passe par l'API Gmail officielle (scope `gmail.send`), pas par SMTP/mot de passe.

1. Crée un projet sur [Google Cloud Console](https://console.cloud.google.com).
2. Active la **Gmail API** (APIs & Services → Library).
3. Configure l'**écran de consentement OAuth** (APIs & Services → OAuth consent screen) :
   - Type : *External*
   - Ajoute ton propre compte Gmail dans **Test users** (tant que l'app reste en mode "Testing", ce qui est suffisant pour un usage personnel).
4. Crée un identifiant (APIs & Services → Credentials → Create Credentials → OAuth client ID → **Desktop app**).
5. Télécharge le fichier JSON, renomme-le `credentials.json` et place-le à la racine du projet.
6. Dans `.env` : `MAIL_PROVIDER=gmail`.

Au premier envoi, un navigateur s'ouvre pour valider l'autorisation du compte Gmail. Un fichier `token.json` est alors généré automatiquement et réutilisé (avec rafraîchissement automatique) pour les envois suivants.

> `credentials.json` et `token.json` contiennent des secrets : ils sont exclus du dépôt via `.gitignore` et ne doivent **jamais** être commités.

## Ajouter un template

Dépose un fichier `.html` dans `templates/`. Tout placeholder de la forme `{{ champ }}` est automatiquement détecté et demandé à l'envoi (CLI ou GUI).

Exemple :

```html
<h1>Bonjour {{ prenom }},</h1>
<p>Merci de votre visite, {{ prenom }} {{ nom }} !</p>
```

## Utilisation

### En ligne de commande

```bash
python main.py
```

Le script demande successivement : sujet, nom de l'expéditeur, identifiant mail de l'expéditeur, destinataire, puis le template à utiliser (liste numérotée) et enfin la valeur de chaque champ détecté dans le template.

### Interface graphique

```bash
python gui.py
```

Même déroulé que la CLI, sous forme de formulaire : les champs du template sélectionné apparaissent dynamiquement dans la fenêtre.

## Logs

Chaque exécution écrit dans `logs/app.log` (rotation automatique selon `LOG_MAX_SIZE_MB` / `LOG_BACKUP_COUNT`). Utile pour diagnostiquer un échec d'envoi sans exposer d'informations sensibles à l'écran.

## Licence

Projet personnel, libre d'usage à titre d'exemple/apprentissage.
