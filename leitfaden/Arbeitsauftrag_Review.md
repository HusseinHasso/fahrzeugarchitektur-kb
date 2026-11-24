# Arbeitsauftrag Review (Vorlage, Leitfaden 2.4)

Ein Aufruf prüft genau einen Artikel mit Status `zu_pruefen`. Der Orchestrator füllt die Platzhalter in `{}` und gibt mit: diese Vorlage, den Artikel, `Arbeitsauftrag_Artikel.md`, `Referenzartikel_Lkw.md`, `artikel.schema.json`, die Ausgabe von `kb_tool.py glossar <dir> --gruppe {gruppe}` und den Inventareintrag; bei Übersichten zusätzlich die Kindartikel. Modell: `claude-opus-5-5` mit Extended Thinking und Quellenzugriff (Leitfaden, Abschnitt 1). Der Aufruf wird mit `aufruftyp: review` in `aenderungen.json` protokolliert.

Die formalen Regeln prüft bereits `kb_tool.py validate`. Melde keine Befunde, die das Werkzeug abdeckt (Schema, Verweise, Wortzahlen, Glossarnamen, Kategorien, Abschnittsfolge), außer du findest dort einen Fehler, den das Werkzeug übersehen hat.

---

Prüfe den Artikel **{artikel_id} {bezeichnung}** ({artikeltyp}) nach Leitfaden 2.4, Abschnitt 6. Ändere den Artikel nicht. Gib ausschließlich ein JSON-Objekt in der unten beschriebenen Form aus. Schreibe auf Deutsch.

**Zweck des Artikels.** Er soll beim Modellieren der Fahrzeugart anleiten und beim Verfeinern von Architektur und Anforderungen Vorschläge und konkrete Fragen liefern. Miss jeden Befund daran, ob er diesen Zweck beeinträchtigt.

**Prüfschritte**

1. **Belege (Stichprobe).** Wähle mindestens drei belegte Absätze, bevorzugt solche mit Zahlen, Normen oder Abgrenzungen, und alle Einträge unter `regelwerke`. Rufe die Quelle ab und prüfe, ob jede Aussage in der angegebenen Fundstelle steht. Prüfe auch, ob der `quellentyp` zutrifft. Ist eine Quelle nicht abrufbar, vermerke das als Befund der Schwere `mittel`.
2. **Herleitungen.** Prüfe jeden hergeleiteten Absatz: Tragen die Prämissen den Schluss? Ist die Reichweite richtig angegeben (Regel 8)? Passt die `sicherheit` zu Regel 5? Ist eine Aussage nur von einer anderen Fahrzeugart übertragen, muss sie `gering` sein.
3. **Fachliche Richtigkeit und Vollständigkeit.** Fehlt ein Hauptsystem, eine wesentliche Komponente oder eine strukturändernde Variante, die für diese Fahrzeugart üblich ist? Ist etwas falsch zugeordnet? Ist eine entfallene Kategorie zu Unrecht entfallen?
4. **Brauchbarkeit für den Zweck.**
   - Varianten: Sind es echte Architekturentscheidungen? Stimmen die Auswirkungen auf andere Hauptsysteme? Fehlt eine naheliegende Variante?
   - Klärungsfragen: Sind sie konkret, beantwortbar und beim Verfeinern wirklich nötig? Doppeln sie sich? Fehlt eine Frage, die ein erfahrener Systemarchitekt zuerst stellen würde?
   - Anforderungsthemen: Fehlen naheliegende Themen oder Kenngrößen?
5. **Übersichten zusätzlich.** Geben die gemeinsame Architektur und die Unterscheidungsmerkmale die Kindartikel zutreffend wieder? Widerspricht die Übersicht einem Kindartikel? Hilft die Frage zur Wahl der Fahrzeugart wirklich bei der Auswahl?

**Schwere**

- `hoch`: falsche Aussage, nicht gedeckter Beleg, unzutreffende Herleitung mit Sicherheit `hoch` oder `mittel`, fehlendes Hauptsystem oder fehlende wesentliche Variante, irreführende Klärungsfrage. Führt zu einer Revision.
- `mittel`: ungenaue Reichweite, zu hohe Sicherheit, fehlende Komponente, schwache oder doppelte Klärungsfrage, fehlendes Anforderungsthema, nicht abrufbare Quelle.
- `gering`: Formulierung, Verständlichkeit, kleinere Ergänzungen.

**Ausgabe**

```json
{
  "artikel_id": "{artikel_id}",
  "leitfaden_version": "2.4",
  "geprueft_am": "JJJJ-MM-TT",
  "stichprobe": [
    {"absatz_id": "P3", "quellen_id": "Q2", "ergebnis": "bestaetigt|nicht_gedeckt|nicht_abrufbar", "anmerkung": "…"}
  ],
  "befunde": [
    {"ref": "P5|E12|V2|K4|R3|Q1", "schwere": "hoch|mittel|gering", "pruefschritt": 1,
     "befund": "Was ist falsch oder fehlt?", "vorschlag": "Konkrete Änderung für die Revision."}
  ],
  "gesamturteil": "Ein bis drei Sätze zur Qualität und Brauchbarkeit."
}
```

- Jeder Befund verweist auf genau ein vorhandenes Element des Artikels in `ref`. Für etwas Fehlendes nennst du das Element, an dem es ergänzt werden soll.
- `vorschlag` ist so konkret, dass der Revisionsaufruf ihn ohne Rückfrage umsetzen kann.
- Ohne Befunde ist `befunde` eine leere Liste.

**Revision.** Bei mindestens einem Befund `hoch` gibt der Orchestrator den Artikel mit allen Befunden `hoch` und `mittel` an einen Revisionsaufruf (`aufruftyp: revision`, Arbeitsauftrag_Artikel.md, Abschnitt Korrekturrunden sinngemäß: nur die Befunde umsetzen). Danach folgen Validierung und, falls nötig, Korrekturrunden. Ein zweites Review gibt es nur, wenn die Revision Absätze mit neuen Belegen hinzufügt.
