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
- [x] Lizenzhinweise in README ergänzen
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

In `pyproject.toml` konfiguriert:

```toml
[project]
license = "Apache-2.0"
license-files = ["LICENSE", "THIRD_PARTY_NOTICES.md"]
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
- [x] verdächtige Nicht-Text-Seiten mit einer kontrollierten 125-DPI-OCR prüfen und OCR-Artefakte verwerfen

## Phase 2 – CLI v0.1 bauen

### 8. Typer + Rich integrieren

- [x] Typer hinzufügen
- [x] Rich hinzufügen
- [x] Haupt-App erstellen
- [x] schöne `--help`-Ausgabe gestalten
- [x] Farb- und Panel-Design festlegen
- [x] einheitliche Fehlermeldungen definieren
- [x] Terminal ohne ANSI / CI berücksichtigen

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
- [x] Sprachpaketverwaltung über administrative Windows PowerShell integrieren
- [x] Sprachen mit `languages install <code>` installieren und mit `languages remove <code>` entfernen
- [x] alle verfügbaren Windows-OCR-Capabilities mit `languages available` dynamisch anzeigen
- [x] administrative PowerShell über Windows UAC öffnen, wenn MatnOCR nicht erhöht läuft
- [x] aktuell gewählte Standardsprache bei `matnocr languages` direkt anzeigen
- [x] Standardsprache im Haupt-Hilfetext von `matnocr` direkt anzeigen

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

- [x] Rich Progress Bar
- [x] aktuelle Seite
- [x] Seitenanzahl
- [x] Geschwindigkeit / pages per second
- [x] elapsed time
- [x] ETA
- [x] nach Abschluss Zusammenfassung
- [x] `--quiet` ohne Animation unterstützen

Beispielziel:

```text
OCR  ████████████████████████████████  71/71

71 pages · 23.4s · 3.03 pages/s

✓ Saved to output.txt
```

### 16. Output v0.1

- [x] TXT als anfänglichen Standard beibehalten
- [x] einfaches Markdown mit `# Page <PDF-Seitennummer>` aus v0.2 vorziehen
- [x] Standardausgabe mit `output default txt|md` speichern und mit `output` anzeigen
- [x] verfügbare Ausgabeformate und Beispiele bei `output` und `output --help` anzeigen
- [x] einmalige Formatwahl mit `--format txt|md`
- [x] Format anhand von `-o`-Endung wählen (`.txt`, `.md`, `.markdown`)
- [x] Endungslosen Zielen gewählte Formatendung ergänzen; ungültige und widersprüchliche Endungen vor OCR ablehnen
- [x] Format- und Spracheinstellungen beim Speichern gegenseitig erhalten
- [x] Seitenmarker beibehalten
- [x] UTF-8 schreiben
- [x] automatischen Dateinamen erzeugen
- [x] OCR-Zeilenumbrüche aus `OcrLine` standardmäßig beibehalten
- [x] Absatzerkennung über Bounding-Boxes als Standardmodus
- [x] Layout mit `--no-layout` abschalten und Text fortlaufend verbinden
- [x] Layoutmodus ohne zweite OCR-Runde und ohne temporäre Rasterdateien
- [x] existierende Dateien nicht versehentlich überschreiben
- [x] Verhalten für `--output` und Formatwahl definieren (mit `--force` als explizitem Überschreibschutz)
- [x] Fehler bei nicht beschreibbaren Pfaden sauber behandeln

## Phase 3 – Qualität und Tests

### 17. Ruff einrichten

- [x] Ruff als Dev Dependency
- [x] `ruff check`
- [x] `ruff format`
- [x] sinnvolle Regeln in `pyproject.toml`
- [x] lokale Formatierung dokumentieren (`README.md`)

### 18. Type Checking

- [x] `ty` als Dev Dependency eintragen
- [x] `ty` im Projekt vollständig testen
- [x] `ty check` konfigurieren
- [x] PyWinRT-Typing-Probleme prüfen
- [x] nötige Ausnahmen dokumentieren

### 19. pytest einrichten

