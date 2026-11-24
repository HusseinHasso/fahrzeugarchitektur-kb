# Arbeitsauftrag je Artikel (Vorlage, Leitfaden 2.3)

Ein Aufruf bearbeitet genau einen Artikel. Der Orchestrator füllt die Platzhalter in `{}` und gibt mit: diese Vorlage, `Referenzartikel_Lkw.md`, die Ausgabe von `kb_tool.py glossar <dir> --gruppe {gruppe}`, den Inventareintrag und `artikel.schema.json`. Bei Übersichten kommen die Kindartikel hinzu, bei Revisionen der bisherige Artikel.

Modellwahl und Einstellungen stehen im Leitfaden, Abschnitt 1. Erstellung, Übersichten und Reviewer laufen mit `claude-opus-5-5`, mit Extended Thinking und dem Schema als strukturierter Ausgabe. Jeder Aufruf wird mit `aufruftyp` und `modell_id` in `aenderungen.json` protokolliert.

Für Korrekturrunden gibt der Orchestrator die Zeilen `FEHLER` und `WARNUNG` aus `kb_tool.py validate <dir> --nur {artikel_id}` zurück, die Zeilen `HINWEIS` nicht.

---

Erstelle den Artikel **{artikel_id} {bezeichnung}** ({artikeltyp}) nach Leitfaden 2.3. Quellenzugriff: **{ja|nein}**. Gib ausschließlich ein JSON-Objekt aus, das `artikel.schema.json` erfüllt (`schema_version: 2.2`, `status: in_arbeit`). Schreibe auf Deutsch.

**Vorrang.** Vollständigkeit geht vor Belegquote. Ein vollständiger, sorgfältig hergeleiteter Artikel mit wenigen Belegen ist besser als ein lückenhafter mit vielen. Nicht belegte Aussagen sicherst du durch Herleitung ab (Vorgehen, Schritt 3). Du streichst sie nicht.

**Ziel (Blattartikel).** Beschreibe die **generische Referenzarchitektur der Fahrzeugart**, in Aufbau, Dramaturgie und Detailtiefe wie im Referenzartikel Lkw. Schreibe zusammenhängende Fließtextabsätze über Aufgabe, Bauteile, Wirkzusammenhang, Varianten und Schnittstellen. Der Artikel ist kein Datenblatt eines Modells und keine Sammlung belegter Einzelbauweisen. Quellen ergänzen und präzisieren den Text, sie begrenzen ihn nicht.

**Vorgehen**
1. Leite den Artikel schrittweise her, als Arbeitsnotiz im Denken, die du nicht ausgibst:
   - Systemgrenze und Hauptfunktionen
   - Hauptsysteme je Kategorie (Regel 1)
   - je Hauptsystem: Subsysteme, Komponenten, Flüsse, Schnittstellen und Varianten
   - Funktionen mit ihrer Zuordnung
   - Lücken
2. Mit Quellenzugriff: Suche Quellen gezielt für Grundaufbau, Varianten, Zahlen, Normen und Abgrenzungen (Regel 6). Füll verbleibende Lücken aus Herleitung oder Fachwissen.
3. **Absichern.** Prüfe in der Arbeitsnotiz jede Aussage ohne Beleg in vier Schritten:
   - (a) Folgt sie aus dem Funktionsprinzip oder einer physikalischen Notwendigkeit? Ein Beispiel: Ein elektrischer Antrieb braucht Energiespeicher, Wandler und Wärmeabfuhr.
   - (b) Passt sie zu den belegten Absätzen und den anderen Hauptsystemen? Jeder Fluss braucht Ursprung und Ziel, jede Funktion ein ausführendes Element.
   - (c) Gegenprobe: Gibt es Bauweisen oder Betriebsarten, für die sie nicht gilt? Dann schränkst du die Reichweite ein oder beschreibst die Variante.
   - (d) Ist sie nur von einer anderen Fahrzeugart übertragen? Dann ist sie ein Analogieschluss.

   Trägt (a) oder (b), kennzeichnest du die Aussage als `hergeleitet` und schreibst die Prämissen in `herleitung`. Bleibt nur Fachwissen, kennzeichnest du sie als `modellwissen`. Die Sicherheit richtet sich nach dem Ergebnis (Regel 5). Was weder herleitbar noch als Fachwissen tragfähig ist, kommt in `offene_punkte`.
