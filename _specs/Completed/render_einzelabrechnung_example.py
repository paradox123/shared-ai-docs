#!/usr/bin/env python3
"""Render a printable tenant billing example (HTML + PDF) from JSON input data."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parent
INPUT_JSON = ROOT / "nebenkosten_input_example.json"
OUTPUT_DIR = ROOT / "rendered_example" / "mp-kraft-huehne"
HTML_OUT = OUTPUT_DIR / "einzelabrechnung.html"
PDF_OUT = OUTPUT_DIR / "einzelabrechnung.pdf"


@dataclass
class CostRow:
    kostenart: str
    bereich: str
    gesamtkosten: float
    verteilung: str
    rechnung: str
    ihr_betrag: float


def load_input() -> Dict:
    with INPUT_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


def eur(value: float) -> str:
    s = f"{value:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".") + " EUR"


def get_tenant_context(data: Dict) -> Dict:
    tenant = next(m for m in data["mietparteien"] if m["id"] == "mp-kraft-huehne")
    ne_id = tenant["zugeordnete_nu"][0]

    be = None
    ne = None
    all_ne = []
    for unit in data["objekt"]["berechnungseinheiten"]:
        for n in unit["nutzeinheiten"]:
            all_ne.append(n)
            if n["id"] == ne_id:
                be = unit
                ne = n
    if be is None or ne is None:
        raise ValueError("Tenant context not found")

    total_wohnflaeche = sum(n["wohnflaeche_m2"] for n in all_ne)
    be_wohnflaeche = sum(n["wohnflaeche_m2"] for n in be["nutzeinheiten"])
    total_personen = sum(m["personen"] for m in data["mietparteien"])

    return {
        "tenant": tenant,
        "ne": ne,
        "be": be,
        "total_wohnflaeche": total_wohnflaeche,
        "be_wohnflaeche": be_wohnflaeche,
        "total_personen": total_personen,
    }


def find_beleg(data: Dict, kostenart_id: str, be_id: int | None = None, vers: str | None = None) -> Dict:
    for b in data["kostenbelege"]:
        if b["kostenart_id"] != kostenart_id:
            continue
        scope = b.get("scope", {})
        if be_id is not None and scope.get("berechnungseinheit") != be_id:
            continue
        if vers is not None and scope.get("versicherungsvertrag") != vers:
            continue
        if be_id is None and vers is None and scope:
            continue
        return b
    raise ValueError(f"No beleg found for {kostenart_id}, be={be_id}, vers={vers}")


def build_cost_rows(data: Dict, ctx: Dict) -> List[CostRow]:
    ne_area = ctx["ne"]["wohnflaeche_m2"]
    total_area = ctx["total_wohnflaeche"]
    be_area = ctx["be_wohnflaeche"]
    tenant_personen = ctx["tenant"]["personen"]
    total_personen = ctx["total_personen"]

    r_objekt = ne_area / total_area
    r_be = ne_area / be_area
    r_person = tenant_personen / total_personen

    grundsteuer = find_beleg(data, "GRU")["betrag"]
    oberflaeche = find_beleg(data, "OBF")["betrag"]
    muell = find_beleg(data, "MUE")["betrag"]
    vers = find_beleg(data, "GEV", vers="vers-axa-3")["betrag"]
    brennstoff = find_beleg(data, "BRE", be_id=1)["betrag"]
    warmwasser = find_beleg(data, "WWV", be_id=1)["betrag"]
    strom = find_beleg(data, "STR", be_id=1)["betrag"]

    rows = [
        CostRow(
            kostenart="Grundsteuer",
            bereich="gesamtes Objekt",
            gesamtkosten=grundsteuer,
            verteilung=f"nach Wohnflaeche: {total_area} m2 gesamt, davon {ne_area} m2 Ihre Wohnung",
            rechnung=f"{eur(grundsteuer)} x ({ne_area} / {total_area})",
            ihr_betrag=grundsteuer * r_objekt,
        ),
        CostRow(
            kostenart="Oberflaechenwasser",
            bereich="gesamtes Objekt",
            gesamtkosten=oberflaeche,
            verteilung=f"nach Wohnflaeche: {total_area} m2 gesamt, davon {ne_area} m2 Ihre Wohnung",
            rechnung=f"{eur(oberflaeche)} x ({ne_area} / {total_area})",
            ihr_betrag=oberflaeche * r_objekt,
        ),
        CostRow(
            kostenart="Muellabfuhr",
            bereich="gesamtes Objekt",
            gesamtkosten=muell,
            verteilung=f"nach Personenzahl: {total_personen} Personen gesamt, davon {tenant_personen} Personen Ihre Mietpartei",
            rechnung=f"{eur(muell)} x ({tenant_personen} / {total_personen})",
            ihr_betrag=muell * r_person,
        ),
        CostRow(
            kostenart="Gebaeudeversicherung (AXA 56003644333)",
            bereich="Vertrag",
            gesamtkosten=vers,
            verteilung=f"im Vertrag nach Wohnflaeche: {be_area} m2 gesamt, davon {ne_area} m2 Ihre Wohnung",
            rechnung=f"{eur(vers)} x ({ne_area} / {be_area})",
            ihr_betrag=vers * r_be,
        ),
        CostRow(
            kostenart="Brennstoffkosten (Gebaeude Ost)",
            bereich="Gebaeude Ost (BE1)",
            gesamtkosten=brennstoff,
            verteilung=f"Demo-Verteilung nach Wohnflaeche in BE1: {be_area} m2 gesamt, davon {ne_area} m2 Ihre Wohnung",
            rechnung=f"{eur(brennstoff)} x ({ne_area} / {be_area})",
            ihr_betrag=brennstoff * r_be,
        ),
        CostRow(
            kostenart="Warmwasseraufbereitung per Waermepumpe",
            bereich="Gebaeude Ost (BE1)",
            gesamtkosten=warmwasser,
            verteilung=f"Demo-Verteilung nach Wohnflaeche in BE1: {be_area} m2 gesamt, davon {ne_area} m2 Ihre Wohnung",
            rechnung=f"{eur(warmwasser)} x ({ne_area} / {be_area})",
            ihr_betrag=warmwasser * r_be,
        ),
        CostRow(
            kostenart="Stromkosten (Gebaeude Ost)",
            bereich="Gebaeude Ost (BE1)",
            gesamtkosten=strom,
            verteilung=f"Demo-Verteilung nach Wohnflaeche in BE1: {be_area} m2 gesamt, davon {ne_area} m2 Ihre Wohnung",
            rechnung=f"{eur(strom)} x ({ne_area} / {be_area})",
            ihr_betrag=strom * r_be,
        ),
    ]
    return rows


def reading_diff(data: Dict, zaehler_id: str, ne_id: str) -> float:
    items = [a for a in data["ablesungen"] if a.get("zaehler_id") == zaehler_id and a.get("ne_id") == ne_id]
    if not items:
        return 0.0
    if "messwert_alt" in items[0] and "messwert_neu" in items[0]:
        return float(items[0]["messwert_neu"] - items[0]["messwert_alt"])
    # manual model: two stichtag entries
    items_sorted = sorted(items, key=lambda x: x.get("stichtag", ""))
    if len(items_sorted) >= 2:
        return float(items_sorted[-1]["messwert"] - items_sorted[0]["messwert"])
    return 0.0


def build_consumption_rows(data: Dict, ctx: Dict) -> List[List[str]]:
    ne_id = ctx["ne"]["id"]
    hv_diff = reading_diff(data, "z-heizverbrauch-ne1", ne_id)
    hv_converted = hv_diff * 1.32

    return [
        ["Kaltwasser", "z-kaltwasser-ne1", "m3", "125,50"],
        ["Warmwasser", "z-warmwasser-ne1", "m3", "25,80"],
        ["Heizverbrauch", "z-heizverbrauch-ne1", "VE", f"{hv_diff:,.0f}".replace(",", ".")],
        ["Heizverbrauch (umgerechnet)", "z-heizverbrauch-ne1", "VE", f"{hv_converted:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")],
        ["Strom Wohnung", "z-strom-ne1", "kWh", f"{reading_diff(data, 'z-strom-ne1', ne_id):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")],
    ]


def render_html(data: Dict, ctx: Dict, costs: List[CostRow], consumptions: List[List[str]]) -> str:
    total = sum(r.ihr_betrag for r in costs)
    v = next(x for x in data["vorauszahlungen"] if x["mietpartei_id"] == ctx["tenant"]["id"])
    v_total = float(v["gesamtbetrag"])
    saldo = total - v_total

    cost_rows = "\n".join(
        (
            "<tr>"
            f"<td>{r.kostenart}</td>"
            f"<td>{r.bereich}</td>"
            f"<td>{eur(r.gesamtkosten)}</td>"
            f"<td>{r.verteilung}</td>"
            f"<td>{r.rechnung} = {eur(r.ihr_betrag)}</td>"
            f"<td>{eur(r.ihr_betrag)}</td>"
            "</tr>"
        )
        for r in costs
    )

    cons_rows = "\n".join(
        f"<tr><td>{n}</td><td>{z}</td><td>{u}</td><td>{v}</td></tr>" for n, z, u, v in consumptions
    )

    return f"""<!doctype html>
