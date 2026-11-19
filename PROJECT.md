# MatnOCR – Project

## 1. Projektidee

Dieses Projekt ist eine sehr schnelle, vollständig lokale OCR-CLI für Windows.

Ziel ist es, gescannte PDF-Bücher und Dokumente direkt im Terminal in Text umzuwandeln – mit besonderem Fokus auf arabische Bücher, aber mit Unterstützung für alle OCR-Sprachen, die über die native Windows-OCR-Engine verfügbar sind.

Die Anwendung soll:

- vollständig lokal arbeiten
- keine Cloud-OCR benötigen
- ohne GPU funktionieren
- sehr schnell sein
- große PDFs verarbeiten können
- mehrere Sprachen unterstützen
- besonders gut für arabische Buchseiten funktionieren
- eine saubere und angenehme CLI bieten
- als Open-Source-Projekt auf GitHub veröffentlicht werden
- einfach über PyPI bzw. `uv tool` / `pipx` installierbar sein
- zusätzlich als fertiger Windows-Build über GitHub Releases angeboten werden

## 2. Aktueller technischer Kern

### OCR-Engine

Die eigentliche Texterkennung erfolgt über:

```python
Windows.Media.Ocr
```

Python greift über PyWinRT auf die native Windows Runtime API zu:

```python
from winrt.windows.media.ocr import OcrEngine
```

Vorteile:

- sehr schnelle lokale OCR
- kein separates großes KI-Modell
- Windows verwaltet die OCR-Sprachpakete
- offline verwendbar
- gute Qualität bei arabischem Buchdruck
- mehrere installierbare Sprachen

### Aktuell erkannte Windows-OCR-Sprachen auf dem Testsystem

```text
ar-SA
de-DE
tr-TR / tr
```

Windows unterstützt zusätzlich weitere OCR-Sprachen wie unter anderem:

```text
bg-BG
bs-LATN-BA
cs-CZ
da-DK
el-GR
en-GB
en-US
es-ES
es-MX
fi-FI
fr-CA
fr-FR
hr-HR
hu-HU
it-IT
ja-JP
ko-KR
nb-NO
nl-NL
pl-PL
pt-BR
pt-PT
ro-RO
ru-RU
sk-SK
sl-SI
sr-CYRL-RS
sr-LATN-RS
sv-SE
zh-CN
zh-HK
zh-TW
```

Die Anwendung soll nicht mit einer festen Sprachliste arbeiten, sondern die tatsächlich installierten Windows-OCR-Sprachen dynamisch über die Windows API abfragen.

## 3. Aktuelle Direct-RAM-Pipeline

Die erste Version schrieb jede gerenderte PDF-Seite als temporäre PNG-Datei auf die Festplatte.

Frühere Pipeline:

```text
PDF
→ PyMuPDF
→ RGB
→ PNG-Encoding
→ temporäre Datei
→ PNG erneut einlesen
→ BitmapDecoder
→ SoftwareBitmap
→ Windows OCR
```

Die aktuelle optimierte Pipeline arbeitet direkt im RAM:

```text
PDF
→ PDF Renderer
→ Pixel im RAM
→ SoftwareBitmap
→ Windows OCR
```

Dadurch entfallen:

- temporäre Bilddateien
- SSD-Schreibzugriffe
- erneutes Einlesen
- PNG-Encoding
- PNG-Decoding

Die OCR-Qualität blieb im Vergleich praktisch identisch, die Verarbeitung wurde jedoch schneller.

## 4. Aktueller PDF-Renderer

Der gewählte und implementierte Renderer ist `pypdfium2` auf Basis von PDFium.
Der Vergleich mit PyMuPDF auf sechs arabischen Benchmark-Seiten bei 200, 250
und 300 DPI ist laut `TODO.md` abgeschlossen. Rendering, Bitmap-Konvertierung,
OCR-Zeit, Gesamtzeit und OCR-Ausgaben wurden verglichen. Die OCR-Qualität war
praktisch auf PyMuPDF-Niveau; zugleich ermöglicht PDFium die gewählte
permissive Projektlizenz Apache-2.0.

