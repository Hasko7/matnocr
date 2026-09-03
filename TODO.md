# TODO – MatnOCR

> Projektname, Paketname und CLI-Befehl: `MatnOCR` / `matnocr`.

## Phase 0 – Entscheidungen vor dem eigentlichen Projektaufbau

### 1. Projektname festlegen

- [x] Namensideen sammeln
- [x] kurze und gut merkbare Namen bevorzugen
- [x] prüfen, ob der Name als CLI-Befehl gut funktioniert
- [x] PyPI auf Namenskollision prüfen
- [x] GitHub auf Namenskollision prüfen
- [x] winget auf Namenskollision prüfen
- [x] npm auf Namenskollision prüfen
- [x] Cargo auf Namenskollision prüfen
- [x] Suchmaschinenprüfung durchführen
- [x] endgültigen Paketnamen festlegen: `matnocr`
- [x] endgültigen CLI-Befehl festlegen: `matnocr`
- [x] endgültigen GitHub-Repository-Namen festlegen: `matnocr`

Entscheidung:

```text
Brand:       MatnOCR
PyPI:        matnocr
CLI:         matnocr
Python pkg:  matnocr
GitHub repo: matnocr
Executable:  matnocr.exe
```

### 2. PDF-Renderer vergleichen: PyMuPDF vs. pypdfium2

- [x] `pypdfium2` Testprojekt erstellen
- [x] PDF-Seiten direkt in RAM rendern
- [x] PDFium-Buffer direkt in `SoftwareBitmap` überführen
- [x] dieselben sechs Benchmark-Seiten verwenden
- [x] 200 DPI testen
- [x] 250 DPI testen
- [x] 300 DPI testen
- [x] Rendering-Zeit vergleichen
- [x] Bitmap-Konvertierung vergleichen
- [x] OCR-Zeit vergleichen
- [x] Gesamtzeit vergleichen
- [ ] Speicherverbrauch vergleichen *(nicht blockierend für v0.1)*
- [x] OCR-Ausgaben vergleichen
- [ ] Installation / Wheel-Größe vergleichen *(Wheel-Größe noch messen; nicht blockierend)*
- [x] Lizenzfolgen dokumentieren
- [x] endgültigen Renderer auswählen: `pypdfium2`

Entscheidung:

```text
pypdfium2 + permissive Projektlizenz
```

Begründung:

- direkter Originalscan-Fast-Path für gescannte PDFs
- OCR-Qualität bei 200 / 250 / 300 DPI praktisch auf PyMuPDF-Niveau
- keine temporären PNG-Dateien und kein Pillow nötig
- Direct-RAM-Pipeline bleibt erhalten
- normaler PDFium-Renderpfad bleibt als Fallback
- permissivere Lizenzsituation als bei PyMuPDF/AGPL

### 3. Lizenz festlegen

- [x] Renderer-Entscheidung abwarten
- [x] Kernabhängigkeiten und deren Lizenzen prüfen
- [x] zwischen AGPL / MIT / Apache-2.0 entscheiden
- [x] Projektlizenz festlegen: `Apache-2.0`
- [x] `LICENSE` erstellen
- [x] Drittanbieter-Lizenzpflichten dokumentieren (`THIRD_PARTY_NOTICES.md`)
- [x] Lizenz im `pyproject.toml` eintragen
- [ ] Lizenzhinweise in README ergänzen *(sobald README angelegt wird)*
- [ ] bei Windows-Binärreleases PDFium- und Third-Party-Lizenzdateien mit ausliefern

Lizenzentscheidung:

```text
MatnOCR: Apache-2.0
```

Wichtige Abhängigkeiten:

```text
pypdfium2 / PDFium    permissiv (Apache-2.0 / BSD-3-Clause bzw. BSD-style + Third-Party-Lizenzen)
PyWinRT                MIT
Typer                  MIT
Rich                   MIT
Ruff                   MIT
ty                     MIT
pytest                 MIT
```

Für `pyproject.toml` später verwenden:

```toml
[project]
license = "Apache-2.0"
license-files = ["LICENSE"]
```

## Phase 1 – Projekt sauber aufsetzen

### 4. Neues Git-Projekt erstellen