- [x] pytest und pytest-cov als Dev Dependencies eintragen
- [x] Unit-Test-Struktur erstellen
- [x] Integration-Test-Struktur erstellen
- [x] pytest konfigurieren

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

- [x] PDF-Renderer
- [x] Direct-RAM-Pipeline
- [x] SoftwareBitmap-Erstellung
- [x] Windows OCR
- [x] reale OCR auf kleinem Testdokument
- [x] Test überspringen, wenn notwendige OCR-Sprache fehlt
- [x] Testdaten lizenzrechtlich sauber halten

### 22. Eigene Test-PDFs erstellen

- [x] synthetische englische PDF (zur Testlaufzeit erzeugt)
- [x] synthetische deutsche Scan-PDF mit Umlauten und ß (zur Testlaufzeit erzeugt)
- [x] synthetische arabische Scan-PDF mit verbundenen Buchstaben und RTL-Prüfung (zur Testlaufzeit erzeugt)

Die Testtexte sind selbst verfasst. Gemeinfreie Texte bleiben eine optionale
Alternative, keine zusätzliche Pflichtaufgabe.

Dauerhafte Regel: Keine urheberrechtlich problematischen Buchseiten oder
privaten Benchmark-Dateien committen. Systemschriften werden nur lokal zum
Rendern verwendet; Schriftdateien werden nicht mitgeliefert.

## Phase 4 – Dokumentation und Open Source

### 23. README schreiben

README enthält:

- [x] Projektbeschreibung
- [x] Screenshot / CLI-Beispiel
- [x] README für neue Nutzer strukturieren und Detaildokumentation nach `docs/` auslagern
- [x] Screenshot-Pfade und Anleitung unter `docs/images/` vorbereiten
- [x] echten Terminal-Screenshot als `docs/images/terminal.png` ergänzen (Nutzer)
- [x] arabische Buchseite als `docs/images/book_page.png` mit unverändertem OCR-Beispiel ergänzen (Nutzer)
- [x] Features
- [x] Installation
- [x] kurze GitHub-Installationsanleitung mit Voraussetzungen, lokalem Klonen und geprüftem Python-Status ergänzen
- [x] Quick Start
- [x] Sprachen
- [x] Windows-OCR-Sprachpakete
- [x] Page Ranges
- [x] DPI / Quality Modes
- [x] Benchmarks
- [x] Limitations
- [x] Lizenz
- [x] Contributing

### 24. Open-Source-Dateien

- [x] `LICENSE`
- [x] `CONTRIBUTING.md`
- [x] `CHANGELOG.md`
- [x] `SECURITY.md`
- [x] `CODE_OF_CONDUCT.md`
- [x] `PROJECT.md`
- [x] `TODO.md`

### 25. GitHub Templates

- [x] Bug Report Template
- [x] Feature Request Template
- [x] Pull Request Template
- [x] OCR Quality Report Template

OCR Quality Report fragt unter anderem ab:

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