Die Implementierung in `src/matnocr/renderer.py` verwendet zwei Pfade:

- **Originalscan-Fast-Path:** Deckt ein eingebettetes Bild mindestens 70 % der
  PDF-Seite ab, wird dieses Bild direkt bei der gewünschten DPI verarbeitet.
- **Fallback:** Ohne geeignetes Scanbild oder bei einem Runtime-Fehler im
  Fast-Path wird die vollständige PDF-Seite gerendert.

Beide Pfade kopieren BGRA-Pixel im RAM in ein Windows-`SoftwareBitmap`.
Temporäre Rasterdateien und Pillow sind dafür nicht erforderlich. Das
PDFium-Bitmap wird nach der Konvertierung explizit geschlossen. Im Fast-Path
wird die allgemeine Warnung beim Schließen eines foreign-Bitmaps gezielt
unterdrückt, da keine Ansicht seines Puffers an die OCR weitergegeben wird.

Speicherverbrauch und Wheel-Größe müssen noch verglichen werden; diese
Messungen sind laut Roadmap nicht blockierend für v0.1. Die vollständigen
Drittanbieter-Lizenzdateien müssen vor Windows-Binärreleases mitgeliefert werden.

## 5. Historische Performance-Referenz

Die folgenden Werte stammen vom früheren PyMuPDF-Direct-RAM-Prototyp mit einer
sechsseitigen gescannten arabischen PDF. Sie sind lokale historische
Referenzwerte, keine Messung der aktuellen pypdfium2-Paketversion. Der
Release-Benchmark mit dokumentierter Hardware steht laut `TODO.md` noch aus.

### 200 DPI – Direct RAM

```text
Pages:      6
Total:      1.685 s
Average:    0.281 s/page
```

Breakdown:

```text
Rendering:  0.040 s/page
Bitmap:     0.015 s/page
OCR:        0.224 s/page
```

### 300 DPI – Direct RAM

```text
Pages:      6
Total:      2.137 s
Average:    0.356 s/page
```

Breakdown:

```text
Rendering:  0.032 s/page
Bitmap:     0.032 s/page
OCR:        0.291 s/page
```

### Alte 300-DPI-PNG-Pipeline

```text
Average: ca. 0.42 s/page
```

### Neue Direct-RAM-Version

```text
Average: ca. 0.356 s/page
```

Die Worterkennung blieb praktisch identisch.

## 6. DPI-Modi

Die Anwendung soll drei direkte DPI-Modi unterstützen:

```text
200 DPI
250 DPI
300 DPI
```

Zusätzlich sollen benutzerfreundliche Presets angeboten werden:

```text
fast      -> 200 DPI
balanced  -> 250 DPI
quality   -> 300 DPI
```

Aktueller Standard:

```text
quality / 300 DPI
```

300 DPI hat auf den bisherigen arabischen Buchseiten an mehreren schwierigen Stellen bessere Ergebnisse geliefert, bei weiterhin sehr hoher Geschwindigkeit.

## 7. Arabisch und RTL

Ein besonderer Fokus des Projekts liegt auf Arabisch.

Windows OCR liefert die erkannten Wörter inklusive Bounding Boxes. Bei RTL-Sprachen wird die Wortreihenfolge deshalb anhand der horizontalen Position rekonstruiert.

Aktuell vorgesehene RTL-Sprachen:

```text
ar
fa
ur
he
```

Die Sortierung geschieht pro erkannter Zeile.

MatnOCR bewahrt standardmäßig die von Windows OCR erkannten Zeilen und erkennt
auffällig große vertikale Abstände als Absatzwechsel. Die Schwelle wird pro
Seite aus Wort-Bounding-Boxes und den typischen Zeilenabständen bestimmt. Dafür
ist weder eine zweite OCR-Runde noch eine temporäre Bilddatei erforderlich. Mit
`--no-layout` werden die erkannten Zeilen stattdessen mit Leerzeichen zu einem
fortlaufenden Text verbunden.

