# AGENTS.md

## Zweck dieser Datei

Diese Datei enthält verbindliche Arbeitsregeln für KI-Agenten, Coding-Assistenten und automatisierte Entwicklungswerkzeuge, die an diesem Repository arbeiten.

Das Projekt ist eine schnelle, lokale und Windows-native PDF-OCR-CLI mit besonderem Fokus auf arabische Bücher und RTL-Sprachen.

Bevor Änderungen vorgenommen werden, müssen die Projektziele, Architekturentscheidungen und die aktuelle Roadmap verstanden werden.

## 1. Pflichtlektüre vor jeder größeren Änderung

Vor jeder nicht-trivialen Änderung müssen zuerst diese Dateien gelesen werden:

```text
PROJECT.md
TODO.md
```

### `PROJECT.md`

`PROJECT.md` beschreibt:

- Zweck des Projekts
- Produktvision
- aktuelle Architektur
- Windows-OCR-Engine
- Direct-RAM-Pipeline
- RTL-Strategie
- geplanten CLI-Stack
- Packaging- und Release-Strategie
- GitHub- und PyPI-Ziele
- Performance-Ziele
- Lizenzfragen
- Version-0.1-Umfang
- langfristige Architektur

Ein Agent darf keine größere Architekturentscheidung treffen, ohne zu prüfen, ob sie mit `PROJECT.md` vereinbar ist.

### `TODO.md`

`TODO.md` ist die aktuelle Entwicklungsroadmap.

Vor neuen Arbeiten muss geprüft werden:

- welches To-do aktuell als Nächstes vorgesehen ist
- welche Abhängigkeiten zwischen Aufgaben bestehen
- welche Entscheidungen noch offen sind
- ob eine Aufgabe bereits erledigt wurde
- ob eine Änderung eigentlich für eine spätere Version vorgesehen ist

Nach Abschluss einer Aufgabe soll `TODO.md` aktualisiert werden, wenn dies sinnvoll ist.

## 2. Aktuelle Prioritäten respektieren

Die Reihenfolge in `TODO.md` ist grundsätzlich maßgeblich.

Insbesondere gelten aktuell als frühe Kernentscheidungen:

1. Projektname festlegen
2. `PyMuPDF` gegen `pypdfium2` benchmarken
3. Lizenzstrategie festlegen
4. sauberes Git-/uv-Projekt aufbauen
5. Prototyp modularisieren
6. CLI mit Typer + Rich bauen
7. Tests und CI aufbauen
8. GitHub/PyPI/Release-Pipeline einrichten

Ein Agent soll nicht eigenständig große spätere Features vorziehen, wenn dadurch diese Grundlagen übersprungen werden.

## 3. Kernprinzipien des Projekts

Alle Änderungen sollen diese Prinzipien respektieren:

```text
fast
local
simple
transparent
multilingual
scriptable
open source
```

Zusätzlich:

- Windows-native OCR bleibt der primäre OCR-Kern.
- Arabisch ist der wichtigste Use Case.
- Andere Windows-OCR-Sprachen sollen vollständig unterstützt werden.
- Die Anwendung soll ohne GPU funktionieren.
- Die Anwendung soll lokal und offline arbeiten.
- Große Bücher müssen zuverlässig verarbeitet werden können.
- Die CLI soll angenehm und professionell wirken.
- Performance muss gemessen und nicht nur vermutet werden.

## 4. Keine Performance-Regression ohne guten Grund

Performance ist ein zentrales Projektziel.

Die aktuelle Direct-RAM-Pipeline darf nicht ohne Benchmark durch eine langsamere Architektur ersetzt werden.

Aktuelle Referenzwerte des Prototyps:

### 200 DPI

```text
ca. 0.281 s/page
```

### 300 DPI

```text
ca. 0.356 s/page
```

Diese Werte stammen von einem sechsseitigen arabischen Test-PDF auf dem bisherigen Testsystem und sind keine universellen Garantien, dienen aber als lokale Referenz.

Bei Änderungen an:

- PDF-Rendering
- Bitmap-Konvertierung
- OCR-Pipeline
- Speicherverwaltung
- Parallelisierung
- Preprocessing

soll ein reproduzierbarer Vorher-/Nachher-Benchmark durchgeführt werden.

Nicht optimieren, bevor gemessen wurde, wo tatsächlich Zeit verloren geht.