- [x] bestehenden Projektordner mit endgültigem Namen verwenden
- [x] `git init`
- [x] `.gitignore` für Python / uv / VS Code / Build-Artefakte erstellen
- [x] initiale Branch-Strategie festlegen (`main`)
- [x] ersten Commit erstellen

### 5. uv-Projekt initialisieren

- [x] `uv init --app`
- [x] Python-Minimum festlegen, zunächst `>=3.11`
- [x] `src/`-Layout verwenden
- [x] `uv.lock` erzeugen
- [x] `uv_build` als Build-Backend prüfen / konfigurieren
- [x] Runtime Dependencies eintragen
- [x] Dev Dependencies eintragen

### 6. Geplante Paketstruktur anlegen

- [x] `src/matnocr/__init__.py`
- [x] `src/matnocr/__main__.py`
- [x] `src/matnocr/cli.py`
- [x] `src/matnocr/engine.py`
- [x] `src/matnocr/renderer.py`
- [x] `src/matnocr/languages.py`
- [x] `src/matnocr/pages.py`
- [x] `src/matnocr/rtl.py`
- [x] `src/matnocr/output.py`
- [x] `src/matnocr/config.py`
- [x] `src/matnocr/ui.py`

### 7. Aktuellen OCR-Prototyp modularisieren

- [x] Windows-OCR-Code aus dem Testskript extrahieren
- [x] Engine-Erstellung in eigenes Modul verschieben
- [x] Direct-RAM-Pipeline übernehmen
- [x] PDF-Renderer abstrahieren
- [x] RTL-Rekonstruktion in eigenes Modul verschieben
- [x] Language Resolution auslagern
- [x] Output-Erzeugung auslagern
- [x] Timing-Code optional / strukturiert machen
- [x] keine globalen Projektvariablen mehr verwenden

## Phase 2 – CLI v0.1 bauen

### 8. Typer + Rich integrieren

- [x] Typer hinzufügen
- [x] Rich hinzufügen
- [x] Haupt-App erstellen
- [ ] schöne `--help`-Ausgabe gestalten
- [ ] Farb- und Panel-Design festlegen
- [ ] einheitliche Fehlermeldungen definieren
- [ ] Terminal ohne ANSI / CI berücksichtigen

### 9. Console Entry Point einrichten

- [x] `[project.scripts]` konfigurieren
- [x] `matnocr = "matnocr.cli:app"`
- [x] lokale Installation testen
- [x] prüfen, dass `matnocr --help` funktioniert
- [x] `python -m matnocr` ebenfalls unterstützen

### 10. Basisargumente implementieren

- [x] PDF als positional Argument
- [x] `--lang`
- [x] `--dpi`
- [x] `--quality`
- [x] `-o / --output`
- [x] `--quiet`
- [x] `--version`

### 11. DPI-Presets implementieren

- [x] `fast -> 200`
- [x] `balanced -> 250`
- [x] `quality -> 300`
- [x] Konflikt zwischen `--quality` und `--dpi` sauber behandeln
- [x] Standardmodus festlegen: `quality` / 300 DPI

### 12. Page-Range-Parser implementieren

Unterstützen:

```text
30-50
1,5,20-35,100
```

- [x] einzelne Seiten
- [x] Bereiche
- [x] Kombinationen
- [x] Duplikate entfernen
- [x] Reihenfolge definieren: aufsteigend nach PDF-Seite
- [x] ungültige Seiten erkennen
- [x] Seiten außerhalb der PDF erkennen
- [x] gute Fehlermeldungen schreiben
- [x] Seitenanzahl einer PDF mit `--page-count` ausgeben

### 13. `languages` Command

- [x] installierte Windows-OCR-Sprachen dynamisch auslesen
- [x] Sprachcode anzeigen
- [x] lesbaren Namen anzeigen
- [x] aktive / verfügbare Sprachen als Rich-Tabelle darstellen
- [x] fehlende Sprache bei OCR-Aufruf verständlich melden
- [x] persistente Standardsprache mit `languages default <code>` setzen
- [x] Sprachpaketverwaltung bewusst Windows / PowerShell überlassen

### 14. `doctor` Command

Prüfen:

- [x] unterstütztes Windows
- [x] Windows.Media.Ocr verfügbar
- [x] installierte OCR-Sprachen
- [x] PDF-Renderer verfügbar
- [x] Direct-RAM-Konvertierung funktioniert
- [x] max. Bilddimension auslesen
- [x] Python-Version anzeigen
- [x] Paketversion anzeigen
- [x] Diagnose klar mit ✓ / ✗ darstellen

