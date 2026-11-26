# Fahrzeugarchitektur-Wissensbasis: Überblick

## Worum es geht

Die Wissensbasis beschreibt generische Referenzarchitekturen für **191 Fahrzeugarten**. Es gibt 124 Blattartikel, etwa Pkw, Lokomotive, Mähdrescher oder ROV, und 67 Übersichten, etwa Nutzfahrzeuge, Schienenfahrzeuge oder Landfahrzeuge. Die Artikel verteilen sich auf fünf Gruppen:

| Gruppe | Artikel |
|---|---|
| Landfahrzeuge | 83 |
| Wasserfahrzeuge | 41 |
| Luftfahrzeuge | 32 |
| Raumfahrzeuge | 25 |
| Mehrraum- und Hybridfahrzeuge | 10 |

Die Wissensbasis gibt **Anleitung beim Modellieren von Fahrzeugen**. Beim Verfeinern von Architekturen und Anforderungen liefert sie **Vorschläge und konkrete Fragen**.

## Artikelschema 2.3

Jeder Artikel ist eine JSON-Datei (`kb/artikel/A-nnnn.json`). Sie enthält zwei verknüpfte Teile, den lesbaren Fließtext und einen maschinenlesbaren Modellblock.

### Kopf

- `artikel_id`, `titel`, `artikeltyp` (`blatt` oder `uebersicht`), `betrachtungsumfang` (was zum Artikel gehört und was nicht)
- `status`: `offen` → `in_arbeit` → `zu_pruefen` → `geprueft`
- `quellen`: jede Quelle mit Typ (Norm, Behörde, Fachliteratur …), URL und Abrufdatum
- `offene_punkte`: Rechercheaufträge und Glossarvorschläge

### Fließtext (`abschnitte` → `absaetze`)

Die Abschnitte folgen einer festen Reihenfolge: Gesamtsystem, je ein Abschnitt pro Hauptsystem, Querschnitt, Varianten, Flüsse, Perspektiven, Modellierung.

Jeder Absatz trägt seine **Begründung**:

- `belegt`: Die Aussage steht in einer abgerufenen Quelle, mit genauer Fundstelle.
- `hergeleitet`: Die Aussage folgt aus benannten Prämissen; die Sicherheit ist `hoch`, `mittel` oder `gering`.
- `gemischt` oder `modellwissen`: teils belegt, teils hergeleitet, oder Fachwissen ohne Quelle.

So ist bei jeder Aussage erkennbar, wie gut sie abgesichert ist.

### Modellblock (`modell`)

| Teil | Inhalt |
|---|---|
| `elemente` | Zerlegung in Gesamtsystem → Hauptsysteme → Subsysteme → Komponenten (Hauptsystemnamen aus dem Glossar) |
| `funktionen` | Was das Fahrzeug leistet (Verb–Objekt, etwa „Fahrzeug verzögern“) und welche Elemente es ausführen |
| `fluesse` | Energie-, Stoff-, Kraft- und Informationsflüsse zwischen Elementen, an Systemgrenzen mit benannter `schnittstelle` |
| `varianten` | Architekturentscheidungen, etwa die Antriebsart, mit Alternativen, Auswahlkriterien und Auswirkungen auf andere Systeme |
| `klaerungsfragen` | Konkrete Fragen an Modellierer oder Auftraggeber, mit Anlass (Architektur, Anforderung, Schnittstelle, Betrieb) und Relevanz |
| `anforderungsthemen` | Typische Anforderungsfelder mit Kenngrößen, Regelwerke nur mit Quelle und Fundstelle |

Text und Modell sind über IDs verknüpft (`E…` Element, `F…` Funktion, `V…` Variante, `K…` Klärungsfrage, `R…` Anforderungsthema, `P…` Absatz).

### Übersichten

Übersichten wiederholen die Kindartikel nicht. Sie zeigen die **gemeinsame Architektur** und die **Unterscheidungsmerkmale** der Kindartikel. Jede Übersicht enthält mindestens eine Frage zur Wahl der passenden Fahrzeugart.

## Qualitätssicherung

1. **Erstellung:** Ein Modell (Opus) schreibt jeden Artikel mit Quellenrecherche.
2. **Validierung:** `tools/kb_tool.py validate` prüft Schema, Verweise, Wortgrenzen, Glossarnamen, Zuordnungsliste und Abschnittsfolge.
3. **Review:** Ein unabhängiger Aufruf prüft Belege stichprobenartig an der Quelle sowie Herleitungen, fachliche Vollständigkeit und Brauchbarkeit.
4. **Revision:** Bei Befunden der Schwere „hoch“ wird der Artikel überarbeitet. Danach werden neue Belege nachgeprüft, erst dann folgt `geprueft`.
5. **Glossarpflege:** Nach jeder Welle werden Synonyme zusammengeführt und neue Namen aufgenommen. So verwenden alle Artikel dasselbe Vokabular.

## Was man mit dem fertigen Repository machen kann

- **Ein Fahrzeug modellieren:** Den passenden Artikel als Startpunkt nehmen und Elemente, Funktionen und Flüsse übernehmen, etwa als SysML-Blöcke, Aktivitäten oder Ports.
- **Die Fahrzeugart wählen:** Über die Übersichten von der Gruppe bis zum Blattartikel absteigen. Gemeinsame Grundmodelle lassen sich wiederverwenden, nur das Spezifische wird ergänzt.
- **Architekturen verfeinern:** Die Varianten zeigen, welche Entscheidungen anstehen und was sie in anderen Systemen auslösen. Ein Beispiel ist der batterieelektrische Antrieb mit seinen Folgen für Thermomanagement, Bremse und Bordnetz.
- **Gezielt nachfragen:** Die Klärungsfragen liefern eine sofort nutzbare Fragenliste für Workshops mit Auftraggebern oder Fachabteilungen.
- **Anforderungen aufbauen:** Die Anforderungsthemen mit Kenngrößen und belegten Regelwerken dienen als Gliederung und Checkliste für Lastenhefte.
- **Werkzeuge und KI-Assistenten speisen:** Die JSON-Struktur ist maschinenlesbar. Sie eignet sich für Generatoren (etwa Modellgerüste), Konsistenzprüfungen, Suche oder als Wissensbasis für einen Assistenten, der Vorschläge und Rückfragen erzeugt.
- **Belastbarkeit einschätzen:** Jede Aussage zeigt ihre Begründung und Sicherheit. Belegte Aussagen sind mit Quelle und Fundstelle nachprüfbar.

## Stand

Die Landfahrzeuge sind in Arbeit. Alle 60 Blattartikel sind geprüft, die 23 Übersichten werden gerade erstellt. Danach folgen Wasser-, Luft-, Raum- und Mehrraumfahrzeuge. Die Ergebnisse liegen auf dem Branch `lauf/2026-11-24`.

```bash
python3 tools/kb_tool.py plan kb
```

```bash
python3 tools/kb_tool.py validate kb --nur A-0008
```
