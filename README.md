# Pokémon Karten-Tracker

Deine eigene App für die Pokémon-Sammlung: Nummer eintippen, Cardmarket-Preis (Durchschnitt der letzten 7 Tage) sehen, mit einem Klick hinzufügen. Läuft am PC und am Handy als installierte App, die Sammlung ist auf allen Geräten dieselbe.

Einrichtung dauert einmalig etwa 20 Minuten. Du brauchst zwei kostenlose Konten: **GitHub** (dort liegt die App) und **Supabase** (dort liegt deine Sammlung).

---

## 1. App auf GitHub hochladen

1. Konto auf https://github.com anlegen (falls noch nicht vorhanden).
2. Oben rechts auf **+** > **New repository**.
   - Name: `karten-tracker`
   - **Public** auswählen (nötig für kostenloses Hosting, deine Sammlung liegt nicht hier, sondern bei Supabase)
   - **Create repository**
3. Auf der neuen Seite **uploading an existing file** anklicken und alle Dateien und Ordner aus diesem Ordner hineinziehen: `index.html`, `config.js`, `manifest.webmanifest`, `sw.js`, `supabase.sql`, `README.md`, die Ordner `data`, `icons`, `tools`. Unten auf **Commit changes**.
4. Die Datei für die wöchentlichen Preise extra anlegen (der Ordner `.github` ist auf vielen Rechnern versteckt):
   **Add file** > **Create new file**, als Namen `.github/workflows/preise.yml` eintippen, den Inhalt der gleichnamigen Datei aus diesem Ordner hineinkopieren, **Commit changes**.

## 2. Als Webseite freischalten

1. Im Repository auf **Settings** > **Pages**.
2. Bei *Source* **Deploy from a branch** wählen, Branch **main**, Ordner **/ (root)**, **Save**.
3. Nach ein bis zwei Minuten steht oben die Adresse, etwa `https://DEINNAME.github.io/karten-tracker/`. Das ist deine App.

## 3. Wöchentliche Preise erlauben

1. **Settings** > **Actions** > **General**, ganz unten bei *Workflow permissions* **Read and write permissions** wählen, **Save**.
2. Reiter **Actions** > **Preise aktualisieren** > **Run workflow**. Nach etwa einer Minute ist ein grüner Haken da. Ab jetzt läuft das jeden Montag früh von selbst.

## 4. Supabase für den Sync einrichten

1. Konto auf https://supabase.com anlegen, **New project**. Name egal, Region **Frankfurt**, Datenbank-Passwort irgendwo notieren.
2. Links **SQL Editor** > **New query**, den kompletten Inhalt von `supabase.sql` einfügen, **Run**.
3. Links **Authentication** > **URL Configuration**: bei *Site URL* deine App-Adresse aus Schritt 2 eintragen, speichern.
4. Optional, damit du keine Bestätigungs-Mail brauchst: **Authentication** > **Sign In / Providers** > **Email**, *Confirm email* ausschalten.
5. **Project Settings** > **API** (bzw. **Data API**): *Project URL* und den Schlüssel **anon public** kopieren.
6. Zurück auf GitHub die Datei `config.js` öffnen, auf den Stift klicken, beide Werte zwischen die Anführungszeichen setzen, **Commit changes**:

   ```js
   window.PKT_CONFIG = {
     supabaseUrl: 'https://xxxxxxxx.supabase.co',
     supabaseKey: 'eyJhbGciOi...'
   };
   ```

   Der *anon*-Schlüssel darf öffentlich sein, die Datenbank lässt trotzdem nur dich an deine Einträge.

## 5. Anmelden und alte Sammlung übernehmen

1. App-Adresse öffnen, E-Mail und Passwort eingeben, **Neues Konto anlegen**, danach **Anmelden**.
2. Reiter **Konto** > **Importieren...** > Datei `meine-sammlung.json` aus diesem Ordner wählen. Damit sind deine bisherigen Karten drin.

## 6. Installieren

- **PC (Chrome oder Edge):** App-Adresse öffnen, oben in der Titelleiste auf **App installieren** klicken (oder das Symbol rechts in der Adresszeile). Danach startet sie wie ein eigenes Programm, auch über das Startmenü.
- **iPhone:** Adresse in **Safari** öffnen, Teilen-Symbol > **Zum Home-Bildschirm**.
- **Android:** Adresse in **Chrome** öffnen, Menü (drei Punkte) > **App installieren**.

Einmal pro Gerät anmelden, dann ist alles synchron.

---

## Gut zu wissen

- **Preise:** kommen aus dem öffentlichen Cardmarket-Preisguide, Durchschnitt der letzten 7 Tage. Bei deutschen, englischen, französischen usw. Karten führt Cardmarket alles als ein Produkt, japanische Karten haben eigene Preise. Karten, die nicht im Katalog stehen, trägst du über "Von Hand eintragen" mit eigenem Wert ein.
- **Verlauf:** Die App speichert pro Woche einen Preispunkt, sobald du sie öffnest. Einmal pro Woche reinschauen reicht.
- **Supabase pausiert** kostenlose Projekte, wenn eine Woche lang niemand darauf zugreift. Dann kommt eine Mail, und du klickst im Supabase-Dashboard auf *Restore*. Deine Daten bleiben erhalten.
- **GitHub** schaltet geplante Abläufe manchmal nach 60 Tagen ohne Aktivität ab. Kommt dazu eine Mail, im Reiter *Actions* einfach wieder aktivieren.
- **Sicherung:** Reiter *Konto* > *Exportieren* speichert die ganze Sammlung als Datei.
- **Kartenbilder und Set-Logos** werden live von TCGdex geladen.
