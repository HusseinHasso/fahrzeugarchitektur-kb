# Leitfaden 2.4 – Erstellung der Fahrzeugarchitektur-Wissensbasis

> **Fassung 2.4 vom 2026-11-24.** Sie beruht auf einer Rekonstruktion von Leitfaden 2.3, dessen Original nicht
> vorlag, und erweitert sie um den Zweck der Wissensbasis und Schema 2.3 (Abschnitt 10). Die Rekonstruktion ist aus
> `Arbeitsauftrag_Artikel.md`, `artikel.schema.json` (Schema 2.2), `glossar_vorgaben.json` und den Dateien von
> Probelauf 2 (`probelaeufe/probelauf2/`) hergeleitet. Jede Festlegung trägt eine Kennung:
> **[belegt]** steht so oder sinngemäß in diesen Dateien; **[ergänzt]** ist eine neue Festlegung, die die Lücke
> schließt und vom Auftraggeber bestätigt oder geändert werden sollte.
> Bei Widerspruch gehen Arbeitsauftrag und Schema diesem Leitfaden vor.

## 0. Zweck, Gegenstand und Dateien

**Zweck.** Die Wissensbasis gibt Anleitung und Unterstützung beim Modellieren von Fahrzeugen. Sie dient dazu,
beim Verfeinern von Architekturen und Anforderungen Vorschläge zu machen und konkrete Fragen zu stellen.
**[vom Auftraggeber festgelegt, 2026-11-24]** Daraus folgen drei Nutzungen jedes Artikels:

1. **Anleiten:** Dekomposition, Funktionszuordnung, Flüsse und Modellierungsbezug zeigen, wie die Fahrzeugart als
   Modell aufgebaut wird.
2. **Vorschlagen:** Varianten mit Alternativen, Auswahlkriterien und Auswirkungen auf andere Hauptsysteme
   (`modell.varianten`); Vergleich mit verwandten Fahrzeugarten über die Übersichten.
3. **Nachfragen:** Klärungsfragen je Hauptsystem (`modell.klaerungsfragen`) und Anforderungsthemen mit Kenngrößen
   (`modell.anforderungsthemen`).

Die Kennzeichnung jedes Absatzes nach Begründung und Sicherheit erlaubt einem Assistenten, belegte Lösungen von
Vorschlägen zu unterscheiden.

**Gegenstand.** Die Wissensbasis beschreibt für jede Fahrzeugart des Inventars die generische Referenzarchitektur als
Fließtextartikel mit maschinenlesbarem Modellblock (Elemente, Funktionen, Flüsse, ab Schema 2.3 auch Varianten,
Klärungsfragen und Anforderungsthemen). **[belegt; Erweiterung 2.4]**

| Datei | Zweck |
|---|---|
| `leitfaden/Leitfaden_2.4.md` | dieser Leitfaden |
| `leitfaden/Arbeitsauftrag_Artikel.md` | Vorlage für jeden Erstellungs-, Übersichts- und Korrekturaufruf **[belegt]** |
| `leitfaden/Arbeitsauftrag_Review.md` | Vorlage für jeden Review-Aufruf, Ausgabeformat der Befunde **[ergänzt]** |
| `leitfaden/Referenzartikel_Lkw.md` | Maßstab für Aufbau, Dramaturgie und Detailtiefe, kein Beleg **[belegt]** |
| `leitfaden/artikel.schema.json` | Schema 2.3 für jeden Artikel (2.2 bleibt lesbar) **[belegt; Erweiterung 2.4]** |
| `leitfaden/Recherchegliederung.md` | Taxonomie als Baum, erzeugt aus `kb/inventar.json` **[ergänzt]** |
| `kb/manifest.json` | Versionen: Leitfaden, Schema, Recherchegliederung, Laufart **[belegt]** |
| `kb/inventar.json` | 191 Artikel mit Typ, Recherchepfaden und Kindartikeln **[belegt]** |
| `kb/glossar_vorgaben.json` | verbindliche Hauptsystem- und Funktionsnamen **[belegt]** |
| `kb/aenderungen.json` | ein Eintrag je Aufruf und je Statuswechsel **[belegt]** |
| `kb/protokoll.jsonl` | eine Zeile je Aufruf mit Verbrauchsdaten **[belegt]** |
| `kb/artikel/A-nnnn.json` | die Artikel **[belegt]** |
| `tools/kb_tool.py` | `glossar`, `validate`, `status`, `plan`, `stats`, `gliederung` **[belegt, Werkzeug nachgebaut]** |