## 5. Direct-RAM-Pipeline erhalten

Die bevorzugte Pipeline lautet:

```text
PDF
→ Renderer
→ Pixel im RAM
→ SoftwareBitmap
→ Windows.Media.Ocr
```

Nicht ohne guten Grund zurückkehren zu:

```text
PDF
→ PNG
→ temporäre Datei
→ erneutes Einlesen
→ Decoding
→ OCR
```

Temporäre Rasterdateien sollen im normalen OCR-Pfad vermieden werden.

## 6. PDF-Renderer ist noch nicht endgültig entschieden

Aktuell wird `PyMuPDF` im Prototyp verwendet.

Vor dem öffentlichen Release muss `pypdfium2` getestet werden.

Ein Agent darf den Renderer nicht vorschnell als endgültig festschreiben.

Zu vergleichen sind mindestens:

- Rendering-Zeit
- RAM-/Buffer-Konvertierung
- Gesamtzeit
- OCR-Ausgabe
- Speicherverbrauch
- Paketgröße
- Distribution
- Lizenzfolgen
- 200 DPI
- 250 DPI
- 300 DPI

## 7. Lizenzfragen ernst nehmen

Vor Aufnahme neuer Runtime-Abhängigkeiten muss deren Lizenz geprüft werden.

Besonders wichtig:

- `PyMuPDF` hat relevante AGPL-/Commercial-Lizenzfolgen.
- `pypdfium2` wird unter anderem deshalb als Alternative geprüft.
- Die endgültige Projektlizenz ist noch nicht festgelegt.

Kein Agent soll eigenständig `MIT`, `Apache-2.0`, `AGPL-3.0` oder eine andere Lizenz als endgültig festlegen, bevor die Renderer-Entscheidung getroffen wurde.

Neue Abhängigkeiten sollen möglichst:

- aktiv gepflegt
- gut dokumentiert
- für Open Source geeignet
- für Windows verfügbar
- möglichst leichtgewichtig

sein.

## 8. CLI-Architektur

Für Version 0.1 ist derzeit vorgesehen:

```text
Typer
+
Rich
```

Typer für:

- Argument Parsing
- Commands
- Validation
- Help
- Completion

Rich für:

- Progress
- Tabellen
- Status
- Farben
- Fehlermeldungen
- Abschlusszusammenfassungen

Eine vollständige TUI soll nicht ohne konkreten Bedarf in Version 0.1 eingebaut werden.

Der CLI-Kern soll scriptbar bleiben.

Beispiele:

```powershell
PROJECTNAME book.pdf
PROJECTNAME book.pdf --lang ar --dpi 300
PROJECTNAME book.pdf --pages 30-50
PROJECTNAME languages
PROJECTNAME doctor
```

## 9. CLI muss sowohl für Menschen als auch für Skripte funktionieren

Schöne Terminal-Ausgabe ist erwünscht, darf aber Automatisierung nicht erschweren.

Deshalb:

- `--quiet` respektieren
- keine unnötigen Animationen in nicht-interaktiven Umgebungen
- Exit Codes sinnvoll verwenden
- Fehler nach `stderr`
- Ergebnisdaten nicht mit dekorativer Ausgabe vermischen
- spätere strukturierte Formate wie JSON berücksichtigen

## 10. RTL und Arabisch nicht beschädigen

Arabische OCR ist ein Kernbestandteil des Projekts.

Windows OCR liefert Wortpositionen über Bounding Boxes.

Für RTL-Sprachen wird die Reihenfolge pro Zeile rekonstruiert.

Aktuell vorgesehene RTL-Sprachen:

```text
ar
fa
ur
he
```

Änderungen an der Wortsortierung müssen mit arabischen Beispielen getestet werden.

Nicht einfach den gesamten Seitenstring umdrehen.

Die Sortierung muss zeilenweise und positionsbasiert bleiben.

## 11. Raw OCR nicht still korrigieren

Die Standardausgabe soll den OCR-Output möglichst transparent wiedergeben.

Nicht automatisch und unsichtbar:

- Wörter sprachlich korrigieren
- arabische Formen ersetzen
- `ﷺ` erzwingen
- Inhalte erraten
- Text mit KI umschreiben

Nachbearbeitung soll später explizit optional sein, z. B.:

```text
--clean
--normalize-arabic
```

Raw OCR muss weiterhin verfügbar bleiben.

