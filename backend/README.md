# Mauricette — Backend

API et logique métier de Mauricette, construites en architecture hexagonale.

## Structure

```
src/mauricette/
├── domaine/          # Cœur métier : entités + ports (interfaces), aucune dépendance externe
│   ├── entites/      # Objets métier (AppelOffre, Document, ...)
│   └── ports/        # Interfaces que l'infrastructure doit implémenter
├── application/      # Cas d'usage : orchestrent le domaine via les ports
│   └── cas_usage/
├── infrastructure/    # Adaptateurs concrets (implémentations des ports)
│   ├── persistence/   # Accès PostgreSQL (SQLAlchemy)
│   └── stockage/      # Accès au stockage de documents (local ou S3/MinIO)
├── api/               # Adaptateur d'entrée : FastAPI (routes + schémas HTTP)
└── config/            # Paramètres de l'application (variables d'environnement)
```

**Règle de dépendance** : `domaine` ne dépend de rien. `application` dépend de `domaine`.
`infrastructure` et `api` dépendent de `application` et `domaine`, jamais l'inverse.
Pour changer de base de données ou de fournisseur de stockage, seul un adaptateur
dans `infrastructure/` doit être modifié ou remplacé.

## Démarrage

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run fastapi dev src/mauricette/api/main.py
```
