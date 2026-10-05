# API Catalogue de jeux

API REST de catalogue de jeux vidéo, construite avec FastAPI et SQLAlchemy :
recherche et filtrage du catalogue, gestion des éditeurs, comptes utilisateurs
et authentification par jeton. Destinée au front du catalogue et aux scripts
d'import de l'équipe.

## Prérequis

- Python 3.12 ou plus récent (la CI valide 3.12)
- `pip`

Aucune base de données à installer : le démarrage rapide utilise SQLite, inclus
dans Python. Pour PostgreSQL, voir la section Configuration.

## Démarrage rapide

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
copy .env.example .env          # Windows
cp .env.example .env            # macOS / Linux
```

Ouvrez `.env` et renseignez les deux variables obligatoires :

```bash
DATABASE_URL=sqlite:///./jeux.db
CLE_SECRETE=                                  # collez la clé générée ci-dessous
ORIGINES_AUTORISEES=["http://localhost:5173"]
```

`ORIGINES_AUTORISEES` doit être écrite entre crochets, comme ci-dessus. La forme
sans crochets livrée par `.env.example` fait échouer le démarrage.

Générez votre clé, et collez-la dans `CLE_SECRETE` :

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Créez les tables et le catalogue de démonstration, puis lancez l'API :

```bash
python scripts/peupler.py
fastapi dev app/main.py
```

Ouvrez http://127.0.0.1:8000/docs : la liste des routes s'affiche, groupée par
domaine. Et http://127.0.0.1:8000/ répond :

```json
{"message": "API opérationnelle", "documentation": "/docs", "version": "1.0.0"}
```

Si c'est le cas, l'installation est terminée.

`scripts/peupler.py` insère 8 jeux et crée un compte administrateur local,
`admin@example.com` / `motdepasse123`. Choisissez d'autres identifiants avec
`--admin` et `--mot-de-passe`. Ce compte sert à la démonstration locale : ne le
reproduisez pas sur une base partagée.

## Configuration

Toutes les variables se lisent dans `.env`, validé au démarrage par
`app/config.py`. Une variable obligatoire manquante empêche le lancement, avec
un message explicite.

| Variable | Rôle | Obligatoire | Défaut |
|---|---|:---:|---|
| `DATABASE_URL` | Chaîne de connexion SQLAlchemy | oui | — |
| `CLE_SECRETE` | Signature des jetons d'authentification | oui | — |
| `ALGORITHME_JETON` | Algorithme de signature des jetons | non | `HS256` |
| `DUREE_JETON_MINUTES` | Durée de validité d'un jeton | non | `30` |
| `ORIGINES_AUTORISEES` | Origines CORS autorisées, au format liste JSON | non | `["http://localhost:5173"]` |
| `ENVIRONNEMENT` | `developpement` ou `production` | non | `developpement` |
| `NIVEAU_JOURNAL` | Niveau de journalisation | non | `INFO` |
| `ECHO_SQL` | Affiche les requêtes SQL émises | non | `false` |
| `MAX_TENTATIVES_CONNEXION` | Tentatives de connexion avant blocage | non | `5` |
| `FENETRE_TENTATIVES_MINUTES` | Fenêtre du compteur de tentatives | non | `15` |

`CLE_SECRETE` doit être différente en production : qui la détient peut forger un
jeton d'administrateur. `.env` n'est jamais versionné ; `.env.example` l'est.

Pour PostgreSQL, remplacez `DATABASE_URL` :

```bash
DATABASE_URL=postgresql+psycopg://utilisateur:motdepasse@localhost:5432/jeux
```

## Utilisation

Les routes métier sont préfixées par `/api/v1`. La documentation interactive
générée par FastAPI est à http://127.0.0.1:8000/docs : elle liste toutes les
routes, leurs paramètres et leurs réponses, et permet de les essayer. Trois
exemples pour commencer.

Lister le catalogue, filtré et paginé (aucune authentification) :

```bash
curl "http://127.0.0.1:8000/api/v1/jeux?genre=RPG&note_min=8&limite=5"
```

Consulter les statistiques du catalogue (aucune authentification) :

```bash
curl "http://127.0.0.1:8000/api/v1/jeux/statistiques"
```

Créer un jeu demande un jeton. Obtenez-le avec `POST /api/v1/connexion`, puis
envoyez-le dans l'en-tête `Authorization: Bearer <jeton>`. Le bouton
**Authorize** de `/docs` fait les deux pour vous.

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/jeux" \
  -H "Authorization: Bearer <votre-jeton>" \
  -H "Content-Type: application/json" \
  -d '{"titre": "Outer Wilds", "genre": "Aventure", "note": 9, "annee": 2019}'
```