## 12. Sprachunterstützung dynamisch behandeln

Keine feste Liste der tatsächlich verfügbaren OCR-Sprachen als Runtime-Wahrheit verwenden.

Stattdessen:

```python
OcrEngine.available_recognizer_languages
```

verwenden.

Die Anwendung soll erkennen, welche OCR-Sprachen auf dem Windows-System wirklich installiert sind.

Kurzcodes wie:

```text
ar
de
tr
ru
it
```

dürfen auf verfügbare vollständige Tags wie:

```text
ar-SA
de-DE
ru-RU
it-IT
```

aufgelöst werden.

## 13. DPI und Qualitätsmodi

Vorgesehene DPI-Werte:

```text
200
250
300
```

Vorgesehene Presets:

```text
fast      -> 200 DPI
balanced  -> 250 DPI
quality   -> 300 DPI
```

Andere Werte sollen nur bewusst unterstützt werden.

Qualitätsänderungen müssen anhand echter OCR-Ausgabe und nicht nur anhand Geschwindigkeit bewertet werden.

## 14. Projektstruktur sauber halten

Geplantes `src`-Layout:

```text
src/
└── PACKAGE/
    ├── __init__.py
    ├── __main__.py
    ├── cli.py
    ├── engine.py
    ├── renderer.py
    ├── languages.py
    ├── pages.py
    ├── rtl.py
    ├── output.py
    ├── config.py
    └── ui.py
```

Verantwortlichkeiten sollen getrennt bleiben.

Beispiele:

- CLI-Parsing nicht mit OCR-Engine vermischen
- Renderer nicht mit Rich-UI koppeln
- RTL-Logik separat testbar halten
- Output-Formatierung nicht tief in der OCR-Engine einbauen

Keine unnötig großen monolithischen Dateien erzeugen.

## 15. Python- und Tooling-Strategie

Aktuell vorgesehen:

```text
Python >= 3.11
uv
uv_build
Ruff
ty
pytest
coverage.py
```

Vor Einführung alternativer Tools prüfen, ob ein bereits vorgesehenes Werkzeug denselben Zweck erfüllt.

Keine Tool-Duplikation ohne klaren Vorteil.

Beispiele vermeiden:

```text
Black + Ruff formatter gleichzeitig
Flake8 + Ruff gleichzeitig
mehrere Package Manager gleichzeitig
```

## 16. Tests sind Pflicht für neue Kernlogik

Neue Logik soll soweit sinnvoll getestet werden.

Unit Tests insbesondere für:

- Page-Range Parsing
- Language Resolution
- RTL Sorting
- Output Naming
- Quality Presets
- Config
- CLI Validation
- Text Formatting

Integration Tests für:

- Windows.Media.Ocr
- PDF Renderer
- SoftwareBitmap
- Direct-RAM-Pipeline

Windows-/Sprachpaket-abhängige Tests sollen sauber übersprungen werden können, wenn die Umgebung die benötigte Capability nicht besitzt.

## 17. Testdaten und Copyright

Keine urheberrechtlich problematischen Buchseiten in das öffentliche Repository aufnehmen.

Für öffentliche Tests bevorzugen:

- selbst erzeugte PDFs
- Public-Domain-Texte
- synthetische Dokumente

Private Benchmark-Dateien dürfen lokal verwendet werden, sollen aber nicht automatisch committed werden.

## 18. GitHub und CI

Das Projekt soll über GitHub Actions getestet werden.

CI soll mindestens prüfen:

```text
Ruff check
Ruff format --check
type checking
pytest
package build
wheel install
CLI smoke test
```

Windows ist die zentrale Runtime-Plattform.

Mindestens ein Windows-Runner ist daher Pflicht.

Vor Änderungen an CI immer `TODO.md` prüfen, da Release- und Packaging-Schritte bewusst in Phasen geplant sind.

## 19. Releases

Geplantes Modell:

```text
Git Tag
→ Tests
→ Python Package
→ Windows Build
→ PyPI
→ GitHub Release
```

Alle Artefakte einer Version sollen aus demselben Commit / Tag stammen.

Versionen dürfen nicht manuell an mehreren Stellen auseinanderlaufen.

## 20. PyPI und Distribution

Geplante Installationswege:

```powershell
uv tool install PROJECTNAME
```

alternativ:

```powershell
pipx install PROJECTNAME
```