Stark fragmentierte OCR-Ergebnisse, wie sie bei reinen Ornament- oder
Kachelseiten entstehen können, werden gezielt mit 125 DPI kontrolliert. Nur
verdächtige Seiten erhalten diesen zusätzlichen Lauf. Bestätigt die
Kontroll-OCR keinen glaubwürdigen Text im gewählten Schriftsystem, bleibt die
Seite in der Ausgabe leer. Erkannte Wörter echter Textseiten werden dadurch
nicht sprachlich korrigiert oder umgeschrieben.

### Beispiel

Windows-interne visuelle Reihenfolge:

```text
أو العبادات في ركن النية هل الشافعية أصحابنا اختلف الأول
```

rekonstruiert:

```text
الأول اختلف أصحابنا الشافعية هل النية ركن في العبادات أو
```

## 8. Aktuelles CLI-Erlebnis

Die Anwendung soll nicht wie ein simples Python-Skript wirken, sondern wie eine professionelle moderne CLI.

Implementierter Stack:

```text
Typer
+
Rich
```

Typer übernimmt:

- Argument Parsing
- Subcommands
- Validation
- Help
- Typ-basierte Parameterdefinition

Shell Completion ist derzeit deaktiviert (`add_completion=False`).

Rich übernimmt:

- Progress Bars
- Tabellen
- Panels
- Farben
- Statusmeldungen
- Erfolgs- und Fehlermeldungen
- saubere Zusammenfassungen

Das CLI-Design ist für Version 0.1 einheitlich festgelegt:

- Cyan kennzeichnet Überschriften und zentrale Werte.
- Grün kennzeichnet erfolgreiche Aktionen.
- Gelb ist für Warnungen und Rot für Fehler reserviert.
- Die OCR-Konfiguration erscheint in interaktiven Terminals als kompaktes Panel.
- Die Hilfe gruppiert Eingabe, Erkennung und Ausgabe und enthält direkt nutzbare Beispiele.
- Benutzerfehler verwenden das einheitliche Format `Error: <Nachricht>` und gehen an `stderr`.
- In CI, bei umgeleiteter Ausgabe, mit `NO_COLOR` oder bei `TERM=dumb` werden ANSI-Farben deaktiviert.
- Fortschrittsanimationen laufen nur in einem interaktiven Terminal; `--quiet` unterdrückt sie vollständig.

### Standardaufruf

```powershell
matnocr book.pdf
```

### Explizite Sprache und DPI

```powershell
matnocr book.pdf --lang ar --dpi 300
```

### Seitenbereich

```powershell
matnocr book.pdf --pages 30-50
```

### Mehrere Bereiche

```powershell
matnocr book.pdf --pages 1,5,20-35,100
```

### Presets

```powershell
matnocr book.pdf --quality fast
matnocr book.pdf --quality balanced
matnocr book.pdf --quality quality
```

### Eigene Ausgabe

```powershell
matnocr book.pdf -o output.txt
```

### Ruhiger Modus für Skripte

```powershell
matnocr book.pdf --quiet
```

### Layout nicht beachten

```powershell
matnocr book.pdf --no-layout
```

## 9. Aktuelle Subcommands

### OCR

Standard:

```powershell
matnocr book.pdf
```

### Sprachen anzeigen

```powershell
matnocr languages
```

Beispiel:

```text
Installed OCR languages

✓ ar-SA    Arabic
✓ de-DE    German
✓ tr-TR    Turkish
```

Die Standardsprache für Aufrufe ohne `--lang` wird pro Windows-Benutzer
gespeichert:

```powershell
matnocr languages default ar-SA
```

