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
- `02_satzung-kernpunkte.md` -> `html/satzung.html`
- `03_ansprechpartner.md` -> `html/ansprechpartner.html`
- `04_beitritt-und-prozess.md` -> `html/beitrittsformular.html`
- redaktionelle Updates/News -> `html/aktuelles.html`

## Pflegeprozess

1. Inhalte zuerst in diesem Ordner aktualisieren.
2. Freigabe durch Redaktion/Vorstand einholen.
3. Danach HTML-Seiten synchronisieren.
4. Aenderungen in `CHANGELOG.md` dokumentieren.