## 1. Modellwahl und Einstellungen

| Aufruftyp | Modell | Einstellungen |
|---|---|---|
| `erstellung` (Blattartikel) | `claude-opus-5-5` | Extended Thinking, Schema als strukturierte Ausgabe, Quellenzugriff (Websuche und Abruf) **[belegt]** |
| `uebersicht` | `claude-opus-5-5` | wie Erstellung, zusätzlich alle Kindartikel als Eingabe **[belegt]** |
| `review` | `claude-opus-5-5` | Extended Thinking, Quellenzugriff zum Nachprüfen der Fundstellen **[belegt: Modell; ergänzt: Ablauf, Abschnitt 6]** |
| `korrektur` | dasselbe Modell wie der Aufruf, der den Artikel erzeugt hat | wie Erstellung **[ergänzt; im Probelauf so gehandhabt]** |
| `revision` | `claude-opus-5-5` | wie Erstellung, zusätzlich der bisherige Artikel **[belegt: Eingabe; ergänzt: Modell]** |

- Quellenzugriff ist im Gesamtlauf `ja`. `nein` nur für ausdrücklich so geplante Läufe; dann bleiben
  `quellen` und `belege` leer. **[belegt: Regel 6; ergänzt: Standard ja]**
- Jeder Aufruf wird mit `aufruftyp` und `modell_id` in `aenderungen.json` protokolliert. **[belegt]**
- Kann der Orchestrator das tatsächlich ausführende Modell nicht nachweisen, steht im `anlass`
  „Modell angefordert, nicht verifiziert“. **[belegt, Probelauf 2]**
- Abweichende Modelle (etwa Sonnet zum Vergleich) nur in Läufen mit `laufart: probelauf`. **[ergänzt]**

## 2. Ablauf eines Laufs

1. **Vorbereitung.** `manifest.json` prüfen; `kb_tool.py validate kb` muss ohne FEHLER laufen. `laufart` ist
   `probelauf` oder `gesamtlauf`. **[ergänzt]**
2. **Reihenfolge.** `kb_tool.py plan kb` liefert sie: zuerst alle Blattartikel (Ebene 0), dann die Übersichten
   von unten nach oben (Ebene 1 bis 3). Eine Übersicht startet erst, wenn alle Kindartikel `zu_pruefen` oder
   `geprueft` sind (`bereit`). **[ergänzt; folgt aus Vorgehen Schritt 6 und dem Schemafeld herangezogene_artikel_ids]**
3. **Wellen.** Eine Welle umfasst die Blattartikel einer Gruppe (erste Ebene der Recherchegliederung:
   Landfahrzeuge, Wasserfahrzeuge, Luftfahrzeuge, Raumfahrzeuge, Mehrraum- und Hybridfahrzeuge). Nach jeder Welle
   wird das Glossar fortgeschrieben (Abschnitt 5), bevor die nächste beginnt. Die Übersichten folgen, wenn alle
   Wellen ihrer Teilbäume abgeschlossen sind. **[ergänzt; „nach jeder Welle fortschreiben“ belegt in glossar_vorgaben.json]**
4. **Parallelität.** Innerhalb einer Welle dürfen Artikel parallel laufen. Das Glossar „bisher verwendet“ wird
   dann zu Beginn der Welle einmal erzeugt; Abweichungen innerhalb der Welle löst die Glossarpflege. **[ergänzt]**
5. **Ein Aufruf je Artikel.** Der Orchestrator füllt den Arbeitsauftrag mit `artikel_id`, `bezeichnung`,
   `artikeltyp`, Quellenzugriff und `gruppe` und gibt mit: Arbeitsauftrag, Referenzartikel, Ausgabe von
   `kb_tool.py glossar kb --gruppe {gruppe}`, Inventareintrag, Schema; bei Übersichten die Kindartikel, bei
   Revisionen den bisherigen Artikel. **[belegt]**
6. **Ablage.** Die Ausgabe wird unverändert als `kb/artikel/{artikel_id}.json` gespeichert. Der Orchestrator
   ändert am Inhalt nichts außer dem Status. **[ergänzt; Status belegt]**
7. **Sicherung.** Nach jedem abgeschlossenen Artikel (nach der letzten Korrekturrunde) wird committet und gepusht,
   damit ein Abbruch fortgesetzt werden kann. Der Lauf arbeitet auf einem eigenen Branch
   (`lauf/<datum>`), die Übernahme nach `main` erfolgt per Pull Request. **[ergänzt]**