und:

```powershell
pip install PROJECTNAME
```

Zusätzlich sollen Windows-Binaries über GitHub Releases angeboten werden.

Für PyPI soll nach Möglichkeit Trusted Publishing / OIDC statt langfristiger API Tokens verwendet werden.

## 21. Keine unnötige Komplexität in v0.1

Version 0.1 soll bewusst klein und stabil bleiben.

Nicht ohne klare Entscheidung vorziehen:

- GUI
- vollständige TUI
- AI Text Correction
- Tesseract Ensemble
- OCR Server
- komplexe Layoutanalyse
- Batch-System
- Resume-System
- parallele OCR
- Markdown-Rekonstruktion

Diese Features gehören überwiegend in spätere Roadmap-Phasen.

## 22. Fehlerbehandlung

Normale Benutzerfehler sollen keine rohen Python-Tracebacks erzeugen.

Beispiele:

- PDF nicht gefunden
- Sprache nicht installiert
- ungültiger Seitenbereich
- Output-Datei nicht beschreibbar
- PDF beschädigt
- Windows OCR nicht verfügbar

Für Entwicklerfehler dürfen Debug-/Traceback-Modi vorgesehen werden.

## 23. Dokumentation aktuell halten

Wenn eine Änderung Auswirkungen hat auf:

- Architektur
- CLI-Syntax
- Dependencies
- Performance
- geplante Features
- Lizenz
- Distribution
- Releases

dann prüfen, ob aktualisiert werden müssen:

```text
PROJECT.md
TODO.md
README.md
AGENTS.md
```

Dokumentation soll nicht offensichtlich hinter dem Code zurückbleiben.

## 24. TODO-Status nach Arbeit aktualisieren

Wenn ein Punkt aus `TODO.md` vollständig umgesetzt wurde:

- Checkbox aktualisieren
- gegebenenfalls neue Folgeaufgaben ergänzen
- keine erledigten Aufgaben einfach löschen, wenn sie für die Projektgeschichte relevant sind
- große neue Aufgaben in die passende Phase einordnen

## 25. Keine eigenmächtigen Architekturwechsel

Vor größeren Änderungen wie:

- anderer Programmiersprache
- anderer OCR-Engine als Hauptengine
- Wechsel von Typer
- Wechsel des Package Managers
- neuer PDF-Renderer
- neues Build-System
- andere Lizenz
- vollständige TUI
- GUI

muss zuerst geprüft werden:

```text
PROJECT.md
TODO.md
```

und die Änderung muss einen klaren technischen Grund haben.

## 26. Änderungen klein und nachvollziehbar halten

Bevorzugen:

- kleine logisch zusammengehörige Änderungen
- klare Commits
- testbare Zwischenschritte
- keine unnötigen Refactors neben einem Feature
- keine großen Dependency-Wechsel ohne Benchmark oder Begründung

## 27. Bei Unsicherheit zuerst prüfen

Wenn ein Agent unsicher ist bezüglich:

- aktueller Roadmap
- Projektziel
- Lizenz
- Performance
- Feature-Scope
- Namensgebung
- Distribution

dann zuerst:

```text
1. PROJECT.md lesen
2. TODO.md lesen
3. bestehenden Code und Tests prüfen
4. erst danach Änderungen vornehmen
```

## 28. Definition of Done für größere Aufgaben

Eine größere Aufgabe gilt erst als abgeschlossen, wenn soweit zutreffend:

- Code implementiert
- Tests vorhanden / aktualisiert
- Ruff erfolgreich
- Type Check erfolgreich
- relevante Benchmarks durchgeführt
- CLI-Verhalten geprüft
- Dokumentation aktualisiert
- `TODO.md` aktualisiert
- keine offensichtliche Lizenz- oder Distribution-Regressions entstanden ist

## Kurzfassung für Agenten

Vor jeder größeren Arbeit:

```text
READ PROJECT.md
READ TODO.md
UNDERSTAND CURRENT ARCHITECTURE
CHECK CURRENT PRIORITY
MAKE SMALL TESTABLE CHANGES
BENCHMARK PERFORMANCE-SENSITIVE CODE
PRESERVE RAW OCR
KEEP ARABIC/RTL WORKING
UPDATE TESTS
UPDATE TODO.md WHEN DONE
UPDATE PROJECT.md IF ARCHITECTURE CHANGES
```