<html lang=\"de\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Einzelabrechnung {ctx['tenant']['name']}</title>
  <style>
    @page {{ size: A4; margin: 14mm; }}
    :root {{ --ink:#1f2022; --line:#d8d2c8; --brand:#0f5a52; --bg:#f4efe6; --paper:#fffdfa; }}
    body {{ margin:0; font-family: 'Source Sans 3', 'Segoe UI', sans-serif; color:var(--ink); background:var(--bg); }}
    .page {{ width: 210mm; min-height: 297mm; margin: 8mm auto; background:var(--paper); padding:14mm; box-sizing:border-box; border:1px solid #d7d0c4; }}
    h1,h2 {{ margin:0; font-family:'Georgia', serif; }}
    .sub {{ margin:4px 0 0; color:#4c4f57; }}
    .header {{ border-left:6px solid var(--brand); padding:8px 10px; background:#f1f8f6; }}
    .summary {{ margin-top:10px; display:grid; grid-template-columns: repeat(3,1fr); gap:8px; }}
    .box {{ border:1px solid var(--line); background:white; padding:8px; }}
    .box .label {{ font-size:12px; color:#4c4f57; }}
    .box .value {{ font-size:23px; font-family:'Georgia', serif; }}
    h2 {{ margin-top:14px; font-size:20px; border-bottom:1px solid var(--line); padding-bottom:4px; }}
    .hint {{ margin-top:8px; border:1px solid var(--line); background:#f7faf8; padding:8px; font-size:13px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:8px; font-size:12.5px; }}
    thead {{ display: table-header-group; }}
    tr {{ page-break-inside: avoid; break-inside: avoid; }}
    th,td {{ border:1px solid var(--line); padding:6px 7px; vertical-align:top; }}
    th {{ background:#eef5f3; text-align:left; font-size:11.5px; text-transform:uppercase; letter-spacing:.04em; }}
    .footer {{ margin-top:10px; font-size:12px; color:#5d616b; border-top:1px solid var(--line); padding-top:8px; }}
    @media print {{ body {{ background:white; }} .page {{ margin:0; border:0; }} }}
  </style>
</head>
<body>
  <article class=\"page\">
    <section class=\"header\">
      <h1>Nebenkostenabrechnung {data['abrechnungsjahr']}</h1>
      <p class=\"sub\">Objekt: {data['objekt']['name']} | Mietpartei: {ctx['tenant']['name']} | Wohnung: {ctx['ne']['name']}</p>
      <p class=\"sub\">Abrechnungszeitraum: {data['abrechnungszeitraum']['von']} bis {data['abrechnungszeitraum']['bis']}</p>
    </section>

    <section class=\"summary\">
      <div class=\"box\"><div class=\"label\">Ihre Gesamtkosten</div><div class=\"value\">{eur(total)}</div></div>
      <div class=\"box\"><div class=\"label\">Ihre Vorauszahlungen</div><div class=\"value\">{eur(v_total)}</div></div>
      <div class=\"box\"><div class=\"label\">Saldo</div><div class=\"value\">{eur(saldo)}</div></div>
    </section>

    <div class=\"hint\"><strong>Begriffe:</strong> Ihre Wohnung ist {ctx['ne']['id']}. Diese Wohnung gehoert zur Berechnungseinheit {ctx['be']['name']} (BE{ctx['be']['id']}). In dieser Berechnungseinheit werden bestimmte Kosten gemeinsam verteilt.</div>

    <h2>1. Verbrauchswerte Ihrer Wohnung</h2>
    <table>
      <thead><tr><th>Wert</th><th>Zaehler</th><th>Einheit</th><th>Verbrauch im Zeitraum</th></tr></thead>
      <tbody>
        {cons_rows}
      </tbody>
    </table>

    <h2>2. Kostenarten, Verteilung und Ihr Anteil</h2>
    <table>
      <thead>
        <tr>
          <th>Kostenart</th><th>Bereich</th><th>Gesamtkosten</th><th>So wird verteilt</th><th>Ihre Rechnung</th><th>Ihr Betrag</th>
        </tr>
      </thead>
      <tbody>
        {cost_rows}
      </tbody>
    </table>

    <h2>3. Vorauszahlungen und Ergebnis</h2>
    <table>
      <thead><tr><th>Monatsbetrag</th><th>Anzahl Monate</th><th>Gezahlt</th><th>Gesamtkosten</th><th>Saldo</th></tr></thead>
      <tbody><tr><td>{eur(float(v['betrag_monatlich']))}</td><td>{v['anzahl_monate']}</td><td>{eur(v_total)}</td><td>{eur(total)}</td><td>{eur(saldo)}</td></tr></tbody>
    </table>

    <p class=\"footer\">Hinweis: Dies ist ein erstes Beispiel aus den JSON-Daten. Fuer Kostenarten ohne vollstaendige Vergleichswerte im Beispiel-JSON wird im Mock eine nachvollziehbare Demo-Verteilung verwendet.</p>
  </article>
</body>
</html>
"""


def render_pdf(data: Dict, ctx: Dict, costs: List[CostRow], consumptions: List[List[str]]) -> None:
    total = sum(r.ihr_betrag for r in costs)
    v = next(x for x in data["vorauszahlungen"] if x["mietpartei_id"] == ctx["tenant"]["id"])
    v_total = float(v["gesamtbetrag"])
    saldo = total - v_total

    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18, leading=22)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13, spaceBefore=8, spaceAfter=4)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=9.5, leading=12)
    header_cell = ParagraphStyle("header_cell", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8.6, leading=10, wordWrap="CJK")
    table_cell = ParagraphStyle("table_cell", parent=styles["BodyText"], fontSize=8.4, leading=10, wordWrap="CJK")

    def cell(text: str) -> Paragraph:
        return Paragraph(text, table_cell)

    def hcell(text: str) -> Paragraph:
        return Paragraph(text, header_cell)

    doc = SimpleDocTemplate(str(PDF_OUT), pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=14 * mm, bottomMargin=14 * mm)
    story = []

    story.append(Paragraph(f"Nebenkostenabrechnung {data['abrechnungsjahr']}", title))
    story.append(Paragraph(f"Objekt: {data['objekt']['name']} | Mietpartei: {ctx['tenant']['name']} | Wohnung: {ctx['ne']['name']}", body))
    story.append(Paragraph(f"Abrechnungszeitraum: {data['abrechnungszeitraum']['von']} bis {data['abrechnungszeitraum']['bis']}", body))
    story.append(Spacer(1, 5 * mm))

    summary_data = [
        [hcell("Ihre Gesamtkosten"), hcell("Ihre Vorauszahlungen"), hcell("Saldo")],
        [cell(eur(total)), cell(eur(v_total)), cell(eur(saldo))],
    ]
    summary = Table(summary_data, colWidths=[58 * mm, 58 * mm, 58 * mm])
    summary.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ecf5f2")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cfc9bf")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(summary)

    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Begriffe: Ihre Wohnung ist NE1. Diese Wohnung gehoert zur Berechnungseinheit Gebaeude Ost (BE1).", body))

    story.append(Paragraph("1. Verbrauchswerte Ihrer Wohnung", h2))
    cons_table_data = [[hcell("Wert"), hcell("Zaehler"), hcell("Einheit"), hcell("Verbrauch im Zeitraum")]]
    for n, z, u, v_value in consumptions:
        cons_table_data.append([cell(n), cell(z), cell(u), cell(v_value)])
    cons_table = Table(cons_table_data, colWidths=[52 * mm, 46 * mm, 24 * mm, 58 * mm], repeatRows=1, splitByRow=1)
    cons_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eff6f4")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d4cec3")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(cons_table)

    story.append(Paragraph("2. Kostenarten, Verteilung und Ihr Anteil", h2))
    cost_table_data = [[hcell("Kostenart"), hcell("Bereich"), hcell("Gesamtkosten"), hcell("So wird verteilt"), hcell("Ihre Rechnung"), hcell("Ihr Betrag")]]
    for r in costs:
        cost_table_data.append([
            cell(r.kostenart),
            cell(r.bereich),
            cell(eur(r.gesamtkosten)),
            cell(r.verteilung),
            cell(f"{r.rechnung}<br/>= {eur(r.ihr_betrag)}"),
            cell(eur(r.ihr_betrag)),
        ])

    cost_table = Table(
        cost_table_data,
        colWidths=[28 * mm, 22 * mm, 22 * mm, 43 * mm, 43 * mm, 22 * mm],
        repeatRows=1,
        splitByRow=1,
    )
    cost_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eff6f4")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d4cec3")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(cost_table)

    story.append(Paragraph("3. Vorauszahlungen und Ergebnis", h2))
    result_data = [
        [hcell("Monatsbetrag"), hcell("Anzahl Monate"), hcell("Gezahlt"), hcell("Gesamtkosten"), hcell("Saldo")],
        [cell(eur(float(v["betrag_monatlich"]))), cell(str(v["anzahl_monate"])), cell(eur(v_total)), cell(eur(total)), cell(eur(saldo))],
    ]
    result = Table(result_data, colWidths=[34 * mm, 26 * mm, 36 * mm, 36 * mm, 44 * mm], repeatRows=1, splitByRow=1)
    result.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eff6f4")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d4cec3")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(result)

    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("Hinweis: Langes Tabellenmaterial wird mit wiederholter Tabellenkopfzeile ueber Seiten umbrochen (repeatRows + splitByRow).", body))

    doc.build(story)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data = load_input()
    ctx = get_tenant_context(data)
    costs = build_cost_rows(data, ctx)
    consumptions = build_consumption_rows(data, ctx)

    html = render_html(data, ctx, costs, consumptions)
    HTML_OUT.write_text(html, encoding="utf-8")
    render_pdf(data, ctx, costs, consumptions)

    print(f"HTML generated: {HTML_OUT}")
    print(f"PDF generated: {PDF_OUT}")


if __name__ == "__main__":
    main()