Gruppe eines Artikels ist das erste Element seines ersten Recherchepfads. Artikel mit mehreren Pfaden
(A-0105 Flugauto, A-0109 Raumgleiter) gehören zur Gruppe des ersten Pfads und werden in jeder betroffenen Übersicht
herangezogen. **[ergänzt]**

## 3. Validierung und Korrekturrunden

- Nach jeder Erstellung, Korrektur und Revision: `kb_tool.py validate kb --nur {artikel_id}`. **[belegt]**
- Meldungsstufen **[belegt: Stufen; ergänzt: Zuordnung im Werkzeug]**:
  - `FEHLER`: Verstoß gegen Schema, Verweise, Glossarnamen, Kategorien, Abschnittsfolge, Beleglogik.
  - `WARNUNG`: Verstoß gegen weiche Vorgaben (Wortzahlen, Ziffern in nicht belegten Absätzen, Perspektiven,
    Elementnamen im Text, Sicherheitsverteilung, fehlender Glossarvorschlag).
  - `HINWEIS`: Kennzahlen (Wortzahl, Belegquote, Glossarvorschläge). Gehen nicht an das Modell.
- Gibt es FEHLER oder WARNUNG, startet eine Korrekturrunde: Der Orchestrator gibt nur diese Zeilen und den
  Artikel zurück, das Modell korrigiert nur die gemeldeten Stellen. **[belegt]**
- **Höchstens zwei Korrekturrunden.** **[ergänzt; im Probelauf 2 wurden zwei benötigt]** Danach:
  - nur WARNUNG übrig: Status `zu_pruefen`, Warnungen im Protokoll und im `anlass` vermerken;
  - FEHLER übrig: Status bleibt `in_arbeit`, Artikel kommt auf die Nacharbeitsliste
    (`kb_tool.py plan` zeigt ihn), der Lauf geht mit dem nächsten Artikel weiter.
- Ein hoher Anteil nicht belegter Absätze ist kein Korrekturauftrag, sondern Recherchebedarf im Protokoll. **[belegt]**

## 4. Status

| Status | Bedeutung | gesetzt von |
|---|---|---|
| `offen` | im Inventar, noch kein Artikel (Datei fehlt oder Platzhalter) | Orchestrator **[belegt: Wert; ergänzt: Bedeutung]** |
| `in_arbeit` | erstellt oder in Korrektur; jede Modellausgabe trägt diesen Status | Modell **[belegt]** |
| `zu_pruefen` | Validierung ohne FEHLER, wartet auf Review | Orchestrator mit `kb_tool.py status` **[belegt]** |
| `geprueft` | Review ohne offene Befunde der Schwere `hoch` | Orchestrator mit `kb_tool.py status` **[belegt: Werkzeug; ergänzt: Kriterium]** |

`kb_tool.py status` verweigert `zu_pruefen` und `geprueft`, solange FEHLER vorliegen, und schreibt jeden Wechsel
in `aenderungen.json`. Nur der Orchestrator setzt diese beiden Stufen. **[belegt: nur Orchestrator; ergänzt: Prüfung]**

## 5. Glossarpflege

- `glossar_vorgaben.json` ist die einzige verbindliche Namensliste. Die Datei `glossar_<Gruppe>.txt` ist nur die
  Ausgabe von `kb_tool.py glossar` und wird nicht gepflegt. **[belegt durch Probelauf 2]**
- Nach jeder Welle sammelt der Orchestrator alle „Glossarvorschlag:“-Einträge der Welle
  (`kb_tool.py validate kb` zeigt sie als HINWEIS) und entscheidet je Vorschlag **[ergänzt]**:
  - **aufnehmen** in `funktionen` oder `hauptsysteme` (mit Fahrzeugart in Klammern, wenn nur für sie gültig);
  - **zusammenführen**, wenn mehrere Vorschläge dieselbe Leistung meinen; der gewählte Name wird aufgenommen,
    betroffene Artikel erhalten eine Revision;
  - **ablehnen**, wenn ein gelisteter Name passt; betroffene Artikel erhalten eine Revision.
- Jede Änderung an `glossar_vorgaben.json` aktualisiert dort `stand` und bekommt einen Eintrag in
  `aenderungen.json` (`aufruftyp: glossar`). **[ergänzt]**
