# Jüdisches Adressbuch

Arbeit mit den Daten des Jüdischen Adressbuches der ZLB.

## Schritte

### Laden der [CSV Daten](https://offenedaten.de/storage/f/2014-03-11T06%3A13%3A22.580Z/adressbuchdaten-juedischesadressbuchvongrossberlin1931-version1-0-140310.csv)
nach [data/0-adressen.csv](data/0-adressen.csv) geladen

### Geocodierung
* Wegen Rate Limiting ist Googles Geocoder für die große Zahl der Adressen schlecht geeignet, vermutlich verstöße eine Nutzung auch gegen die Lizenzbedingungen: Im Sinne offener Daten OpenStreetmap Daten nutzen. Den OpenStreetMap [Nominatim Server lokal installieren](http://wiki.openstreetmap.org/wiki/Nominatim/Installation), um schnell viele Abfragen machen zu können.
* Das Skript zum Ermitteln der Koordinaten ist in [data/1-koordinaten/](data/1-koordinaten). Es cached die Ergebnisse (um Raum für Experimente zu bieten) und gibt die Ergebnisse aus als:
	* JSON Array mit einem Eintrag für jedes erfolgreiche Lookup. Dieser ist ein Array mit Feldern: id, lat, long, Name, Beruf, Adresse.
	* CSV Datei mit Spalten: id, lat, long
* Liefert Nominatim mehrere Ergebnisse, wird
* Etwa 10% der Adressen werden nicht gefunden. Bei einigen Beispielen scheint dies an geänderten Straßennamen zu liegen.
* Einige Adressen werden grob (z.B. bei doppelten Straßennamen – erste Experimente zeigen, daß die Nutzung der Orsteilnamen nicht wirklich hilft) oder etwas (scheinbar, wenn OpenStreetmap die Hausnummern nicht richtig kennt) falsch angezeigt

### Web-Anzeige
* Verfügbar unter [http://earthlingsoft.net/ssp/juedisches-adressbuch/](http://earthlingsoft.net/ssp/juedisches-adressbuch/)
* Visualisierung auf OpenStreetMap Karte mit [Leaflet](http://leafletjs.com/)
* Zoomabhängige Clusterung der Böbbel durch [Leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster): Das Laden der Seite ist wegen der mehr als 60000 Böbbel nicht wirklich schnell, funktioniert erstaunlicherweise danach aber ziemlich gut

### Verbindung mit Adressbuchseite
* Skripte im Ordner [data/2-volltext](data/2-volltext).
* Die Daten dafür sind momentan nicht in der [zugehörigen METS Datei](http://digital.zlb.de/viewer/metsresolver?id=1931001_1931) zu finden.
* Laden und extrahieren die Namen aus den Volltexten der ZLB und versuchen eine eindeutige Zuordnung zu finden (6 kurze Shellbefehle mit Standardtools).
* Es klappt für etwa 50% der Einträge. Probleme sind einerseits mehrfach auftauchende Namen, andererseits Werbung oben auf der Seite, durch die der extrahierte Text kein Name ist.
* Zuordnung in der Datei [data/2-volltext/id-name-seite.tsv](data/2-volltext/id-name-seite.tsv), zusammengeführt mit den Originaldaten bei [Google Spreadsheets](https://docs.google.com/spreadsheets/d/1oSrX8P-LLkrnJij5JyjiXsoMC5JiLGIyLgzTobowh6c/edit?usp=sharing) (im Blatt `seite-erster` müssen die `#N/A` Felder in der Spalte `erste ID` ausgefüllt werden).

## Ideen
* Suchschlitz zum Filtern der angezeigten Böbbel nach Name und Adresse
* Abgleich mit Wikidata: Wieviele Personen mit den vorhandenen Namen finden wir? Wie gut läßt sich feststellen, ob es die richtigen sind? Damit ließen sich für die gefundenen Personen weitere Querverweise realisieren.
* Anzahl: Wie verhält sich die Anzahl der Adressbucheinträge zur Anzahl der Menschen? Nur ein Eintrag pro Familie?
* Zeitgemäße Karten: läßt sich eine Karte aus der Zeit, z.B. aus dem Bestand der [Alt Berlin Site](http://www.alt-berlin.info/cgi/stp/lana.pl?nr=21&gr=5) einbinden? Technische Schwierigkeiten? Sind das offene Daten?
* Weitere Daten zu den Personen: Was wissen wir über ihr Schicksal? Was wurde im Rahmen von [Stolperstadt](http://www.stolperstadt.org/deutsch/) schon festgestellt?
* Heatmap ([Screenshot 1](screenshots/heatmap1.png), [Screenshot 2](screenshots/heatmap2.png)): bringt nicht wirklich neue Information und ist mit (dieser) browserseitigen Bibliothek ziemlich langsam

## Credits

* Daten von der Zentral- und Landesbibliothek Berlin: [Adressliste](https://offenedaten.de/dataset/adressbuchdaten-des-judischen-adressbuchs-fur-grob-berlin-von-1931), [Digitalisat](http://digital.zlb.de/viewer/image/1931001_1931/1/LOG_0003/)
* Inspiriert durch [Coding da Vinci](http://codingdavinci.de/) 2013
* Umgesetzt von [Sven-S. Porst](http://earthlingsoft.net/ssp), [ssp-web@earthlingsoft.net](mailto:ssp-web@earthlingsoft.net?subject=J%C3%BCdisches%20Adressbuch)