4. Formuliere erst danach Text und `modell`.
5. Arbeite vor der Ausgabe die Prüfliste ab.
6. Übersichten: Vergleiche die Kindartikel, recherchiere eigenständig zum Elterntaxon, gleiche beides ab und schreib erst dann den Text. Berücksichtige alle Kindartikel in `herangezogene_artikel_ids`.

**Regeln**
1. **Kategorien.** Setze `kategorie` an jedem Hauptsystem. Zur Auswahl stehen: struktur_fahrwerk, antrieb, energieversorgung, lenkung, bremse, bedienraum, aufbau_nutzlast, elektrik_elektronik, steuerung_information, assistenz_sicherheit, beleuchtung_sicht, thermomanagement, nebensysteme und sonstig. `sonstig` ist nur für fahrzeugartspezifische Systeme gedacht, etwa Auftrieb oder Stufentrennung. Nicht zutreffende Kategorien führst du mit kurzem Grund in `modell.entfallene_kategorien`. Streich nichts stillschweigend.
2. **Dramaturgie.** Die Abschnitte folgen in dieser Reihenfolge:
   1. Einleitung (`gesamtsystem`): Definition, Zweck, Schnittstellenarten, Hinweis auf die Dekomposition
   2. je Hauptsystem ein Abschnitt (`hauptsystem` mit `element_id`): Aufgabe, zentrale Struktur und Komponenten, Wirkzusammenhang entlang eines Flusses, Varianten und Schnittstellen. Das gilt auch für die Neben- und Versorgungssysteme.
   3. Zusammenfassung der obersten Ebene (`gesamtsystem`)
   4. Modellierungsbezug (`modellierung`): mindestens drei Dekompositionspfade über mehrere Ebenen, Ports und Konnektoren, Diagrammarten
   5. Flüsse (`fluesse`)
   6. Perspektiven (`perspektiven`)

   Offene Punkte stehen nur im Feld `offene_punkte`.
3. **Umfang.** Der Artikel hat 1.300 bis 2.000 Wörter, gezählt über alle Absätze. Je Hauptsystem-Abschnitt sind es 80 bis 150 Wörter. Schreib die Abschnitte Flüsse und Perspektiven knapp, als dichte Aufzählungssätze und ohne Wiederholung des Haupttexts. Hauptsysteme mit mehr als drei Komponenten bekommen eine Subsystemebene. Varianten, die die interne Struktur ändern, beschreibst du am betroffenen Hauptsystem, mit ihren Auswirkungen auf andere Hauptsysteme.
4. **Begründung.** Jeder Absatz hat genau eine `begruendung`:
   - `belegt` nur, wenn jede Aussage des Absatzes in der Fundstelle steht. Eigene Schlüsse, Lastpfade, Anzahlen oder Anordnungen gehören in einen eigenen Absatz mit `hergeleitet`.
   - `hergeleitet` mit `herleitung` aus Prämissen und Schluss.
   - `modellwissen`.
   - `gemischt` nur ausnahmsweise.

   Der Grundaufbau eines Hauptsystems darf `hergeleitet` oder `modellwissen` sein. Ist eine Herleitung nach Vorgehen, Schritt 3, möglich, wählst du `hergeleitet` statt `modellwissen`.
5. **Sicherheit** (bei allem außer `belegt`):
   - `hoch`: zwingend aus dem Funktionsprinzip oder durch mehrere unabhängige Quellen gestützt
   - `mittel`: eine Quelle oder eine Herleitung aus einem belegten Absatz dieses Artikels
   - `gering`: Analogieschluss von einer anderen Fahrzeugart (auch vom Lkw), Annahme über eine Bauweise oder Variante ohne Quelle, Detailangabe aus Modellwissen

   Keine Stufe darf über 90 % der nicht belegten Absätze tragen.
