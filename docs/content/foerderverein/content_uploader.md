# Content-Uploader fuer Foerderverein

## Ziel

Die Inhalte des Foerdervereins sollen künftig nicht nur manuell im CMS oder in HTML-Dateien gepflegt werden, sondern auch per E-Mail durch definierte Vereinsmitglieder bzw. Mitglieder des Foerdervereins eingereicht werden koennen.

Der geplante Ablauf sieht vor, dass E-Mails mit klar definierten Metadaten und Inhalten als "to be posted content" behandelt werden. Diese eingehenden Inhalte werden anschließend automatisch verarbeitet, strukturiert und in das Frontend als feste Inhaltsboxen integriert.

## Use Case

Ein autorisiertes Vereinsmitglied sendet eine E-Mail mit:

- Betreff / "about"-Angabe
- Bildanhang oder Bild-URL
- Freitext / Inhalt
- optional: Kategorie oder Zielseite
- optional: Freigabe-Flag / Status

Diese E-Mail wird als eingehender Vorschlag behandelt, nicht unmittelbar publiziert.

## Zustandsmodell

### 1. Eingang

Die Mail wird durch ein Postfach oder Mail-Handler verarbeitet.

Erforderliche Kriterien:

- Absender ist ein definiertes Vereinsmitglied oder eine autorisierte E-Mail-Adresse
- Betreff / Thema beinhaltet einen erlaubten Wert, z.B. "Foerderverein: Beitrag"
- Mail enthaelt entweder ein Bild oder Text oder beides

### 2. Validierung

Die Mail wird geprueft auf:

- Herkunft / Autoritaet des Absenders
- Vorhandensein eines Bildes und/oder eines Textkorpus
- Mindestlaenge des Textes
- erlaubte Dateiformate fuer Bilder
- Vorhandensein eines "about"-Werts zur Unterscheidung der Inhalte

Wenn die Mail nicht den Regeln entspricht, wird sie als abgelehnt markiert und nicht weiterverarbeitet.

### 3. To-be-posted-content

Gültige Mails werden als "to be posted content" gespeichert.

Datenmodell (vereinfacht):

```json
{
  "id": "unique-id",
  "sender": "name@domain.de",
  "author": "Mitgliedsname",
  "subject": "Foerderverein: Veranstaltung / Projekt / Beitrag",
  "about": "Beitrag zur Vereinsarbeit",
  "status": "to_be_posted",
  "image": {
    "filename": "bild.jpg",
    "mimeType": "image/jpeg",
    "binary": "base64-or-uploaded-file"
  },
  "text": "Freitext des eingereichten Beitrags...",
  "submittedAt": "2026-10-02T12:00:00Z",
  "approvedBy": null,
  "target": "aktuelles"
}
```

## Verarbeitungsschritt

### Bild- und Text-Parsing

Nach erfolgreicher Annahme wird der Inhalt verarbeitet:

1. Bild extrahieren und als Bilddatei speichern
2. Text aus der E-Mail als Klartext normalisieren
3. Umlaute, Leerzeichen und Absatzstruktur standardisieren
4. Bild- und Textbestand in eine einheitliche Struktur überführen
5. Inhalte einer vordefinierten Layoutvorlage zuordnen

### Parsing-Regeln

- Der Text wird als Rohtext übernommen und in sinnvolle Absätze gegliedert
- Ueberschriften werden wenn moeglich erkannt und als kurze Teaser- oder Abschnittstitel genutzt
- Bild und Text werden als Paar behandelt; die Bildbeschreibung ist optional
- Leere Mail-Abschnitte, Signaturen und automatisierte E-Mail-Header werden entfernt

## Ziel-Layout im Frontend

Die verarbeiteten Inhalte werden in ein festes Format als Content-Box eingefuegt.

### Grundprinzip

