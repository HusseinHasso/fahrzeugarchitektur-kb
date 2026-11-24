#!/usr/bin/env python3
"""kb_tool.py – Werkzeug für die Fahrzeugarchitektur-Wissensbasis (Leitfaden 2.4, Schema 2.3; ältere Schemata werden mitgeprüft).

Nachbau aus Arbeitsauftrag, Schema und Probelauf 2. Befehle:

  glossar  <dir> --gruppe G            Glossarvorgaben und bisher verwendete Namen für den Arbeitsauftrag
  validate <dir> [--nur ID] [--schema PFAD]
                                       Prüft Artikel; Zeilen FEHLER, WARNUNG, HINWEIS; Exit 1 bei FEHLER
  status   <dir> ID STATUS [--grund T] Setzt den Status (nur Orchestrator); zu_pruefen/geprueft nur ohne FEHLER
  plan     <dir> [--gruppe G]          Bearbeitungsreihenfolge: Blattartikel, dann Übersichten von unten nach oben
  stats    <dir>                       Kennzahlen je Artikel (Wörter, Belegquote, Quellen)
  gliederung <dir>                     Recherchegliederung als Markdown-Baum aus dem Inventar

<dir> enthält manifest.json, inventar.json, glossar_vorgaben.json, aenderungen.json und artikel/.
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

KATEGORIEN = [
    "struktur_fahrwerk", "antrieb", "energieversorgung", "lenkung", "bremse", "bedienraum",
    "aufbau_nutzlast", "elektrik_elektronik", "steuerung_information", "assistenz_sicherheit",
    "beleuchtung_sicht", "thermomanagement", "nebensysteme",
]
STATUS = ["offen", "in_arbeit", "zu_pruefen", "geprueft"]
WORT = re.compile(r"\w+", re.UNICODE)
FORMELN = re.compile(r"\b(CO2|H2O|H2|O2|N2O|NO2|CH4|SO2)\b")  # chemische Formeln sind keine Zahlenwerte (Regel 7)


def hat_ziffer(text):
    return bool(re.search(r"\d", FORMELN.sub("", text)))
NORMKUERZEL = re.compile(r"\b(ISO|DIN|EN|IEC|SAE|ECE|UNECE|VDI|DNV|IMCA|StVZO|UN-R|UN R)\b")


# ---------------------------------------------------------------- Hilfen

def lade(pfad, standard=None):
    p = Path(pfad)
    if not p.exists():
        if standard is not None:
            return standard
        sys.exit(f"FEHLER Datei fehlt: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def schreibe(pfad, daten):
    Path(pfad).write_text(json.dumps(daten, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def inventar(d):
    return {e["artikel_id"]: e for e in lade(d / "inventar.json")}


def gruppe_von(eintrag):
    pf = eintrag.get("recherchepfade") or [[]]
    return pf[0][0] if pf and pf[0] else None


def artikel_pfad(d, aid):
    return d / "artikel" / f"{aid}.json"


def alle_artikel(d):
    ordner = d / "artikel"
    if not ordner.is_dir():
        return {}
    erg = {}
    for p in sorted(ordner.glob("A-*.json")):
        try:
            erg[p.stem] = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            erg[p.stem] = e
    return erg


def ohne_klammer(name):
    return re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()


def woerter(text):
    return len(WORT.findall(text))


def absaetze(a):
    return [p for s in a.get("abschnitte", []) for p in s.get("absaetze", [])]


def finde_schema(d, explizit):
    kandidaten = [Path(explizit)] if explizit else [
        d / "artikel.schema.json",
        d.parent / "leitfaden" / "artikel.schema.json",
        Path(__file__).resolve().parent.parent / "leitfaden" / "artikel.schema.json",
    ]
    for k in kandidaten:
        if k.exists():
            return json.loads(k.read_text(encoding="utf-8"))
    return None


# ---------------------------------------------------------------- glossar

def cmd_glossar(args):
    d = Path(args.dir)
    g = lade(d / "glossar_vorgaben.json")
    inv = inventar(d)
    aus = ["VORGABEN (verbindlich, zuerst verwenden)"]
    for kat, namen in g["hauptsysteme"].items():
        aus.append(f"  {kat}: " + "; ".join(namen))
    aus.append("  Funktionen: " + "; ".join(g["funktionen"]))
    for r in g.get("regeln", []):
        aus.append(f"  Regel: {r}")
    aus.append("")
    aus.append(f"BISHER VERWENDET (Gruppe {args.gruppe} markiert)")

    vorgabe = set(g["funktionen"])
    gruppen = collections.defaultdict(set)
    for aid, a in alle_artikel(d).items():
        if isinstance(a, Exception) or not a.get("modell"):
            continue
        gr = gruppe_von(inv.get(aid, {})) or "?"
        for f in a["modell"].get("funktionen", []):
            if f.get("name") and f["name"] not in vorgabe:
                gruppen[f["name"]].add(gr)
    # eigene Gruppe zuerst, dann alphabetisch
    namen = sorted(gruppen, key=lambda n: (args.gruppe not in gruppen[n], n.lower()))
    teile = [("* " if args.gruppe in gruppen[n] else "") + n for n in namen]
    aus.append("  Funktionen: " + "; ".join(teile))
    print("\n".join(aus))


# ---------------------------------------------------------------- validate

class Meldungen:
    def __init__(self):
        self.zeilen = []

    def add(self, stufe, aid, text):
        self.zeilen.append((stufe, aid, text))

    def F(self, aid, t): self.add("FEHLER", aid, t)
    def W(self, aid, t): self.add("WARNUNG", aid, t)
    def H(self, aid, t): self.add("HINWEIS", aid, t)

    def zaehle(self, stufe, aid=None):
        return sum(1 for s, a, _ in self.zeilen if s == stufe and (aid is None or a == aid))


def pruefe_artikel(aid, a, d, inv, glossar, schema, alle, m):
    if isinstance(a, Exception):
        m.F(aid, f"JSON nicht lesbar: {a}")
        return
    # Schema
    if schema is not None:
        try:
            from jsonschema import Draft202012Validator
            for e in sorted(Draft202012Validator(schema).iter_errors(a), key=lambda e: list(e.path)):
                m.F(aid, f"Schema {e.json_path}: {e.message[:200]}")
        except ImportError:
            m.H(aid, "Paket jsonschema fehlt, Schemaprüfung übersprungen")
    else:
        m.H(aid, "artikel.schema.json nicht gefunden, Schemaprüfung übersprungen")

    eintrag = inv.get(aid)
    if eintrag is None:
        m.F(aid, "Artikel steht nicht im Inventar")
        eintrag = {}
    if a.get("artikel_id") != aid:
        m.F(aid, f"artikel_id {a.get('artikel_id')} passt nicht zum Dateinamen")
    if eintrag and a.get("artikeltyp") != eintrag.get("artikeltyp"):
        m.F(aid, f"artikeltyp {a.get('artikeltyp')} weicht vom Inventar ab ({eintrag.get('artikeltyp')})")
    if eintrag and sorted(a.get("kindartikel_ids", [])) != sorted(eintrag.get("kindartikel_ids", [])):
        m.F(aid, "kindartikel_ids weichen vom Inventar ab")

    abschnitte = a.get("abschnitte", [])
    ps = absaetze(a)
    pids = collections.Counter(p.get("absatz_id") for p in ps)
    for k, v in pids.items():
        if v > 1:
            m.F(aid, f"absatz_id {k} doppelt")
    P = set(pids)
    quellen = {q.get("quellen_id"): q for q in a.get("quellen", [])}
    if len(quellen) != len(a.get("quellen", [])):
        m.F(aid, "quellen_id doppelt")

    # Quellen und Belege
    benutzt = set()
    for p in ps:
        b = p.get("begruendung")
        bel = p.get("belege", [])
        for x in bel:
            benutzt.add(x.get("quellen_id"))
            if x.get("quellen_id") not in quellen:
                m.F(aid, f"{p.get('absatz_id')}: Beleg verweist auf unbekannte Quelle {x.get('quellen_id')}")
        if b in ("belegt", "gemischt") and not bel:
            m.F(aid, f"{p.get('absatz_id')}: begruendung {b} ohne Beleg")
        if b in ("hergeleitet", "modellwissen") and bel:
            m.F(aid, f"{p.get('absatz_id')}: begruendung {b} mit Belegen (Liste muss leer sein)")
        if b in ("hergeleitet", "gemischt") and not p.get("herleitung"):
            m.F(aid, f"{p.get('absatz_id')}: begruendung {b} ohne herleitung")
        if b != "belegt" and not p.get("sicherheit"):
            m.F(aid, f"{p.get('absatz_id')}: sicherheit fehlt")
        if p.get("herleitung"):
            for pr in p["herleitung"].get("praemissen", []):
                if re.fullmatch(r"P\d+", pr) and pr not in P:
                    m.F(aid, f"{p.get('absatz_id')}: Prämisse {pr} existiert nicht")
                if re.fullmatch(r"Q\d+", pr) and pr not in quellen:
                    m.F(aid, f"{p.get('absatz_id')}: Prämisse {pr} existiert nicht")
                ref = re.fullmatch(r"(A-\d{4})/(P\d+)", pr)
                if ref:
                    kind = alle.get(ref.group(1))
                    if kind is None or isinstance(kind, Exception):
                        m.F(aid, f"{p.get('absatz_id')}: Prämisse {pr}: Artikel {ref.group(1)} liegt nicht vor")
                    elif ref.group(2) not in {q.get("absatz_id") for q in absaetze(kind)}:
                        m.F(aid, f"{p.get('absatz_id')}: Prämisse {pr} existiert nicht")
        if b != "belegt":
            t = p.get("text", "")
            if hat_ziffer(t) or NORMKUERZEL.search(t):
                m.W(aid, f"{p.get('absatz_id')}: Ziffern oder Normkürzel in nicht belegtem Absatz (Regel 7)")
        if a.get("artikeltyp") == "blatt" and p.get("herangezogene_artikel_ids"):
            m.F(aid, f"{p.get('absatz_id')}: herangezogene_artikel_ids bei Blattartikel nicht leer")
    for r in (a.get("modell") or {}).get("anforderungsthemen", []):
        for rw in r.get("regelwerke", []):
            benutzt.add(rw.get("quellen_id"))
            if rw.get("quellen_id") not in quellen:
                m.F(aid, f"{r.get('id')}: Regelwerk verweist auf unbekannte Quelle {rw.get('quellen_id')}")
    for qid, q in quellen.items():
        if qid not in benutzt:
            m.F(aid, f"Quelle {qid} wird in keinem Beleg und keinem Regelwerk verwendet")
        if not q.get("quellentyp"):
            m.F(aid, f"Quelle {qid} ohne quellentyp")
    if a.get("quellenzugriff") == "nein" and (quellen or benutzt):
        m.F(aid, "Quellenzugriff nein, aber Quellen oder Belege vorhanden")

    # Sicherheitsverteilung
    nb = [p for p in ps if p.get("begruendung") != "belegt"]
    if nb:
        c = collections.Counter(p.get("sicherheit") for p in nb)
        stufe, n = c.most_common(1)[0]
        if len(nb) >= 5 and n / len(nb) > 0.9:
            m.W(aid, f"Sicherheit {stufe} trägt {n}/{len(nb)} nicht belegte Absätze (> 90 %, Regel 5)")
    if ps:
        quote = sum(p.get("begruendung") == "belegt" for p in ps) / len(ps)
        m.H(aid, f"Belegquote {quote:.0%} ({len(ps) - len(nb)}/{len(ps)} Absätze belegt)")

    # Umfang
    gesamt = sum(woerter(p.get("text", "")) for p in ps)
    if a.get("artikeltyp") == "blatt" and not 1300 <= gesamt <= 2000:
        m.W(aid, f"Wortzahl {gesamt} außerhalb 1.300–2.000 (Regel 3)")
    elif a.get("artikeltyp") == "uebersicht" and not 800 <= gesamt <= 1500:
        m.W(aid, f"Wortzahl {gesamt} außerhalb 800–1.500 (Regel 16)")
    else:
        m.H(aid, f"Wortzahl {gesamt}")

    # Dramaturgie
    typen = [s.get("abschnittstyp") for s in abschnitte]
    if "offene_punkte" in typen and a.get("schema_version") != "2.0":
        m.F(aid, "Abschnittstyp offene_punkte ab Schema 2.1 nicht zulässig (Feld offene_punkte verwenden)")
    if a.get("artikeltyp") == "blatt":
        erwartet = ["gesamtsystem", "hauptsystem", "gesamtsystem", "modellierung", "fluesse", "perspektiven"]
        komprimiert = []
        for t in typen:
            if t in ("querschnitt", "variante"):
                continue
            if not komprimiert or komprimiert[-1] != t or t != "hauptsystem":
                komprimiert.append(t)
        if komprimiert != erwartet:
            m.F(aid, "Abschnittsfolge weicht von Regel 2 ab: " + " > ".join(komprimiert))
    elif a.get("artikeltyp") == "uebersicht" and a.get("schema_version", "0") >= "2.3":
        erwartet = ["gesamtsystem", "querschnitt", "variante", "gesamtsystem", "modellierung"]
        komprimiert = [t for i, t in enumerate(typen) if i == 0 or typen[i - 1] != t]
        if komprimiert != erwartet:
            m.F(aid, "Abschnittsfolge weicht von Regel 16 ab: " + " > ".join(komprimiert))

    # Übersicht
    if a.get("artikeltyp") == "uebersicht":
        heran = {x for p in ps for x in p.get("herangezogene_artikel_ids", [])}
        for k in eintrag.get("kindartikel_ids", []):
            if k not in heran:
                m.F(aid, f"Kindartikel {k} in keinem Absatz unter herangezogene_artikel_ids")
            if k not in alle:
                m.W(aid, f"Kindartikel {k} liegt noch nicht vor")
            elif not isinstance(alle[k], Exception) and alle[k].get("status") not in ("zu_pruefen", "geprueft"):
                m.H(aid, f"Kindartikel {k} hat Status {alle[k].get('status')}")
        for x in heran - set(eintrag.get("kindartikel_ids", [])):
            m.W(aid, f"herangezogene_artikel_ids enthält {x}, kein Kindartikel")

    # Modell
    mo = a.get("modell")
    if mo is None:
        if a.get("artikeltyp") == "blatt":
            m.F(aid, "modell fehlt (bei Blattartikel Pflicht)")
        elif a.get("schema_version", "0") >= "2.3":
            m.F(aid, "modell fehlt (ab Schema 2.3 auch bei Übersichten Pflicht, Regel 16)")
        pruefe_offene_punkte(aid, a, set(), m)
        return
    E = {}
    for e in mo.get("elemente", []):
        if e.get("id") in E:
            m.F(aid, f"Element-ID {e.get('id')} doppelt")
        E[e.get("id")] = e
    for liste, art in (("funktionen", "Funktions"), ("fluesse", "Fluss")):
        c = collections.Counter(x.get("id") for x in mo.get(liste, []))
        for k, v in c.items():
            if v > 1:
                m.F(aid, f"{art}-ID {k} doppelt")
    wurzeln = [e for e in E.values() if e.get("typ") == "gesamtsystem"]
    if len(wurzeln) != 1:
        m.F(aid, f"{len(wurzeln)} Elemente vom Typ gesamtsystem (genau eines erwartet)")
    rang = {"gesamtsystem": 0, "hauptsystem": 1, "subsystem": 2, "komponente": 3}
    for e in E.values():
        ei = e.get("eltern_id")
        if e.get("typ") == "gesamtsystem":
            if ei is not None:
                m.F(aid, f"{e['id']}: gesamtsystem mit eltern_id")
        elif ei not in E:
            m.F(aid, f"{e['id']}: eltern_id {ei} existiert nicht")
        else:
            et, pt = e.get("typ"), E[ei].get("typ")
            if et == "hauptsystem" and pt != "gesamtsystem":
                m.F(aid, f"{e['id']}: Hauptsystem hängt nicht am Gesamtsystem")
            elif rang.get(pt, 9) >= rang.get(et, 0) and not (et == "subsystem" == pt):
                m.F(aid, f"{e['id']}: Typ {et} unter {pt} nicht zulässig")
        for x in e.get("absatz_ids", []):
            if x not in P:
                m.F(aid, f"{e['id']}: absatz_id {x} existiert nicht")

    def hs_von(eid, tiefe=0):
        while eid in E and tiefe < 50:
            if E[eid].get("typ") == "hauptsystem":
                return eid
            eid, tiefe = E[eid].get("eltern_id"), tiefe + 1
        return None

    for f in mo.get("funktionen", []):
        for x in f.get("ausgefuehrt_von", []):
            if x not in E:
                m.F(aid, f"{f.get('id')}: ausgefuehrt_von {x} existiert nicht")
        for x in f.get("absatz_ids", []):
            if x not in P:
                m.F(aid, f"{f.get('id')}: absatz_id {x} existiert nicht")
    for fl in mo.get("fluesse", []):
        for k in ("von", "nach"):
            if fl.get(k) not in E:
                m.F(aid, f"{fl.get('id')}: {k} {fl.get(k)} existiert nicht")
        if fl.get("von") == fl.get("nach"):
            m.W(aid, f"{fl.get('id')}: von und nach identisch")
        for x in fl.get("absatz_ids", []):
            if x not in P:
                m.F(aid, f"{fl.get('id')}: absatz_id {x} existiert nicht")

    # Hauptsysteme, Kategorien, Glossar
    hs = [e for e in E.values() if e.get("typ") == "hauptsystem"]
    erlaubt = {k: {ohne_klammer(n) for n in v} for k, v in glossar["hauptsysteme"].items()}
    entfallen = {x.get("kategorie") for x in mo.get("entfallene_kategorien", [])}
    abgedeckt = {h.get("kategorie") for h in hs}
    for k in (KATEGORIEN if a.get("artikeltyp") == "blatt" else []):
        if k not in abgedeckt and k not in entfallen:
            m.F(aid, f"Kategorie {k} weder abgedeckt noch in entfallene_kategorien (Regel 1)")
        if k in abgedeckt and k in entfallen:
            m.F(aid, f"Kategorie {k} abgedeckt und zugleich entfallen")
    abschnitt_von = collections.defaultdict(list)
    for s in abschnitte:
        if s.get("abschnittstyp") == "hauptsystem":
            if s.get("element_id") not in E:
                m.F(aid, f"Abschnitt „{s.get('ueberschrift')}“: element_id {s.get('element_id')} existiert nicht")
            elif E[s["element_id"]].get("typ") != "hauptsystem":
                m.F(aid, f"Abschnitt „{s.get('ueberschrift')}“: element_id ist kein Hauptsystem")
            abschnitt_von[s.get("element_id")].append(s)
    funk_hs = collections.Counter()
    for f in mo.get("funktionen", []):
        for x in {hs_von(x) for x in f.get("ausgefuehrt_von", [])}:
            funk_hs[x] += 1
    fluss_hs = collections.Counter()
    for fl in mo.get("fluesse", []):
        for x in {hs_von(fl.get("von")), hs_von(fl.get("nach"))}:
            fluss_hs[x] += 1
    for h in hs:
        hid, kat = h["id"], h.get("kategorie")
        if not kat:
            m.F(aid, f"{hid}: Hauptsystem ohne kategorie")
        elif h.get("name") not in erlaubt.get(kat, set()):
            m.F(aid, f"{hid}: Name „{h.get('name')}“ nicht in den Glossarvorgaben für {kat} (Regel 9)")
        if a.get("artikeltyp") != "blatt":
            continue
        secs = abschnitt_von.get(hid, [])
        if not secs:
            m.F(aid, f"{hid} {h.get('name')}: kein Abschnitt mit dieser element_id")
        else:
            w = sum(woerter(p.get("text", "")) for s in secs for p in s["absaetze"])
            if w > 300:
                m.W(aid, f"{hid} {h.get('name')}: Abschnitt hat {w} Wörter (höchstens 300, Regel 3)")
            elif w < 80:
                # Richtwert, keine Korrekturrunde (Leitfaden 2.4, Abschnitt 10)
                m.H(aid, f"{hid} {h.get('name')}: Abschnitt hat {w} Wörter (Richtwert mindestens 80, Regel 3)")
        unter = [e for e in E.values() if e.get("id") != hid and hs_von(e.get("id")) == hid]
        if len(unter) < 2:
            m.F(aid, f"{hid} {h.get('name')}: weniger als zwei Elemente darunter")
        direkt_komp = [e for e in E.values() if e.get("eltern_id") == hid and e.get("typ") == "komponente"]
        hat_sub = any(e.get("eltern_id") == hid and e.get("typ") == "subsystem" for e in E.values())
        if len(direkt_komp) > 3 and not hat_sub:
            m.W(aid, f"{hid} {h.get('name')}: mehr als drei Komponenten ohne Subsystemebene (Regel 3)")
        if not funk_hs[hid]:
            m.F(aid, f"{hid} {h.get('name')}: keine Funktion zugeordnet")
        if not fluss_hs[hid]:
            m.F(aid, f"{hid} {h.get('name')}: an keinem Fluss beteiligt")

    # Elementnamen im Text
    text = " ".join(p.get("text", "") for p in ps).lower()
    for e in E.values():
        name = e.get("name", "")
        lang = [w for w in WORT.findall(name) if len(w) >= 5]
        if lang:
            ok = any(w.lower() in text for w in lang)
        else:
            ok = name.lower() in text
        if not ok:
            m.W(aid, f"{e.get('id')}: Elementname „{name}“ kommt im Text nicht vor")

    # Funktionen: Glossar und Perspektiven
    vorgabe = set(glossar["funktionen"])
    bisher = set()
    for k, b in alle.items():
        if k != aid and not isinstance(b, Exception) and b.get("modell"):
            bisher |= {f.get("name") for f in b["modell"].get("funktionen", [])}
    neu = set()
    for f in mo.get("funktionen", []):
        n = f.get("name", "")
        if n not in vorgabe and n not in bisher:
            neu.add(n)
    per = " ".join(p.get("text", "") for s in abschnitte if s.get("abschnittstyp") == "perspektiven"
                   for p in s["absaetze"]).lower()
    if a.get("artikeltyp") == "blatt":
        def genannt(name):
            # wörtlich oder gebeugt: jedes Wort des Funktionsnamens mit seinem Stamm (vier Buchstaben)
            if name.lower() in per:
                return True
            stems = []
            for w in WORT.findall(name):
                w = w.lower()
                if len(w) < 3 or w in ("und", "oder"):
                    continue
                for vor in ("zurück", "fort", "aus", "auf", "ein", "ab", "an", "zu"):
                    # trennbares Verb: „leuchten … aus“, „geben … ab“
                    if w.endswith("en") and w.startswith(vor) and len(w) - len(vor) >= 4:
                        stems += [vor, w[len(vor):][:4]]
                        break
                else:
                    stems.append(w[:4])
            return bool(stems) and all(re.search(r"\b" + re.escape(st), per) for st in stems)

        for f in mo.get("funktionen", []):
            if not genannt(f.get("name", "")):
                m.W(aid, f"{f.get('id')} „{f.get('name')}“ fehlt im Abschnitt Perspektiven (Regel 10)")
    pruefe_erweiterung(aid, a, mo, E, hs, hs_von, P, m)
    pruefe_offene_punkte(aid, a, neu, m)


def pruefe_erweiterung(aid, a, mo, E, hs, hs_von, P, m):
    """Varianten, Klärungsfragen, Anforderungsthemen (ab Schema 2.3)."""
    felder = ("varianten", "klaerungsfragen", "anforderungsthemen")
    neu_schema = a.get("schema_version", "0") >= "2.3"
    if not neu_schema:
        if a.get("artikeltyp") == "blatt":
            m.H(aid, f"Schema {a.get('schema_version')}: ohne Varianten, Klärungsfragen und Anforderungsthemen")
        return
    pflicht = felder if a.get("artikeltyp") == "blatt" else ("varianten", "klaerungsfragen")
    if True:
        for f in pflicht:
            if f not in mo:
                m.F(aid, f"modell.{f} fehlt (ab Schema 2.3 bei Blattartikeln Pflicht)")
    V = {}
    for liste, praefix in (("varianten", "V"), ("klaerungsfragen", "K"), ("anforderungsthemen", "R")):
        c = collections.Counter(x.get("id") for x in mo.get(liste, []))
        for k, n in c.items():
            if n > 1:
                m.F(aid, f"ID {k} in {liste} doppelt")
    for v in mo.get("varianten", []):
        V[v.get("id")] = v
        if v.get("element_id") not in E:
            m.F(aid, f"{v.get('id')}: element_id {v.get('element_id')} existiert nicht")
        for x in v.get("absatz_ids", []):
            if x not in P:
                m.F(aid, f"{v.get('id')}: absatz_id {x} existiert nicht")
        eigen = hs_von(v.get("element_id"))
        andere = False
        for w in v.get("auswirkungen", []):
            if w.get("element_id") not in E:
                m.F(aid, f"{v.get('id')}: Auswirkung auf {w.get('element_id')}, existiert nicht")
            elif hs_von(w.get("element_id")) != eigen:
                andere = True
        if not andere:
            m.H(aid, f"{v.get('id')} „{v.get('bezeichnung')}“: keine Auswirkung auf ein anderes Hauptsystem")
        for t in v.get("alternativen", []) + v.get("auswahlkriterien", []):
            if hat_ziffer(t):
                m.W(aid, f"{v.get('id')}: Ziffern in Alternativen oder Auswahlkriterien (Regel 7)")
                break
    frage_hs = collections.Counter()
    frage_v = collections.Counter()
    for k in mo.get("klaerungsfragen", []):
        for x in k.get("element_ids", []):
            if x not in E:
                m.F(aid, f"{k.get('id')}: element_id {x} existiert nicht")
        for x in {hs_von(x) for x in k.get("element_ids", [])}:
            frage_hs[x] += 1
        for x in k.get("variante_ids", []):
            if x not in V:
                m.F(aid, f"{k.get('id')}: variante_id {x} existiert nicht")
            frage_v[x] += 1
        if not k.get("frage", "").rstrip().endswith("?"):
            m.W(aid, f"{k.get('id')}: Klärungsfrage endet nicht mit Fragezeichen")
        if hat_ziffer(k.get("frage", "")) or NORMKUERZEL.search(k.get("frage", "")):
            m.W(aid, f"{k.get('id')}: Ziffern oder Normkürzel in der Klärungsfrage (Regel 7)")
    anf_hs = collections.Counter()
    for r in mo.get("anforderungsthemen", []):
        for x in r.get("element_ids", []):
            if x not in E:
                m.F(aid, f"{r.get('id')}: element_id {x} existiert nicht")
        for x in {hs_von(x) for x in r.get("element_ids", [])}:
            anf_hs[x] += 1
        frei = " ".join([r.get("thema", "")] + r.get("kenngroessen", []))
        if hat_ziffer(frei) or NORMKUERZEL.search(frei):
            m.W(aid, f"{r.get('id')}: Ziffern oder Normkürzel in Thema oder Kenngrößen; Regelwerke nur unter regelwerke mit Beleg (Regel 7)")
    if a.get("artikeltyp") != "blatt":
        if len(V) < 2:
            m.W(aid, f"nur {len(V)} Unterscheidungsmerkmale unter varianten (mindestens zwei, Regel 16)")
        if len(mo.get("klaerungsfragen", [])) < 3:
            m.W(aid, f"nur {len(mo.get('klaerungsfragen', []))} Klärungsfragen (mindestens drei, Regel 16)")
        for vid, v in V.items():
            if not frage_v[vid]:
                m.W(aid, f"{vid} „{v.get('bezeichnung')}“: keine Klärungsfrage verweist auf diese Variante (Regel 16)")
        return
    for h in hs:
        if not frage_hs[h["id"]]:
            m.F(aid, f"{h['id']} {h.get('name')}: keine Klärungsfrage (Regel 13)")
        if not anf_hs[h["id"]]:
            m.F(aid, f"{h['id']} {h.get('name')}: kein Anforderungsthema (Regel 14)")
    if len(V) < 3:
        m.W(aid, f"nur {len(V)} Varianten im Modellblock (mindestens drei, Regel 12)")
    for vid, v in V.items():
        if not frage_v[vid]:
            m.W(aid, f"{vid} „{v.get('bezeichnung')}“: keine Klärungsfrage verweist auf diese Variante (Regel 13)")
    m.H(aid, f"Erweiterung: {len(V)} Varianten, {len(mo.get('klaerungsfragen', []))} Klärungsfragen, "
             f"{len(mo.get('anforderungsthemen', []))} Anforderungsthemen")


def pruefe_offene_punkte(aid, a, neu, m):
    op = " ".join(a.get("offene_punkte", []))
    for n in sorted(neu):
        if "Glossarvorschlag" not in op or n.lower() not in op.lower():
            m.W(aid, f"Neue Funktion „{n}“ ohne Glossarvorschlag in offene_punkte (Regel 9)")
        else:
            m.H(aid, f"Glossarvorschlag: {n}")
    if a.get("status") not in STATUS:
        m.F(aid, f"status {a.get('status')} ungültig")


def cmd_validate(args):
    d = Path(args.dir)
    inv = inventar(d)
    glossar = lade(d / "glossar_vorgaben.json")
    schema = finde_schema(d, args.schema)
    alle = alle_artikel(d)
    m = Meldungen()
    if args.nur:
        ids = [x.strip() for x in args.nur.split(",")]
        for aid in ids:
            if aid not in alle:
                m.F(aid, f"Artikeldatei {artikel_pfad(d, aid)} fehlt")
    else:
        ids = sorted(alle)
        man = lade(d / "manifest.json", {})
        if man.get("schema_version") and schema is None:
            m.H("-", "Schema nicht gefunden")
        fehlt = [k for k in inv if k not in alle]
        if fehlt:
            m.H("-", f"{len(fehlt)} von {len(inv)} Inventarartikeln liegen noch nicht vor")
        for k in alle:
            if k not in inv:
                m.F(k, "Artikeldatei ohne Inventareintrag")
    for aid in ids:
        if aid in alle:
            pruefe_artikel(aid, alle[aid], d, inv, glossar, schema, alle, m)
    for stufe, aid, text in m.zeilen:
        if stufe == "HINWEIS" and args.ohne_hinweise:
            continue
        print(f"{stufe} {aid}: {text}")
    print(f"ERGEBNIS fehler={m.zaehle('FEHLER')} warnungen={m.zaehle('WARNUNG')} hinweise={m.zaehle('HINWEIS')}")
    return 1 if m.zaehle("FEHLER") else 0


# ---------------------------------------------------------------- status

def cmd_status(args):
    d = Path(args.dir)
    p = artikel_pfad(d, args.artikel_id)
    a = lade(p)
    if args.status in ("zu_pruefen", "geprueft"):
        ns = argparse.Namespace(dir=args.dir, nur=args.artikel_id, schema=args.schema, ohne_hinweise=True)
        import io
        import contextlib
        puffer = io.StringIO()
        with contextlib.redirect_stdout(puffer):
            rc = cmd_validate(ns)
        if rc:
            print(puffer.getvalue(), end="")
            sys.exit(f"FEHLER Status {args.status} nicht gesetzt: Validierung meldet Fehler")
    alt = a.get("status")
    a["status"] = args.status
    schreibe(p, a)
    aend = lade(d / "aenderungen.json", [])
    man = lade(d / "manifest.json", {})
    from datetime import date
    aend.append({
        "datum": date.today().isoformat(),
        "anlass": f"Status {alt} → {args.status}" + (f": {args.grund}" if args.grund else ""),
        "betroffene_artikel_ids": [args.artikel_id],
        "leitfaden_version": man.get("leitfaden_version", ""),
        "aufruftyp": "status",
        "modell_id": "orchestrator",
    })
    schreibe(d / "aenderungen.json", aend)
    print(f"{args.artikel_id}: {alt} → {args.status}")


# ---------------------------------------------------------------- plan, stats

def tiefe(inv, aid, cache):
    if aid in cache:
        return cache[aid]
    cache[aid] = 0  # schützt vor Zyklen
    kids = [k for k in inv.get(aid, {}).get("kindartikel_ids", []) if k in inv]
    cache[aid] = 1 + max(tiefe(inv, k, cache) for k in kids) if kids else 0
    return cache[aid]


def cmd_plan(args):
    d = Path(args.dir)
    inv = inventar(d)
    alle = alle_artikel(d)
    cache = {}
    eintraege = [e for e in inv.values() if not args.gruppe or gruppe_von(e) == args.gruppe]
    eintraege.sort(key=lambda e: (tiefe(inv, e["artikel_id"], cache), e["artikel_id"]))
    for e in eintraege:
        a = alle.get(e["artikel_id"])
        st = "fehlt" if a is None else ("defekt" if isinstance(a, Exception) else a.get("status"))
        bereit = all(k in alle and not isinstance(alle[k], Exception)
                     and alle[k].get("status") in ("zu_pruefen", "geprueft") for k in e.get("kindartikel_ids", []))
        print("\t".join([e["artikel_id"], e["artikeltyp"], f"ebene={tiefe(inv, e['artikel_id'], cache)}",
                         f"status={st}", "bereit" if bereit else "wartet", gruppe_von(e) or "?", e["bezeichnung"]]))


def cmd_gliederung(args):
    """Recherchegliederung als Markdown-Baum aus dem Inventar."""
    d = Path(args.dir)
    inv = inventar(d)
    kinder = {k for e in inv.values() for k in e.get("kindartikel_ids", [])}
    wurzeln = [e for e in inv.values() if e["artikel_id"] not in kinder]
    cache = {}
    zeilen = []

    def knoten(aid, ebene, pfad):
        e = inv[aid]
        weitere = [" > ".join(p) for p in e.get("recherchepfade", []) if p[-1] == e["bezeichnung"]
                   and p[:-1] != pfad]
        zusatz = f" — auch unter: {'; '.join(weitere)}" if weitere else ""
        typ = "Übersicht" if e["artikeltyp"] == "uebersicht" else "Blatt"
        zeilen.append(f"{'  ' * ebene}- **{aid}** {e['bezeichnung']} ({typ}){zusatz}")
        for k in e.get("kindartikel_ids", []):
            if k in inv:
                knoten(k, ebene + 1, pfad + [e["bezeichnung"]])

    for w in sorted(wurzeln, key=lambda e: e["artikel_id"]):
        knoten(w["artikel_id"], 0, [])
    typen = collections.Counter(e["artikeltyp"] for e in inv.values())
    stufen = collections.Counter(tiefe(inv, a, cache) for a in inv)
    man = lade(d / "manifest.json", {})
    print(f"# Recherchegliederung, Version {man.get('recherchegliederung_version', '?')}\n")
    print("<!-- Erzeugt mit: python3 tools/kb_tool.py gliederung kb > leitfaden/Recherchegliederung.md. "
          "Nicht von Hand bearbeiten; Quelle ist kb/inventar.json. -->\n")
    print(f"{len(inv)} Artikel: {typen['blatt']} Blattartikel, {typen['uebersicht']} Übersichten. "
          "Bearbeitungsebenen (0 = Blatt, zuerst): "
          + ", ".join(f"Ebene {k}: {v}" for k, v in sorted(stufen.items())) + ".\n")
    print("Artikel mit mehreren Recherchepfaden erscheinen unter jedem Elternartikel; "
          "ihre Glossargruppe ist die des ersten Pfads.\n")
    print("\n".join(zeilen))


def cmd_stats(args):
    d = Path(args.dir)
    print("artikel\tstatus\twoerter\tabsaetze\tbelegt\tquellen\telemente\tfunktionen\tfluesse\toffene_punkte")
    for aid, a in alle_artikel(d).items():
        if isinstance(a, Exception):
            print(f"{aid}\tdefekt")
            continue
        ps = absaetze(a)
        mo = a.get("modell") or {}
        print("\t".join(map(str, [aid, a.get("status"), sum(woerter(p.get("text", "")) for p in ps), len(ps),
                                  sum(p.get("begruendung") == "belegt" for p in ps), len(a.get("quellen", [])),
                                  len(mo.get("elemente", [])), len(mo.get("funktionen", [])),
                                  len(mo.get("fluesse", [])), len(a.get("offene_punkte", []))])))


# ---------------------------------------------------------------- main

def main():
    import signal
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("glossar"); g.add_argument("dir"); g.add_argument("--gruppe", required=True)
    v = sub.add_parser("validate"); v.add_argument("dir"); v.add_argument("--nur")
    v.add_argument("--schema"); v.add_argument("--ohne-hinweise", action="store_true")
    s = sub.add_parser("status"); s.add_argument("dir"); s.add_argument("artikel_id")
    s.add_argument("status", choices=STATUS); s.add_argument("--grund"); s.add_argument("--schema")
    p = sub.add_parser("plan"); p.add_argument("dir"); p.add_argument("--gruppe")
    st = sub.add_parser("stats"); st.add_argument("dir")
    gl = sub.add_parser("gliederung"); gl.add_argument("dir")
    args = ap.parse_args()
    rc = {"glossar": cmd_glossar, "validate": cmd_validate, "status": cmd_status,
          "plan": cmd_plan, "stats": cmd_stats, "gliederung": cmd_gliederung}[args.cmd](args)
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