Sous Windows, `curl` dans PowerShell est un alias d'`Invoke-WebRequest` et
n'accepte pas ces options : utilisez `/docs`, ou `curl.exe`.

La route `GET /sante` répond `200` et
`{"statut": "ok", "base": "ok", "environnement": "developpement"}` quand la base
est joignable, `503` sinon.

## Tests

Les dépendances de développement ajoutent `pytest` et `ruff` :

```bash
pip install -r requirements-dev.txt
pytest
ruff check .
```

`pytest` utilise une base SQLite en mémoire, recréée à chaque test : votre base
de développement n'est pas touchée. Les deux commandes sont rejouées par la CI
(`.github/workflows/verifications.yml`) sur chaque pull request et sur chaque
fusion dans `main`.

## Architecture

L'application est découpée en couches. Chacune ne connaît que la suivante : un
routeur ne fait pas de SQL, un service ne connaît pas HTTP. C'est ce qui permet
de tester les règles métier sans serveur.

```mermaid
flowchart TD
    Client["Client HTTP"] --> Routeurs["routeurs/ — routes, validation, codes HTTP"]
    Routeurs --> Services["services/ — regles metier et autorisations"]
    Services --> Depots["depots/ — requetes SQLAlchemy"]
    Depots --> Tables["tables/ — tables et contraintes"]
    Tables --> Base[("Base de donnees")]
    Routeurs -.valide avec.-> Modeles["modeles/ — schemas Pydantic"]
```

| Dossier | Rôle |
|---|---|
| `app/routeurs/` | Les routes HTTP, un fichier par domaine |
| `app/services/` | Les règles métier et les autorisations, sans HTTP ni SQL |
| `app/depots/` | Les requêtes SQLAlchemy |
| `app/tables/` | Les tables et leurs contraintes |
| `app/modeles/` | Les schémas Pydantic d'entrée et de sortie |
| `tests/` | Tests unitaires et tests d'intégration |
| `scripts/` | Utilitaires : `peupler`, `importer`, `exporter`, `enrichir`, `statistiques` |
| `donnees/` | Le catalogue CSV de démonstration |

À la racine de `app/` : `main.py` assemble l'application et les gestionnaires
d'erreurs, `config.py` valide la configuration, `securite.py` gère les mots de
passe et les jetons, `base_donnees.py` le moteur et les sessions.

## Contribuer

`main` doit toujours fonctionner. Rien n'y arrive sans relecture.

1. **Une issue** décrit le problème : contexte, étapes pour reproduire,
   comportement attendu, comportement observé.
2. **Une branche** par issue, nommée `type/numero-description` — par exemple
   `fix/1-statistiques-catalogue-vide`. Les types suivent Conventional Commits :
   `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.
3. **Des commits lisibles**, au format `type(portée): résumé à l'impératif`. Le
   corps explique pourquoi ; le diff montre déjà comment. Terminez par
   `Refs #<numero>`.
4. **Une pull request relue**, décrivant le contexte, les changements, l'impact
   et comment tester, et fermant son issue avec `Closes #<numero>`. Attendez que
   la CI soit verte avant de demander la relecture.
5. **Fusion en _squash_** : un commit sur `main` égale une pull request relue.
   Supprimez la branche après la fusion.

Ne nommez pas une branche d'après son seul type : une branche appelée `fix`
empêche la création de toute branche `fix/…` pour l'équipe entière, Git ne
pouvant pas traiter la même référence comme un fichier et comme un dossier.