- Bild links oben im Kasten, mit Rahmen
- Bild wird zugeschnitten bzw. skaliert, damit es sauber in das Layout passt
- Text rechts vom Bild, mit Fließtext um das Bild herum
- Wenn Text länger ist, läuft er unterhalb des Bildes weiter
- Das Gesamtlayout bleibt konsistent und wiederverwendbar

### Layoutbeschreibung

```text
+--------------------------------------------------------------+
| [ Bild links, mit Border, cropped/resized ]   [ Textblock ] |
|                                              |             |
|                                              |             |
|                                              |             |
| [ Text fließt um Bild herum, rechts und darunter ]        |
+--------------------------------------------------------------+
```

### CSS-Designprinzipien

- Bild als float:left oder als grid-basierte Linke Spalte
- Bereich mit klarer Box-Border / abgestimmter Hintergrundfarbe
- Schriftblock mit einheitlicher Innenabstand
- Responsive Verhalten: auf mobilen Geräten wird das Bild unter den Text verschoben
- Bild darf nicht verzerrt werden; es wird mit `object-fit: cover` oder vergleichbarer Regel zugeschnitten

### Strukturidee im HTML

```html
<article class="content-box content-box-email">
  <div class="content-box__image-wrap">
    <img src="..." alt="..." class="content-box__image">
  </div>
  <div class="content-box__text">
    <h3>Beitragstitel / About</h3>
    <p>Textabschnitt 1...</p>
    <p>Textabschnitt 2...</p>
  </div>
</article>
```

## Aufgabenbereich des Parsers

Der Parser soll die eingegangene E-Mail in folgende Felder aufteilen:

- `title` oder `about`
- `image`
- `body` / `content`
- `author`
- `submittedAt`
- `status`
- `targetSection`

## Freigabe- und Moderationslogik

Die eingehende Mail soll nicht automatisch live gehen.

Vorgeschlagene Reihenfolge:

1. Mail eingegangen
2. Validierung und Parsing
3. Vorschau/Preview im Admin-Bereich
4. Freigabe durch Vorstand oder definierte Mitglieder
5. Veröffentlichung in definierter Inhaltsbox
6. Archivierung der ursprünglichen E-Mail

## Anforderungen an die Redaktion

- Definierte Absender-Domains oder Mitgliedslisten
- klare E-Mail-Vorgaben fuer Betreff und Inhalt
- optionales Redaktions-Review vor Publikation
- separate Ablage von "approved", "rejected" und "to_be_posted"

## Empfehlenswerte Richtlinien

- Keine unkontrollierte Freigabe von externen E-Mails
- Keine Veröffentlichung ohne Bild oder Text
- Kein Live-Posten ohne klaren "about"-Wert
- einheitliches Layout fuer alle eingereichten Inhalte
- Inhalte sollen immer als Vereinskommunikation erkennbar sein

## Vorschlag fuer die Produkt-Ansicht

Die neue Funktion kann als "E-Mail-Content-Upload" oder "Mitglieder-Content-Upload" behandelt werden.

Die zentrale Idee lautet:

> Eine autorisierte Vereins-Mitglieds-E-Mail wird als Content-Vorschlag verarbeitet. Der Beitrag wird automatisch in einen festen Bild-Text-Box-Container umgewandelt und erst nach Freigabe im Frontend veröffentlicht.

## Offene Punkte / Nacharbeit

- Welche E-Mail-Adressen sind freigeschaltet?
- Wie werden Bildformate und Größen kontrolliert?
- Welche Abschnittsseiten sollen als Ziel dienen?
- Wie soll die Vorschauen-Ansicht für Redakteure aussehen?
- Wer darf freigeben?

## Abschluss

Diese Funktion schafft einen einfachen, kontrollierten und wiederverwendbaren Weg, Vereinsinhalte aus E-Mails in das Frontend zu überführen. Die Inhalte bleiben aber in einer klaren, moderierten Pipeline: Eingang -> Prüfung -> To-be-posted -> Freigabe -> Publikation.