Die Sprachenübersicht zeigt die aktuell gewählte Standardsprache ausdrücklich
an. Windows-OCR-Sprachpakete können außerdem verwaltet werden:

Auch der Haupt-Hilfetext von `matnocr` zeigt die aktuell konfigurierte
Standardsprache mit ihrem lokalisierten Namen und dem technischen Sprachcode
direkt unter der Projektbeschreibung an. Ist Arabisch nicht installiert, zeigt
die Hilfe den passenden Installationsbefehl.

```powershell
matnocr languages available
matnocr languages install fr-FR
matnocr languages remove fr-FR
```

`languages available` liest die vollständige Liste dynamisch über
`Get-WindowsCapability` aus und zeigt pro Sprachcode `Installed` oder
`Not installed`. Der lesbare Sprachname wird über
`Windows.Globalization.Language` in der Windows-Anzeigesprache des Nutzers
ermittelt. Dadurch muss MatnOCR weder Capability-Codes noch Übersetzungen als
feste Liste führen.

Installation und Entfernung verwenden die Windows-Capabilities
`Language.OCR~~~<tag>~0.0.1.0`. Läuft MatnOCR nicht erhöht, öffnet es über die
Windows-UAC-Abfrage eine administrative Windows PowerShell. Nach der Operation
wird der tatsächliche Capability-Status erneut geprüft. Die aktive
MatnOCR-Standardsprache kann nicht entfernt werden, bevor eine andere
Standardsprache gewählt wurde.

### Systemdiagnose

```powershell
matnocr doctor
```

Mögliche Ausgabe:

```text
MatnOCR system check

✓ Windows supported
✓ Windows.Media.Ocr available
✓ OCR languages detected
✓ PDF renderer available
✓ Direct-RAM pipeline available
✓ Max OCR image dimension detected

Ready.
```

### Version

```powershell
matnocr --version
```

## 10. Fehlerbehandlung

Die CLI soll verständliche Fehler erzeugen.

Beispiel bei fehlender OCR-Sprache:

```text
✗ Russian OCR language is not installed.

Detected OCR languages:
  ar-SA
  de-DE
  tr-TR

Install the Windows Russian OCR language capability and try again.
```

Die Anwendung soll niemals mit schwer verständlichen Python-Tracebacks enden, sofern es sich um normale Benutzerfehler handelt.

## 11. Ausgabeformate

### Version 0.1

TXT bleibt die anfängliche Standardausgabe. Einfaches Markdown ist auf
Nutzerwunsch aus v0.2 vorgezogen und implementiert. Es trennt Seiten mit
`# Page <PDF-Seitennummer>`, ohne weitere Buchstruktur abzuleiten.

```powershell
matnocr book.pdf --format md
matnocr book.pdf -o notes.md
matnocr output
matnocr output default md
matnocr output default txt
```

Die Standardausgabe wird neben der Standardsprache in der benutzerspezifischen
`config.json` gespeichert. Änderungen erhalten die jeweils andere Einstellung.
`.txt` bei `-o` wählt TXT, `.md` oder `.markdown` wählt Markdown, unabhängig vom
gespeicherten Standard und ohne Beachtung der Groß-/Kleinschreibung. Ohne Endung
wird die gewählte Formatendung ergänzt. `--format txt|md` überschreibt den
Standard für einen Aufruf; widerspricht es der Dateiendung, folgt vor OCR eine
Fehlermeldung. Andere Dateiendungen werden abgelehnt.

Vorhandene Ausgaben werden vor dem OCR-Lauf abgelehnt; nur `--force` erlaubt
bewusstes Ersetzen. Beim normalen Schreiben verhindert exklusives Anlegen
auch ein Überschreiben einer zwischenzeitlich entstandenen Datei. Bei `--force`
wird eine vollständige temporäre Textdatei neben dem Ziel geschrieben und erst
danach ersetzt. Fehlende Ausgabeordner, ungültige Pfade, Berechtigungs- und
Schreibfehler führen zu einer stderr-Meldung mit Exit Code 1 ohne Traceback.
Ausgabeordner werden nicht automatisch angelegt. Die temporäre Textdatei ist
kein Rasterbild und verändert die Direct-RAM-OCR-Pipeline nicht.

