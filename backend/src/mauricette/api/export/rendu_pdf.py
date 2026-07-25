"""Rendu PDF du questionnaire d'un AO, via `reportlab`.

Choisi plutôt que `weasyprint` pour éviter ses dépendances système natives
(GTK/Pango/Cairo), pénibles à installer sous Windows : `reportlab` est
pur Python (roues précompilées), sans dépendance système.
"""

from __future__ import annotations

import io
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from mauricette.api.export.theme import CYAN, GRIS_DISCRET, MARINE
from mauricette.application.cas_usage.exporter_reponses_appel_offre import ExportReponses

_MARINE = colors.HexColor(f"#{MARINE}")
_CYAN = colors.HexColor(f"#{CYAN}")
_GRIS = colors.HexColor(f"#{GRIS_DISCRET}")

_STYLE_TITRE_BANDEAU = ParagraphStyle(
    "TitreBandeau", fontName="Helvetica-Bold", fontSize=18, textColor=colors.white, leading=22
)
_STYLE_H1 = ParagraphStyle(
    "H1", fontName="Helvetica-Bold", fontSize=15, textColor=_MARINE, spaceBefore=18, spaceAfter=6
)
_STYLE_H2 = ParagraphStyle(
    "H2", fontName="Helvetica-Bold", fontSize=11.5, textColor=_MARINE, spaceBefore=12, spaceAfter=4
)
_STYLE_QUESTION = ParagraphStyle(
    "Question", fontName="Helvetica-Bold", fontSize=10, spaceBefore=8, spaceAfter=2, leading=13
)
_STYLE_OBLIGATOIRE = ParagraphStyle(
    "Obligatoire", fontName="Helvetica-Oblique", fontSize=8, textColor=_CYAN, spaceAfter=2
)
_STYLE_REPONSE = ParagraphStyle("Reponse", fontName="Helvetica", fontSize=10, leading=13)
_STYLE_REPONSE_VIDE = ParagraphStyle(
    "ReponseVide", fontName="Helvetica-Oblique", fontSize=10, textColor=_GRIS, leading=13
)
_STYLE_CITATIONS = ParagraphStyle(
    "Citations", fontName="Helvetica", fontSize=8, textColor=_GRIS, spaceBefore=2
)


def generer_pdf(export: ExportReponses) -> bytes:
    """Génère le PDF du questionnaire complet (une question par bloc, "Non renseigné" si vide)."""
    tampon = io.BytesIO()
    document = SimpleDocTemplate(
        tampon,
        pagesize=A4,
        topMargin=0,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    largeur_page = A4[0]
    bandeau = Table(
        [[Paragraph(escape(export.nom_appel_offre), _STYLE_TITRE_BANDEAU)]],
        colWidths=[largeur_page],
    )
    bandeau.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), _MARINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 2 * cm),
                ("TOPPADDING", (0, 0), (-1, -1), 16),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
            ]
        )
    )

    corps: list = [bandeau, Spacer(1, 20)]

    for referentiel in export.referentiels:
        corps.append(Paragraph(escape(referentiel.nom), _STYLE_H1))
        for section in referentiel.sections:
            corps.append(Paragraph(escape(section.nom), _STYLE_H2))
            corps.append(HRFlowable(width="100%", thickness=1.5, color=_CYAN, spaceAfter=8))
            for question in section.questions:
                corps.append(Paragraph(escape(question.question), _STYLE_QUESTION))
                if question.obligatoire:
                    corps.append(Paragraph("Obligatoire", _STYLE_OBLIGATOIRE))
                if question.contenu:
                    corps.append(Paragraph(escape(question.contenu), _STYLE_REPONSE))
                else:
                    corps.append(Paragraph("Non renseigné", _STYLE_REPONSE_VIDE))
                if question.citations:
                    corps.append(
                        Paragraph(escape(" · ".join(question.citations)), _STYLE_CITATIONS)
                    )
                corps.append(Spacer(1, 10))

    document.build(corps)
    return tampon.getvalue()
