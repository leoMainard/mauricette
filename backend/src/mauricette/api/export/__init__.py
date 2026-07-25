"""Rendu des exports (PDF/DOCX/XLSX) du questionnaire d'un AO.

Package volontairement placé dans la couche API (comme `api/schemas/`) plutôt
que dans le domaine ou l'application : il ne fait que présenter des données déjà
assemblées par `ExporterReponsesAppelOffre` sous une forme de fichier particulière,
et est le seul endroit du projet autorisé à dépendre de `reportlab`/`python-docx`/
`openpyxl`.
"""