Automatische Dateinamen verwenden je nach Format `.txt` oder `.md`. Die
Markdown-Ausgabe ist UTF-8 und erhält erkannte Wörter und Absatzabstände;
Markdown-Sonderzeichen im OCR-Text werden nicht maskiert.

Die normale TXT-Ausgabe enthält die von Windows OCR erkannten Zeilen und ergänzt
bei deutlich größeren vertikalen Zeilenabständen eine Leerzeile. Mit
`--no-layout` werden die Zeilen zu fortlaufendem Text verbunden. Beide Modi
verändern keine erkannten Wörter.

Seitenmarker:

```text
========== Page 1 ==========

...

========== Page 2 ==========
```

### Spätere Versionen

Geplant bzw. denkbar:

```text
PDF (Text-PDF und durchsuchbare Scan-PDF, Ziel v0.2)
JSON
JSONL
```

JSON könnte später enthalten:

- Seitenzahl
- Zeilentext
- Wörter
- Bounding Boxes
- Sprache
- DPI
- Timing-Informationen

## 12. Roh-OCR vs. Nachbearbeitung

Die Standardausgabe soll möglichst nah am echten OCR-Ergebnis bleiben.

Automatische sprachliche Korrekturen sollen nicht still im Hintergrund stattfinden.

Spätere optionale Modi können z. B. sein:

```powershell
--clean
--normalize-arabic
```

Mögliche Funktionen:

- Unicode-BiDi-Steuerzeichen entfernen
- offensichtliche Artefakte entfernen
- optionale Normalisierung von `ﷺ`
- Leerzeichenbereinigung
- Zeilenbereinigung

Wichtig:

```text
raw OCR
```

und:

```text
postprocessed OCR
```

müssen klar unterscheidbar bleiben.

## 13. Aktueller Python-Projektstack

### Runtime

```text
Python >= 3.11
```

### Paket- und Projektmanagement

```text
uv
```

### Build Backend

```text
uv_build
```

### CLI

```text
Typer
Rich
```

### OCR

```text
PyWinRT
Windows.Media.Ocr
```

### PDF

```text
pypdfium2 / PDFium
```

### Tests

```text
pytest
coverage.py
```

### Linting / Formatting

```text
Ruff
```

### Type Checking

```text
ty
```

Ruff, ty, pytest und pytest-cov (coverage.py) sind bereits in der
Dev-Dependency-Gruppe von `pyproject.toml` eingetragen und in `uv.lock` erfasst.
Ruff, ty, pytest und Branch-Coverage sind in `pyproject.toml` konfiguriert.
Ruff prüft den aktiven Code und Tests; die historischen Experimente
`prototype.py` und `add_new_white_page.py` sind ausgeschlossen. ty prüft `src/`
und `tests/` für Python 3.11 unter Windows. Die installierten PyWinRT-Typen
benötigen keine globalen Regelabschaltungen; bestehende `Any`-Grenzen für native
Objekte sind in `README.md` erklärt. Lokale Befehle stehen ebenfalls dort.

## 14. Projektstruktur und geplanter Ausbau

```text
project/
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
├── PROJECT.md
├── TODO.md
│
├── src/
│   └── matnocr/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── engine.py
│       ├── renderer.py
│       ├── languages.py
│       ├── pages.py
│       ├── rtl.py
│       ├── output.py
│       ├── config.py
│       ├── doctor.py
│       ├── language_capabilities.py
│       ├── settings.py
│       ├── validation.py
│       └── ui.py
│
├── tests/
│   ├── unit/
│   │   ├── test_pages.py
│   │   ├── test_languages.py
│   │   ├── test_rtl.py
│   │   └── test_output.py
│   │
│   └── integration/
│       ├── test_windows_ocr.py
│       └── test_pdf_renderer.py
│
└── .github/
    ├── ISSUE_TEMPLATE/
    ├── pull_request_template.md
    └── workflows/
        ├── ci.yml
        ├── release.yml
        └── codeql.yml
```