- [x] Public Repository erstellen
- [x] Beschreibung setzen
- [x] Topics hinzufügen
- [x] Lizenz anzeigen lassen
- [x] Default Branch `main`
- [x] lokalen Git-Remote setzen
- [x] ersten Commit pushen
- [x] Issue-Formulare auf GitHub prüfen
- [x] PR-Vorlage beim ersten echten Pull Request auf GitHub prüfen (PR #1)
- [x] privates Vulnerability Reporting aktivieren und den Meldeweg in `SECURITY.md` prüfen
- [x] Moderationsmeldeweg in `CODE_OF_CONDUCT.md` festlegen: GitHub-Meldetools, bewusst keine öffentliche E-Mail-Adresse und kein direkter privater Projektkontakt

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

### 27. Branch- und Release-Schutz aktivieren

- [x] Pull Requests vor Merge
- [x] CI muss erfolgreich sein (Check `CI` von GitHub Actions verpflichtend; Branch muss aktuell sein)
- [x] versehentliches Force Push verhindern
- [x] Tags / Releases schützen
- [x] aktives Tag-Ruleset `Protect version tags` für `v*`: Änderungen und Löschungen gesperrt, keine Bypass-Ausnahmen
- [x] Release Immutability für zukünftige GitHub Releases aktivieren

Neue Versions-Tags können weiterhin erstellt werden. Für Releases zuerst einen
Entwurf mit allen Assets vorbereiten und erst anschließend veröffentlichen.
Veröffentlichte Assets sind dann unveränderlich; Korrekturen erhalten eine neue
Version. Einrichtung und Ablauf stehen in `docs/releases.md`.

## Phase 6 – GitHub CI

### 28. GitHub Actions CI erstellen

Workflow:

```text
push
pull_request
```

Schritte:

- [x] Checkout
- [x] uv installieren
- [x] Python installieren
- [x] `uv sync --locked`
- [x] `ruff check`
- [x] `ruff format --check`
- [x] `ty check`
- [x] `pytest`
- [x] Package bauen
- [x] gebauten Wheel installieren
- [x] CLI Smoke Test

Der Workflow ist implementiert und auf GitHub für Python 3.11–3.14 erfolgreich
geprüft. Der [erfolgreiche Lauf auf main](https://github.com/Hasko7/matnocr/actions/runs/45465791622)
prüft alle vier Versionen einschließlich Build, frischer Wheel-Installation und
CLI-Smoke-Tests. CLI-Tests erzeugen eigene Eingabepfade; erzwungene
Terminalformatierung ist im Workflow deaktiviert.

- [x] ersten erfolgreichen GitHub-Lauf auf dem PR und auf main prüfen (Matrix und echte Runner-Capabilities)

### 29. Windows Runner

- [x] Windows GitHub Runner konfigurieren (`windows-2025`; Hosted-Lauf erfolgreich)
- [x] Runner-Image-Familie festlegen (`windows-2025`; konkrete Image-Version im Actions-Log)
- [x] verfügbare Windows-OCR-Sprachen im ersten GitHub-Lauf untersuchen: `en-US`; Deutsch und Arabisch fehlen
- [x] kleine Integrationstests im Workflow aktivieren
- [x] OCR-Sprachabhängige Tests bei fehlender Runtime oder Sprache sauber skippen

### 30. Python CI Matrix

Matrix 3.11–3.14 ist auf GitHub erfolgreich geprüft:

- [x] Python 3.11
- [x] Python 3.12
- [x] Python 3.13
- [x] Python 3.14

Im Hosted-Lauf bestehen pro Version 142 Tests; zwei OCR-Integrationstests werden
wegen fehlender deutscher und arabischer Sprachpakete übersprungen. Lokal unter
Python 3.13 bestehen mit diesen Sprachpaketen alle 144 Tests. Die Hosted-Matrix
belegt damit keine reale deutsche oder arabische OCR auf allen Python-Versionen.

### 31. Security Automation

- [ ] Dependabot
- [ ] CodeQL
- [x] minimale GitHub-Action-Berechtigungen (`contents: read` im CI-Workflow)
- [x] CI-Actions auf geprüfte Commit-SHAs und uv auf Version pinnen

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

- [x] `uv build`
- [x] sdist prüfen
- [x] wheel prüfen
- [x] frische virtuelle Umgebung erstellen
- [x] wheel dort installieren
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
- [ ] alle Release-Assets einschließlich Checksums zuerst an einen Entwurf anhängen und erst danach unveränderlich veröffentlichen

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

- [x] einfaches Markdown nach v0.1 vorgezogen (Seitenüberschriften und gespeicherter Standard)
- [ ] PDF-Export nach der ersten öffentlichen Veröffentlichung ergänzen (Ziel v0.2)
- [ ] Text-PDF: neues PDF mit sichtbarem OCR-Text, Arabisch-/RTL-Darstellung, Schriften und Seitenumbrüchen
- [ ] Durchsuchbare Scan-PDF: Originalseiten mit unsichtbarer OCR-Textebene zum Suchen und Kopieren
- [ ] PDF-Backend und Abhängigkeiten einschließlich Lizenz- und Distribution-Folgen prüfen
- [ ] PDF-Export für beide Varianten mit arabischem Text und Such-/Kopierverhalten testen
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
