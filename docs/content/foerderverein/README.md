# TSV Rudow Foerderverein - strukturierte Altinhalte

Diese Sammlung ist die redaktionelle Quellenbasis fuer die Foerderverein-Inhalte im Frontend.

## Zweck

- nachvollziehbare Migration der Altdaten
- saubere Zuordnung alt -> neue Seitenstruktur
- zentrale Grundlage fuer redaktionelle Pflege

## Quellen

- http://tsvrudow.de/foerderverein/
- http://tsvrudow.de/foerderverein/Satzung.html
- http://tsvrudow.de/foerderverein/Ansprechpartner.html
- http://tsvrudow.de/foerderverein/Beitrittsformular.html

Hinweis: Der Altbestand war technisch veraltet (Word-HTML), der Abruf erfolgte via HTTP.

## Mapping auf die neue IA

- `01_philosophie-und-historie.md` -> `html/philosophie.html`
- `02_satzung-kernpunkte.md` -> `html/transparenz.html`
- `03_ansprechpartner.md` -> `html/ansprechpartner.html`
- `04_beitritt-und-prozess.md` -> inhalt in `html/ansprechpartner.html` integriert
- redaktionelle Updates/News -> `html/aktuelles.html` (Demo/Upload-Preview)
- Ergebnisse & Tabellen -> `html/ergebnisse.html`
- `content_uploader.md` -> geplantes Feature/Design fuer E-Mail-Content-Upload

## Pflegeprozess

1. Inhalte zuerst in diesem Ordner aktualisieren.
2. Freigabe durch Redaktion/Vorstand einholen.
3. Danach HTML-Seiten synchronisieren.
4. Bei neuen Inhalten die Upload-Logik bzw. das Demo-Layout in `aktuelles.html` beachten.
5. Aenderungen in `CHANGELOG.md` dokumentieren.