Das Paket liegt unter `src/matnocr/`; Unit Tests sind unter `tests/unit/`
und Integrationstests unter `tests/integration/` vorhanden. Der Baum zeigt auch
geplante Dateien: GitHub-Workflows und weitere Open-Source-Dokumente sind offen. Den
verbindlichen Umsetzungsstand beschreibt `TODO.md`.

## 15. Packaging und Installation

Das Projekt verwendet `uv_build` und ein `src/`-Layout für das Python-Paket.

Konfigurierter Console Entry Point:

```toml
[project.scripts]
matnocr = "matnocr.cli:app"
```

Der Console Entry Point startet `matnocr`; alternativ ist
`python -m matnocr` verfügbar. Die vollständige Build- und Wheel-Prüfung bleibt
Teil der Packaging-Roadmap.

## 16. Installation für Nutzer

Aktuell wird aus dem lokalen Checkout installiert. Mit installiertem uv:

```powershell
uv sync --locked
uv run matnocr --help
```

Für einen eigenständigen CLI-Aufruf außerhalb der Projektumgebung:

```powershell
uv tool install .
```

Nach Änderungen am Checkout muss eine solche Tool-Installation aktualisiert
werden. Die Entwicklung kann direkt mit `uv run matnocr` getestet werden.

Nach einer späteren PyPI-Veröffentlichung sind `uv tool install matnocr`,
`pipx install matnocr` und `pip install matnocr` vorgesehen. PyPI-Publishing und
öffentliche GitHub-Releases sind laut Roadmap noch nicht eingerichtet.

## 17. Windows-Binary / GitHub Release

Zusätzlich zum Python-Paket soll ein fertiger Windows-Build angeboten werden.

Geplant:

```text
matnocr-windows-x64.zip
```

und eventuell:

```text
matnocr-windows-x64.exe
```

Für Version 1 soll zunächst PyInstaller getestet werden.

Zu prüfen:

```text
PyInstaller onedir
PyInstaller onefile
```

Später optional:

```text
Nuitka
```

Ziel ist, dass normale Windows-Nutzer die Anwendung ohne eigene Python-Installation verwenden können.

## 18. GitHub und Open Source

Das Projekt soll öffentlich auf GitHub veröffentlicht werden.

Geplante Repository-Dateien:

```text
README.md
LICENSE
CONTRIBUTING.md
CHANGELOG.md
SECURITY.md
CODE_OF_CONDUCT.md
PROJECT.md
TODO.md
```

Zusätzlich:

```text
.github/
```

mit:

- CI Workflows
- Release Workflow
- CodeQL
- Issue Templates
- Pull Request Template
- Dependabot-Konfiguration

## 19. CI – Continuous Integration

CI soll über GitHub Actions laufen.

Da die OCR Windows-spezifisch ist, muss mindestens ein Windows-Runner verwendet werden.

Geplanter Ablauf bei Pull Requests und Pushes:

```text
Checkout
→ setup uv
→ install Python
→ uv sync --locked
→ Ruff check
→ Ruff format --check
→ ty check
→ pytest
→ build wheel/sdist
→ install built package
→ CLI smoke test
```

### Python-Matrix

Geplant zu prüfen:

```text
3.11
3.12
3.13
3.14
```

Nur Versionen, die mit allen WinRT-Abhängigkeiten stabil funktionieren, sollen offiziell unterstützt werden.

## 20. Tests

### Unit Tests

Sollen unabhängig von installierten Windows-Sprachpaketen funktionieren.

Zu testen:

- Page-Range-Parser
- Language-Resolution
- RTL-Sortierung
- Output-Dateinamen
- Presets
- Config
- CLI Validation
- Textformatierung

### Integration Tests

Unter `tests/integration/`, mit dem pytest-Marker `integration`:

- Windows.Media.Ocr verfügbar
- SoftwareBitmap-Konvertierung
- echter OCR-Lauf
- PDF-Rendering
- Direct-RAM-Pipeline
- installierte Sprachpakete

Die Tests erzeugen eine eigene englische PDF im temporären Testverzeichnis.
Windows-abhängige Tests überspringen fehlende Plattform-/WinRT-Capabilities;
der echte Text-OCR-Test überspringt ein fehlendes englisches Sprachpaket.
Sie installieren keine Systemsprachen. GitHub Windows Runner können andere
OCR-Sprachen als das lokale System haben. Weitere synthetische deutsche und
arabische Dokumente bleiben in der Roadmap.

## 21. Releases

Vorgesehener Release-Ablauf:

```text
main
↓
Git Tag
↓
v0.x.y
↓
GitHub Actions
↓
Tests
↓
Python Build
↓
Windows Binary Build
↓
PyPI
↓
GitHub Release
```

Alle Artefakte einer Version sollen aus exakt demselben Git-Tag stammen.

## 22. PyPI

Das Projekt soll später auf PyPI veröffentlicht werden.

Beispiel:

```powershell
uv tool install matnocr
```

Der PyPI-Release soll möglichst über Trusted Publishing / OIDC erfolgen, sodass keine langfristigen PyPI-API-Tokens als GitHub Secrets gespeichert werden müssen.

## 23. GitHub Releases

GitHub Releases sollen zusätzlich bereitstellen:

```text
Python wheel
sdist
Windows x64 binary / zip
checksums
release notes
```

Später eventuell:

```text
Windows ARM64
```

## 24. Lizenzstrategie

MatnOCR ist unter **Apache-2.0** lizenziert. Die Entscheidung wurde nach dem
Renderer-Vergleich getroffen und ist in `LICENSE` sowie `pyproject.toml`
festgehalten. PyMuPDF ist keine Runtime-Abhängigkeit des Pakets.

Die Lizenzen der Abhängigkeiten bleiben eigenständig. `THIRD_PARTY_NOTICES.md`
dokumentiert insbesondere pypdfium2/PDFium, PyWinRT, Typer und Rich. Bei
gebündelten Windows-Releases müssen die vollständigen PDFium- und
Drittanbieter-Lizenzdateien der tatsächlich verwendeten Versionen beiliegen.

## 25. Projektname

Die Namensentscheidung ist abgeschlossen:

```text
Brand:       MatnOCR
PyPI:        matnocr
CLI:         matnocr
Python pkg:  matnocr
GitHub repo: matnocr
Executable:  matnocr.exe
```

Die Kollisionsprüfungen sind in Phase 0 von `TODO.md` als erledigt dokumentiert.
Der festgelegte Name bedeutet noch keine erfolgte Veröffentlichung auf GitHub
oder PyPI.

## 26. Positionierung

Das Projekt soll nicht nur als einfacher Wrapper um Windows OCR positioniert werden.

Die eigentliche Nische ist:

```text
High-performance PDF/book OCR CLI powered by Windows native OCR
```

Besondere Merkmale:

- PDF-first
- book-first
- Arabic-first, aber multilingual
- native Windows OCR
- Direct RAM
- RTL reconstruction
- Page ranges
- DPI presets
- sehr hoher Durchsatz
- vollständig lokal
- keine GPU
- angenehme CLI
- reproduzierbare Benchmarks

## 27. Version 0.1 – Zielumfang

Die erste echte Open-Source-Version soll bewusst kompakt bleiben.

Geplant:

- PDF-Eingabe
- Windows OCR
- Direct-RAM-Pipeline
- dynamische Windows-OCR-Sprachen
- Arabic / RTL-Rekonstruktion
- `--lang`
- `--pages`
- `--dpi`
- `--quality`
- `--output`
- TXT- und einfache Markdown-Ausgabe mit gespeichertem Standard
- `languages`
- `doctor`
- `--quiet`
- `--version`
- Rich Progress
- saubere Fehlermeldungen
- Python Package
- GitHub CI
- PyPI Release
- GitHub Windows Release

Noch nicht zwingend in v0.1:

- GUI
- KI-Korrektur
- Tesseract-Ensemble
- komplexe Layout-Rekonstruktion
- komplexe Markdown-Layoutrekonstruktion
- OCR-Server
- parallele OCR
- Batch-Ordnerverarbeitung

## 28. Version 0.2+ – mögliche Erweiterungen

### Erweiterte Ausgabe

Einfaches Markdown mit Seitenüberschriften ist bereits in v0.1 verfügbar.
Weitere Ziele:

- PDF-Export für Version 0.2 nach der ersten öffentlichen Veröffentlichung:
  - Text-PDF mit sichtbarem OCR-Text, geeigneten Schriften, Arabisch-/RTL-Darstellung und Seitenumbrüchen.
  - Durchsuchbare Scan-PDF mit Originalseiten und unsichtbarer OCR-Textebene zum Suchen und Kopieren.
- JSON
- JSONL
- Bounding Boxes

Für beide PDF-Varianten müssen Backend und Lizenzfolgen sowie Textpositionen,
Schriften und Such-/Kopierverhalten bei Arabisch geprüft werden. PDF-Export ist
noch nicht implementiert und soll die bestehende Direct-RAM-OCR nicht verändern.

### Batch-Verarbeitung

```powershell
matnocr batch ./books
```

### Resume

Abgebrochene große OCR-Jobs fortsetzen.

### Benchmark Command

```powershell
matnocr benchmark book.pdf
```

### Renderer Benchmark

Der initiale PyMuPDF-/PDFium-Vergleich ist abgeschlossen. Weitere Messungen
zu Speicherverbrauch und Wheel-Größe sowie wiederholbare Release-Benchmarks
bleiben vorgesehen.

### Alternative OCR Engines

Optional:

- Tesseract
- Windows OCR + Tesseract Ensemble
- Fallback-Engine für schwierige Seiten

### Arabische Nachbearbeitung

Optional:

- ﷺ-Normalisierung
- BiDi-Cleanup
- Unicode-Normalisierung
- Artefakterkennung

### Strukturierte Ausgabe

- Überschriften
- Fußnoten
- Seitenzahlen
- Absätze
- Tabellen

## 29. Benchmark-Regeln

Performance-Vergleiche sollen reproduzierbar sein.

Für jeden Test dokumentieren:

- PDF
- Seitenzahl
- DPI
- CPU
- Windows-Version
- Python-Version
- Renderer
- OCR Engine
- Render-Zeit
- Bitmap-Zeit
- OCR-Zeit
- Gesamtzeit
- durchschnittliche Zeit pro Seite

Urheberrechtlich geschützte Testseiten sollen nicht ohne Erlaubnis in das öffentliche Repository aufgenommen werden.

Für CI-Tests sollen stattdessen eigene oder Public-Domain-Testdokumente verwendet werden.

## 30. Langfristige Vision

Das langfristige Ziel ist eine Open-Source-Windows-CLI, mit der ein Nutzer beispielsweise nur Folgendes ausführen muss:

```powershell
matnocr kitab.pdf --lang ar --pages 30-100
```

und innerhalb kurzer Zeit eine saubere Textdatei erhält.

Das Projekt soll die Einfachheit einer modernen CLI mit der Geschwindigkeit der nativen Windows-OCR-Engine verbinden.

Langfristige Kernprinzipien:

```text
fast
local
simple
transparent
multilingual
scriptable
open source
```