- Offen aus Probelauf 2: „Tether führen“ und „Tetherlänge anpassen“ meinen dieselbe Funktion; „Druck ausgleichen“,
  „Nebenaggregate antreiben“, „Innenraum klimatisieren“, „Unterdruck bereitstellen“ sind zu entscheiden.

## 6. Review

**[ergänzt bis auf Modellwahl]**

- Jeder Artikel mit `zu_pruefen` erhält einen Review-Aufruf. Eingaben: Artikel, Arbeitsauftrag, Referenzartikel,
  Schema, Glossarausgabe; bei Übersichten die Kindartikel.
- Der Reviewer prüft, was `validate` nicht prüfen kann:
  1. Stichprobe von mindestens drei belegten Absätzen: Quelle abrufen, steht jede Aussage in der Fundstelle?
  2. Fachliche Richtigkeit und Reichweite der hergeleiteten Absätze (trägt die Herleitung, stimmt die Sicherheit?).
  2a. Brauchbarkeit für den Zweck: Sind die Varianten echte Architekturentscheidungen mit zutreffenden
     Auswirkungen? Sind die Klärungsfragen konkret, beantwortbar und für die Verfeinerung nötig? Fehlen
     naheliegende Anforderungsthemen?
  3. Vollständigkeit der Architektur gegenüber der Fahrzeugart; fehlende strukturändernde Varianten.
  4. Passen `begruendung`, `aussagetyp` und Quellentyp?
  5. Bei Übersichten: Sind Gemeinsamkeiten und Unterschiede der Kindartikel zutreffend wiedergegeben?
- Ausgabe: JSON-Liste von Befunden `{absatz_id|element_id, schwere: hoch|mittel|gering, befund, vorschlag}`.
  Der Reviewer ändert den Artikel nicht.
- Befunde `hoch` führen zu einer Revision (`aufruftyp: revision`, Eingabe: bisheriger Artikel und Befunde), danach
  erneut Validierung. Trägt die Revision neue Belege oder Regelwerke ein, prüft der Reviewer nur diese nach
  (Feld `nachpruefung` in der Review-Datei); erst wenn alle bestätigt sind, folgt `geprueft`. Ohne Befund `hoch` setzt der Orchestrator `geprueft`; Befunde `mittel` und `gering` werden
  im `anlass` vermerkt.
- Review-Befunde werden unter `kb/reviews/{artikel_id}.json` abgelegt. Vorlage und Ausgabeformat: `leitfaden/Arbeitsauftrag_Review.md`.

## 7. Protokollierung

**`aenderungen.json`**, ein Eintrag je Aufruf und Statuswechsel **[belegt]**:

```json
{"datum": "JJJJ-MM-TT", "anlass": "…", "betroffene_artikel_ids": ["A-0001"],
 "leitfaden_version": "2.4", "aufruftyp": "erstellung|uebersicht|korrektur|revision|review|status|glossar",
 "modell_id": "claude-opus-5-5"}
```

`aufruftyp` `erstellung` und `korrektur` sind belegt, die übrigen Werte sind ergänzt.

**`protokoll.jsonl`**, eine Zeile je Modellaufruf, **vollständig** auszufüllen **[belegt: Felder; ergänzt: Pflicht]**:

```json
{"artikel": "A-0001", "modell": "opus", "aufruftyp": "erstellung", "runde": 0, "tokens": 0, "tool_uses": 0,
 "dauer_s": 0, "fehler": 0, "warnungen": 0, "recherchebedarf": false}
```

- `runde` 0 ist die Erstellung, 1 und 2 sind Korrekturrunden.
- `fehler` und `warnungen` sind die Zahlen aus der Validierung **nach** diesem Aufruf.
- `recherchebedarf: true`, wenn weniger als ein Viertel der Absätze belegt ist (Arbeitsauftrag, Korrekturrunden).
- In Probelauf 2 fehlten eine Zeile (Opus A-0001) und die Zählwerte der Sonnet-Korrekturrunden. Das ist künftig
  ein Fehler im Lauf.

## 8. Versionierung

- `leitfaden_version`, `schema_version` und `recherchegliederung_version` stehen in `manifest.json` und in jedem
  Eintrag von `aenderungen.json`. **[belegt]**
- Änderungen an Regeln oder Arbeitsauftrag erhöhen die Leitfadenversion. Bestehende Artikel bleiben gültig, bis
  eine Revision sie anhebt. **[ergänzt]**
- Änderungen am Inventar (neue, gestrichene oder umgehängte Artikel) erhöhen die Version der Recherchegliederung.
  `leitfaden/Recherchegliederung.md` wird danach neu erzeugt. **[ergänzt]**

