# Fahrzeugarchitektur-Wissensbasis

Generische Referenzarchitekturen für 191 Fahrzeugarten (124 Blattartikel, 67 Übersichten), je Artikel als
Fließtext mit Modellblock (Elemente, Funktionen, Flüsse) nach Schema 2.2.

- `leitfaden/`: Leitfaden 2.3 (Rekonstruktion), Arbeitsauftrag, Referenzartikel Lkw, Schema, Recherchegliederung
- `kb/`: Manifest, Inventar, Glossarvorgaben, Änderungs- und Laufprotokoll, `artikel/`
- `tools/kb_tool.py`: Werkzeug für den Orchestrator (Nachbau)
- `probelaeufe/probelauf2/`: Probelauf 2 vom 2026-11-24 (Pkw und ROV mit Sonnet und Opus), unverändert

```bash
python3 tools/kb_tool.py plan kb
python3 tools/kb_tool.py glossar kb --gruppe Landfahrzeuge
python3 tools/kb_tool.py validate kb --nur A-0001
```

`validate` braucht das Python-Paket `jsonschema`.