### 15. Progress UI

- [ ] Rich Progress Bar
- [ ] aktuelle Seite
- [ ] Seitenanzahl
- [ ] Geschwindigkeit / pages per second
- [ ] elapsed time
- [ ] optional ETA
- [ ] nach Abschluss Zusammenfassung
- [ ] `--quiet` ohne Animation unterstützen

Beispielziel:

```text
OCR  ████████████████████████████████  71/71

71 pages · 23.4s · 3.03 pages/s

✓ Saved to output.txt
```

### 16. Output v0.1

- [x] TXT als Standard
- [x] Seitenmarker beibehalten
- [x] UTF-8 schreiben
- [x] automatischen Dateinamen erzeugen
- [ ] existierende Dateien nicht versehentlich überschreiben
- [ ] Verhalten für `--output` definieren
- [ ] Fehler bei nicht beschreibbaren Pfaden sauber behandeln

## Phase 3 – Qualität und Tests

### 17. Ruff einrichten

- [ ] Ruff als Dev Dependency
- [ ] `ruff check`
- [ ] `ruff format`
- [ ] sinnvolle Regeln in `pyproject.toml`
- [ ] lokale Formatierung dokumentieren

### 18. Type Checking

- [ ] `ty` als Dev Dependency testen
- [ ] `ty check` konfigurieren
- [ ] PyWinRT-Typing-Probleme prüfen
- [ ] nötige Ausnahmen dokumentieren

### 19. pytest einrichten

- [x] Unit-Test-Struktur erstellen
- [ ] Integration-Test-Struktur erstellen
- [ ] pytest konfigurieren

### 20. Unit Tests

- [x] Page-Range-Parser
- [x] Language Resolution
- [x] RTL-Sortierung
- [x] Dateinamengenerierung
- [x] Quality-Presets
- [x] Output Formatting
- [x] CLI Validation
- [x] Konfiguration

### 21. Integration Tests

- [ ] PDF-Renderer
- [ ] Direct-RAM-Pipeline
- [ ] SoftwareBitmap-Erstellung
- [ ] Windows OCR
- [ ] reale OCR auf kleinem Testdokument
- [ ] Test überspringen, wenn notwendige OCR-Sprache fehlt
- [ ] Testdaten lizenzrechtlich sauber halten

### 22. Eigene Test-PDFs erstellen

- [ ] synthetische englische PDF
- [ ] synthetische deutsche PDF
- [ ] synthetische arabische PDF
- [ ] Public-Domain-Testtext möglich
- [ ] keine urheberrechtlich problematischen Buchseiten committen

## Phase 4 – Dokumentation und Open Source

### 23. README schreiben

README soll mindestens enthalten:

- [ ] Projektbeschreibung
- [ ] Screenshot / CLI-Beispiel
- [ ] Features
- [ ] Installation
- [ ] Quick Start
- [ ] Sprachen
- [ ] Windows-OCR-Sprachpakete
- [ ] Page Ranges
- [ ] DPI / Quality Modes
- [ ] Benchmarks
- [ ] Limitations
- [ ] Lizenz
- [ ] Contributing

### 24. Open-Source-Dateien

- [ ] `LICENSE`
- [ ] `CONTRIBUTING.md`
- [ ] `CHANGELOG.md`
- [ ] `SECURITY.md`
- [ ] `CODE_OF_CONDUCT.md`
- [ ] `PROJECT.md`
- [ ] `TODO.md`

### 25. GitHub Templates

- [ ] Bug Report Template
- [ ] Feature Request Template
- [ ] Pull Request Template
- [ ] eventuell OCR Quality Report Template

OCR Quality Report könnte abfragen:

```text
language
Windows version
DPI
PDF type
page sample
expected text
actual OCR
```

## Phase 5 – GitHub Repository

### 26. GitHub Repository erstellen

- [ ] Public Repository erstellen
- [ ] Beschreibung setzen
- [ ] Topics hinzufügen
- [ ] Lizenz anzeigen lassen
- [ ] Default Branch `main`
- [ ] lokalen Git-Remote setzen
- [ ] ersten Commit pushen

Mögliche Topics:

```text
ocr
windows
pdf
arabic
cli
python
winrt
pdf-ocr
offline-ocr
```

### 27. Branch Protection später aktivieren

- [ ] Pull Requests vor Merge
- [ ] CI muss erfolgreich sein
- [ ] versehentliches Force Push verhindern
- [ ] Tags / Releases schützen

## Phase 6 – GitHub CI

### 28. GitHub Actions CI erstellen

Workflow:

```text
push
pull_request
```

Schritte:

- [ ] Checkout
- [ ] uv installieren
- [ ] Python installieren
- [ ] `uv sync --locked`
- [ ] `ruff check`
- [ ] `ruff format --check`
- [ ] `ty check`
- [ ] `pytest`
- [ ] Package bauen
- [ ] gebauten Wheel installieren
- [ ] CLI Smoke Test

### 29. Windows Runner

- [ ] Windows GitHub Runner verwenden
- [ ] genaue Runner-Version festlegen
- [ ] verfügbare Windows-OCR-Sprachen untersuchen
- [ ] falls sinnvoll kleine Integrationstests aktivieren
- [ ] OCR-Sprachabhängige Tests sauber skippen

### 30. Python CI Matrix

Prüfen:

- [ ] Python 3.11
- [ ] Python 3.12
- [ ] Python 3.13
- [ ] Python 3.14

Nur nach erfolgreichem Test offiziell unterstützen.

### 31. Security Automation

- [ ] Dependabot
- [ ] CodeQL
- [ ] minimale GitHub-Action-Berechtigungen
- [ ] Actions möglichst auf stabile Versionen / SHAs pinnen

## Phase 7 – Python Packaging / PyPI

### 32. `pyproject.toml` finalisieren

- [ ] Package Metadata
- [ ] Name
- [ ] Version
- [ ] Description
- [ ] Readme
- [ ] License
- [ ] Authors
- [ ] Python-Version
- [ ] Dependencies
- [ ] Optional Dev Dependencies
- [ ] Project URLs
- [ ] CLI Entry Point
- [ ] Classifiers

### 33. Build lokal testen

- [ ] `uv build`
- [ ] sdist prüfen
- [ ] wheel prüfen
- [ ] frische virtuelle Umgebung erstellen
- [ ] wheel dort installieren
- [ ] CLI vollständig testen

### 34. TestPyPI

- [ ] TestPyPI-Account / Projekt vorbereiten
- [ ] ersten Testrelease hochladen
- [ ] Installation von TestPyPI testen

### 35. PyPI Trusted Publishing

- [ ] PyPI-Projekt anlegen
- [ ] GitHub Trusted Publisher konfigurieren
- [ ] OIDC statt langfristigem API Token verwenden
- [ ] separaten Release-Workflow erstellen

### 36. PyPI Installation testen

Später:

```powershell
uv tool install matnocr
```

und:

```powershell
pipx install matnocr
```

- [ ] `uv tool`
- [ ] pipx
- [ ] pip

## Phase 8 – GitHub Releases / Windows Distribution

### 37. PyInstaller evaluieren

- [ ] `onedir` bauen
- [ ] `onefile` bauen
- [ ] Startup-Zeit vergleichen
- [ ] Dateigröße vergleichen
- [ ] WinRT-Kompatibilität prüfen
- [ ] PDF-Renderer-Binaries prüfen
- [ ] frischen Windows-PC / VM testen

### 38. GitHub Release Assets

Geplant:

```text
matnocr-windows-x64.zip
matnocr-windows-x64.exe
Python wheel
sdist
SHA256SUMS.txt
```

- [ ] Release Notes generieren
- [ ] Checksums erstellen
- [ ] Artefakte automatisch hochladen

### 39. Release Workflow

Trigger:

```text
git tag v0.1.0
```

Pipeline:

```text
test
→ build Python package
→ build Windows executable
→ publish PyPI
→ create GitHub Release
```

- [ ] Versionen müssen überall identisch sein
- [ ] Release nur aus getaggtem Commit
- [ ] fehlerhafte Builds dürfen nicht veröffentlicht werden

## Phase 9 – v0.1.0 Release

### 40. Feature Freeze

v0.1 soll enthalten:

- [ ] PDF OCR
- [ ] Direct RAM
- [ ] Windows OCR
- [ ] dynamische Sprachen
- [ ] RTL
- [ ] `--lang`
- [ ] `--pages`
- [ ] `--dpi`
- [ ] `--quality`
- [ ] `--output`
- [ ] `--quiet`
- [ ] `--version`
- [ ] `languages`
- [ ] `doctor`
- [ ] TXT
- [ ] Rich UI
- [ ] Tests
- [ ] GitHub CI
- [ ] PyPI
- [ ] GitHub Release

### 41. v0.1 Benchmark dokumentieren

- [ ] 200 DPI
- [ ] 250 DPI
- [ ] 300 DPI
- [ ] mehrere PDF-Typen
- [ ] mehrere Sprachen
- [ ] Hardware dokumentieren
- [ ] Seiten/s dokumentieren

## Version 0.2 – geplante Erweiterungen

### 42. Zusätzliche Ausgabeformate

- [ ] Markdown
- [ ] JSON
- [ ] JSONL
- [ ] Bounding Boxes exportieren

### 43. Batch OCR

- [ ] ganze Ordner
- [ ] mehrere PDFs
- [ ] Output-Verzeichnis
- [ ] Fehler eines Dokuments sollen Batch nicht komplett stoppen

### 44. Resume / Checkpointing

- [ ] Verarbeitung großer Bücher fortsetzen
- [ ] bereits fertige Seiten erkennen
- [ ] temporäre Job-Metadaten

### 45. Benchmark Command

Beispiel:

```powershell
matnocr benchmark book.pdf
```

- [ ] Renderzeit
- [ ] Bitmapzeit
- [ ] OCR-Zeit
- [ ] Seiten/s
- [ ] JSON Benchmark Output

### 46. Verbesserte Nachbearbeitung

Optional:

- [ ] `--clean`
- [ ] `--normalize-arabic`
- [ ] BiDi-Steuerzeichen
- [ ] Unicode Normalization
- [ ] ﷺ-Normalisierung
- [ ] offensichtliche Artefakte

Wichtig:

- [ ] Raw OCR muss weiterhin verfügbar bleiben

### 47. Alternative OCR Engine

- [ ] Tesseract Fast als optionalen Backend-Prototyp testen
- [ ] Windows OCR vs. Tesseract vergleichen
- [ ] optionales Fallback untersuchen
- [ ] Ensemble nur bauen, wenn messbar bessere Qualität

### 48. Strukturierte Buch-OCR

Langfristig prüfen:

- [ ] Überschriftenerkennung
- [ ] Fußnoten
- [ ] Seitenzahlen
- [ ] Absatzrekonstruktion
- [ ] Spalten
- [ ] Tabellen
- [ ] Markdown-Ausgabe

## Version 0.3+ / langfristige Ideen

### 49. Native Windows Installer

- [ ] winget Package
- [ ] möglicher MSI / Installer
- [ ] automatische PATH-Einrichtung
- [ ] OCR-Sprachpaket-Hilfe

### 50. ARM64

- [ ] Windows ARM64 testen
- [ ] PyWinRT Wheels prüfen
- [ ] PDF-Renderer prüfen
- [ ] eigenes Release Asset bauen

### 51. Performance-Experimente

Nur nach Profiling:

- [ ] Parallel Rendering
- [ ] Pipeline-Prefetch
- [ ] mehrere OCR Engines
- [ ] Speicherpool
- [ ] Batch Bitmap Conversion

Keine Optimierung ohne vorherige Messung.

### 52. Optionale GUI

Nur langfristig und getrennt von der CLI:

- [ ] GUI-Konzept prüfen
- [ ] CLI bleibt Kern
- [ ] GUI soll dieselbe OCR-Library verwenden

## Grundprinzipien

Bei allen zukünftigen Entscheidungen gelten:

```text
1. Geschwindigkeit messen, nicht vermuten.
2. Raw OCR nicht still verändern.
3. CLI einfach halten.
4. Windows-native OCR als Kern beibehalten.
5. Arabisch als Haupt-Use-Case ernst nehmen.
6. Andere Windows-OCR-Sprachen vollständig unterstützen.
7. Releases reproduzierbar bauen.
8. Open-Source-Lizenz sauber behandeln.
9. Große Bücher müssen zuverlässig funktionieren.
10. Keine unnötige Komplexität in v0.1.
```