## 9. Offene Punkte zu diesem Leitfaden

- Bestätigen oder korrigieren: alle **[ergänzt]**-Festlegungen, besonders die Höchstzahl der Korrekturrunden,
  das Kriterium für `geprueft` und den Review-Ablauf.
- Klären, ob `kb_tool.py validate` im Original andere Prüfungen oder Stufen hatte.
- Für den Gesamtlauf den Ressourcenrahmen festlegen: Probelauf 2 brauchte je Blattartikel etwa 120.000 bis 150.000
  Tokens und 6 bis 11 Minuten.

## 10. Änderungen in Fassung 2.4 gegenüber 2.3

- **Zweck** der Wissensbasis aufgenommen (Abschnitt 0).
- **Schema 2.3**: im Modellblock neu `varianten`, `klaerungsfragen` und `anforderungsthemen` (bei Blattartikeln
  Pflicht), an Flüssen optional `schnittstelle`. Der Fließtext und seine Wortgrenzen bleiben unverändert.
- **Arbeitsauftrag**: Abschnitt „Zweck der Wissensbasis“, Vorgehen Schritt 1 ergänzt, Regeln 12 bis 15, zwei
  Punkte in der Prüfliste.
- **`kb_tool.py validate`**: prüft die neuen Felder. FEHLER: kaputte Verweise, Hauptsystem ohne Klärungsfrage oder
  ohne Anforderungsthema, fehlende Pflichtfelder. WARNUNG: weniger als drei Varianten, Variante ohne Klärungsfrage,
  Frage ohne Fragezeichen, Ziffern oder Normkürzel außerhalb von `regelwerke`. HINWEIS: Variante ohne Auswirkung
  auf ein anderes Hauptsystem.
- **Review** (Abschnitt 6) prüft zusätzlich die Brauchbarkeit von Varianten, Fragen und Anforderungsthemen.
- Artikel nach Schema 2.2 (Probelauf 2) bleiben gültig. `validate` meldet bei ihnen einen HINWEIS.
- **Übersichten** (Arbeitsauftrag, Regel 16): Abschnittsfolge Einleitung, gemeinsame Architektur, Unterscheidungsmerkmale,
  Zusammenfassung, Modellierungsbezug; 800 bis 1.500 Wörter; Modellblock Pflicht mit gemeinsamen Hauptsystemen,
  mindestens zwei Unterscheidungsmerkmalen und drei Klärungsfragen. `validate` prüft das ab Schema 2.3.
- **Review-Vorlage** `Arbeitsauftrag_Review.md` neu.
- **Glossar** (Stand 2026-11-24, nach Probelauf 3): aufgenommen „Unterdruck bereitstellen“, „Innenraum klimatisieren“,
  „Tether ausgeben und einholen“ (ersetzt die Vorschläge „Tether führen“ und „Tetherlänge anpassen“). Offen:
  „Druck ausgleichen“, „Nebenaggregate antreiben“.
- **Mindestlänge der Hauptsystem-Abschnitte** (Festlegung des Auftraggebers, 2026-11-24): 80 Wörter sind ein Richtwert
  für die Mindestlänge, keine exakte Grenze. `validate` meldet eine Unterschreitung nur als HINWEIS, sie löst keine
  Korrekturrunde aus. Die Obergrenze je Hauptsystem-Abschnitt liegt bei 300 Wörtern (WARNUNG).
- **Toleranz der Wortgrenzen** (Festlegung des Auftraggebers, 2026-11-24): Alle Wortgrenzen (Artikel 1.300 bis 2.000,
  Übersicht 800 bis 1.500, Hauptsystem-Abschnitt höchstens 300) gelten mit ±50 Wörtern Toleranz. Innerhalb der Toleranz
  meldet `validate` einen HINWEIS, erst darüber hinaus eine WARNUNG mit Korrekturrunde.
- **Nach der Generalprobe** (2026-11-24): Zuordnungsliste im Glossar (`zuordnung`, verbindlich, von `validate` als
  WARNUNG geprüft); im Arbeitsauftrag Zuordnung (Regel 1), Geltungsbereich von Regelwerken (Regel 8), Speicher und
  Wandler je Antriebsart (Regel 12), belegte Absätze beim Kürzen nur umformulieren (Korrekturrunden); Nachprüfung
  neuer Belege nach einer Revision (Abschnitt 6).