6. **Quellen.**
   - Nur Quellen, die in diesem Lauf abgerufen und gelesen wurden, und nur Fundstellen aus dem gelesenen Inhalt.
   - `quellentyp` steht an jeder Quelle:
     - `norm`: Norm, Gesetz, Verordnung, Regelwerk
     - `behoerde`: Behörde, staatliche Forschungseinrichtung, Raumfahrtagentur
     - `fachliteratur`: Lehrbuch, Handbuch, wissenschaftliche Veröffentlichung, Hochschulskript
     - `fachpresse`: Fach- und Branchenmagazin
     - `nachschlagewerk`: Enzyklopädie, auch offene wie Wikipedia
     - `verband`: Verband, Prüfinstitution
     - `hersteller`: Hersteller- und Zuliefererunterlagen
   - Wikipedia und andere offene Nachschlagewerke sind als Quelle erlaubt (`nachschlagewerk`). Nennt der Artikel eine leicht erreichbare Primärquelle, rufst du sie zusätzlich ab und belegst damit Zahlen, Normen und Abgrenzungen.
   - Passt kein Typ, lass die Quelle weg. Setz nie einen unzutreffenden Typ.
   - Bevorzuge Norm, Behörde und Fachliteratur. Herstellerquellen und Fachpresse belegen nur das genannte Modell oder die genannte Baureihe.
   - Bei Quellenzugriff `nein` bleiben `quellen` und `belege` leer.
7. **Zahlen und Normen.** Zahlenwerte, Kennwerte, Normverweise, Hersteller- und Modellangaben nur mit Beleg, sonst weglassen.
8. **Reichweite.** Nenne, wofür eine Aussage gilt: Fahrzeugart, Bauweise oder Baureihe. „Typischerweise“ nur, wenn Quelle oder Herleitung es stützen. Modellvorschläge kennzeichnest du mit `aussagetyp: modellannahme`.
9. **Vokabular.** Hauptsystemnamen übernimmst du aus den Glossarvorgaben. Funktionsnamen (Verb–Objekt, Infinitiv) ebenfalls zuerst daraus, dann aus den bisher verwendeten Namen, vorrangig aus derselben Gruppe. Einen neuen Namen vergibst du nur, wenn keiner passt, und nie als Synonym. Jeder neue Name kommt in `offene_punkte` als „Glossarvorschlag: …“.
10. **Perspektiven.** Der Abschnitt ordnet alle Funktionen des Modellblocks den ausführenden Systemen und Komponenten zu, nicht nur beispielhaft.
11. **Offene Punkte.** Hier stehen konkreter Recherchebedarf (Quelle oder Suchbegriff), nicht herleitbare Bestandteile und Glossarvorschläge, keine allgemeinen Geltungshinweise.

**Prüfliste vor der Ausgabe** (im Denken, ohne Skript)
- Vollständigkeit: Jede Kategorie ist abgedeckt oder begründet entfallen. Jedes Hauptsystem ist bis zu den Komponenten zerlegt. Die strukturändernden Varianten sind beschrieben.
- Jedes Hauptsystem hat einen Abschnitt mit seiner `element_id`, mindestens zwei Elemente darunter, mindestens eine Funktion und mindestens einen Fluss, an dem es selbst oder ein Element darunter beteiligt ist.
- Jeder Elementname kommt wörtlich im Text vor, mindestens ein Wort mit fünf oder mehr Buchstaben daraus. Text und Modellblock verwenden dieselben Bezeichnungen.
- Jede `absatz_id`, `element_id`, jedes `von` und `nach` verweist auf etwas Vorhandenes. Alle IDs sind eindeutig.
- Jede Quelle hat einen zutreffenden `quellentyp` und wird in mindestens einem Beleg verwendet.
- Die Wortzahl liegt zwischen 1.300 und 2.000. In nicht belegten Absätzen stehen keine Ziffern und keine Normkürzel.

**Korrekturrunden**
- Korrigiere nur die gemeldeten Stellen und gib das vollständige JSON mit `status: in_arbeit` erneut aus.
- Neue Quellen und neue Absätze ergänzt du nur, wenn eine Meldung es erfordert. Ein hoher Anteil nicht belegter Absätze ist kein Korrekturauftrag. Er wird im Protokoll als Recherchebedarf vermerkt.
- Den Status setzt ausschließlich der Orchestrator.
