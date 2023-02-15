# Beitragsrichtlinien (Contributing Guidelines)

> English note: Since this software is dedicated to german scouts, most of the documentation and community content on Github is in German.

Herzlich Willkommen bei knotnpunkt. Schön dass du den Weg hierher gefunden hast.

Diese Seite soll eine Hilfestellung für die Menschen liefern, die etwas betragen möchten, egal ob es ein Bug-Report, eine Verbesserung der Dokumentation oder ein komplett neues Feature ist. Außerdem ist dies der Ort für Konventionen und Hinweise, die eine einfachere Entwicklung ermöglichen. Bitte nimm dir die Zeit, bevor du einen Issue erstellt oder mit der Arbeit im Code beginnst.

## Wie kann man etwas beitragen?
+ *Fehlerhinweise* (sog. Bug Reports) sind Stellen in der Software, die deiner Meinung nach nicht so funktionieren wie geplant oder offensichtlich falsch sind (Rechtschreibfehler z. B.) Ein Fehler kann im Issues-Tab auf Github eingesendet werden. Bitte beachte "Vor dem Erstellen eines Issues". Wenn dir ein Fehler auffällt, kannst du dich gerne direkt an die Arbeit machen.
+ *Neue Funktionen* die bereits fertig entwickelt sind und in dieses Repository integriert werden sollen, können per Pull Request eingesendet werden. Optional kann ein Issue mit weitergehender Beschreibung der Funktion erstellt werden.
+ *Ideen oder Anfragen* bzgl. neuer Funktionen reichst du bitte auch als Issue ein. Das ermöglicht die Diskussion und genauere Koordination der angefragten Funktionen.
+ *Was dir sonst so einfällt* kannst du entweder auf der Diskussions-Seite oder über einen anderen Kanal an uns herantragen.

## Vor dem Erstellen eines Issues

Bitte kontrolliere im Vorhinein, ob dein Anliegen bereits aufgeführt ist. Dabei kann dir die Suchfunktion helfen, da dort auch bereits geschlossene Issues und Pull Requests angezeigt werden. Beteilige dich im Zweifelsfall an der bestehenden Diskussion, bevor du ein neues Thema eröffnest.

## Hinweise für Entwickler*innen

### Umgang mit dem Datenbankschema

Um die Kompatibilität des Datenbankschemas bei neuen Versionen sicherzustellen, ist hier besondere Vorsicht geboten. Um verschiedene Versionen des Schemas verwalten zu können, wird die Python-Bibliothekt flask-db bzw. alembic eingesetzt. Um eine Änderung an der Schemadefinition vorzunehmen, beachte folgende Punkte:

+ Stoppe alle lokalen knotnpunkt-Instanzen während du mit flask-db/alembic arbeitest.
+ Um eine Änderung am Datenbankschema einzuführen, muss mit flask-db eine sog. Revision (engl.) erstellt werden. Wenn deine Änderungen in knotnpunkt/database/db.py gespeichert sind, führe folgenden Befehl aus und ersetze `<MESSAGE>` durch eine kurze Information über deine Änderung.
```PowerShell
flask db migrate revision --autogenerate -m '<MESSAGE>'
```
+ Dadurch wird eine neue Datei im Ordner migrations/versions erstellt, die die Datenbankänderungen als Python-Code ausdrückt. Da flask-db bzw. alembic nicht 100% aller Änderungen erkennen kann, muss diese Datei unbegingt manuell überprüft werden. Schau dazu bitte in der Dokumetation zu alembic nach.
+ Wenn alles passt, können deine Änderungen auch auf deine lokale Datenbank übertragen werden:
```PowerShell
flask db migrate
```
> An dieser Stelle wird evtl. Issue #70 Einfluss haben.
+ Wenn alles passt und du deine Änderungen in einen Commit verpacken möchtest, denke bitte daran, die neue Revisions-Datei zusammen mit den Änderungen in knotnpunkt/database/db.py in einem Commit zusammenzufassen (ohne weitere Änderungen) um die Integration so einfach wie möglich zu gestalten.
