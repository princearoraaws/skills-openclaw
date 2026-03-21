# Humanizer-DE

**Erster deutscher KI-Text-Detektor für OpenClaw.**

5-Durchgang-Analyse: Erkennt 24 KI-Schreibmuster, flaggt 168 deutsche KI-Vokabeln und Phrasen in 3 Schweregrad-Stufen, misst 5 statistische Signale (Burstiness, TTR, Flesch-DE) und schreibt Texte mit Personality Injection um. Inklusive Lesch-Stil-Layer.

> Version 1.0.0 · Autor: OpenClaw · Lizenz: MIT · Sprache: Deutsch

---

## Was macht dieser Skill?

Du gibst ihm einen deutschen Text. Er sagt dir:

1. **Wie stark** der Text nach KI klingt (Score 0–100)
2. **Wo genau** KI-Muster stecken (markiert + erklärt)
3. **Wie du es besser machst** (konkrete Umschreibvorschläge)

Score 0 = klingt menschlich. Score 100 = klingt wie ChatGPT auf Autopilot.

---

## Installation

Sag deinem OpenClaw:

> *"Installiere den Skill Tikitackr/humanizer-de"*

OpenClaw lädt den Skill herunter und bestätigt die Installation. Fertig. Kein Terminal, kein manueller Download – alles läuft über den Chat.

Der Skill wird per Chat-Befehl aufgerufen (z.B. "Check diesen Text") – er läuft nicht automatisch im Hintergrund.

---

## Befehle

| Befehl | Was passiert |
|--------|-------------|
| `Check diesen Text` | Vollständiger Report: Score + Muster + Vokabeln + Statistik + Vorschläge |
| `Score: [Text]` | Nur der Score (0–100) mit Kurzeinschätzung |
| `Was klingt hier nach KI?` | Nur die problematischen Stellen markiert |
| `Humanisiere das` | Text umschreiben mit Personality Injection (Basis-Stil) |
| `Humanisiere das im Lesch-Stil` | Umschreiben mit Lesch-Layer (Visionär/Mahner/Erklärer) |
| `Mach das menschlicher` | Wie "Humanisiere das" – Synonym |

---

## Was wird analysiert?

### 24 KI-Schreibmuster

Der Skill erkennt 24 typische Muster, die KI-generierte deutsche Texte verraten – von Bedeutungsinflation über Aufzählungs-Sucht bis zu leeren Verstärkern. Jedes Muster hat einen Schweregrad (HOCH / MITTEL / NIEDRIG) und konkrete Umschreibvorschläge.

### 168 KI-Vokabeln & Phrasen in 3 Tiers

- **Tier 1 (VERBOTEN):** 44 Wörter die sofort auffallen ("ermöglicht", "nahtlos", "maßgeblich")
- **Tier 2 (SPARSAM):** 47 Wörter die in Maßen okay sind, aber bei Häufung KI signalisieren (inkl. Nominalstil-Marker wie "Fragestellung", "Zielsetzung")
- **Tier 3 (BEOBACHTEN):** 35 Wörter die nur im Cluster verdächtig werden (inkl. Anglizismen wie "Benchmark", "Use Case", "Impact")
- **Verbotene Phrasen:** 48 Phrasen die sofort raus müssen ("Es ist wichtig zu beachten", "In der heutigen Welt", "Vor dem Hintergrund")

Plus **7 Co-Occurrence-Sets** – Wort-Cluster die gemeinsam auftreten und KI-Herkunft verraten (inkl. Anglizismen-Cluster und Nominalstil-Cluster).

### 5 Statistische Signale

| Signal | Was es misst |
|--------|-------------|
| Burstiness | Variation der Satzabstände (KI schreibt gleichmäßig) |
| Type-Token-Ratio | Wortschatz-Vielfalt pro 100-Wort-Fenster |
| Satzlängen-CoV | Variation der Satzlängen (KI = monoton) |
| Trigramm-Wiederholung | Wiederholte 3-Wort-Folgen |
| Flesch-DE | Lesbarkeit (KI-Texte landen oft im Sweetspot 40–50) |

### Personality Injection

5 Techniken machen Texte menschlicher: Einschübe, Rhythmuswechsel, Mini-Abschweifungen, Unsicherheitsmarker und Umgangssprache-Tupfer. Der Skill wählt je nach Kontext (formal vs. locker) die passende Mischung.

### Stil-Layer

- **Basis:** Neutrale Humanisierung ohne besonderen Stil. Funktioniert für jeden Text.
- **Lesch:** Inspiriert vom Erklärstil von Harald Lesch – Tonwechsel (Visionär/Mahner/Erklärer), Analogien, philosophische Anker.

---

## CLI-Tool (optional, Subset)

Im Ordner `scripts/` liegt ein Node.js CLI-Tool fuer schnelle Analysen **ohne KI**. Das CLI implementiert einen Teil der Analyse: Tier-1/2-Vokabelcheck, Phrasenersetzung und statistische Signale. Die vollstaendige 5-Durchgangs-Analyse mit allen 24 KI-Mustern und Personality Injection laeuft ueber den OpenClaw-Agent (SKILL.md).

```bash
node humanize-de.js score   < mein-text.txt
node humanize-de.js analyze < mein-text.txt
node humanize-de.js suggest < mein-text.txt
```

Nur `fs` und `path` als Dependencies – kein Netzwerk, keine externen Pakete.

---

## Kalibrierung

Getestet an 7+ Texten in Session 46–47:

| Texttyp | Score-Bereich | Erwartung | Ergebnis |
|---------|---------------|-----------|----------|
| Menschlich geschrieben | 0–8 | 0–30 | Passt |
| Lesch-Stil (KI-bereinigt) | 2–6 | 0–30 | Passt |
| Subtiler KI-Text | 42 | 30–60 ("Gemischt") | Passt |
| Typischer ChatGPT-Text | 64–92 | 60–100 | Passt |
| Offensichtlicher KI-Text | 98 | 60–100 | Passt |

---

## Dateistruktur

```
humanizer-de/
├── _meta.json                          Skill-Metadaten
├── README.md                           Diese Datei
├── SKILL.md                            Hauptlogik & Workflow
├── references/
│   ├── ki-muster.md                    24 KI-Schreibmuster (deutsch)
│   ├── vokabeln.md                     168 KI-Vokabeln & Phrasen in 3 Tiers
│   ├── statistische-signale.md         5 statistische Signale mit Formeln
│   ├── personality-injection.md        5 Humanisierungs-Techniken
│   ├── examples.md                     6 Vorher/Nachher-Transformationen
│   └── stil-layer/
│       ├── basis.md                    Standard-Humanisierung
│       └── lesch.md                    Lesch-Erweiterung
└── scripts/
    └── humanize-de.js                  Node.js CLI-Tool (960 Zeilen)
```

---

## Teil des OpenClaw-Projekts

Dieser Skill ist eigenständig nutzbar – du brauchst kein Buch und kein Dashboard.

Wenn du mehr willst: Der Skill ist Teil des **OpenClaw Sachbuch-Projekts** ("Agentic Authorship"), das erklärt wie man KI-Agenten baut, betreibt und qualitätssichert. Das Buch nutzt den Humanizer selbst für die eigene Textqualität.

- Dashboard: https://tikitackr.github.io/OpenClaw-Dashboard/
- Cowan (mobiler Buch-Begleiter): https://tikitackr.github.io/Cowan/

---

## Lizenz

MIT – mach damit was du willst. Wenn du ihn verbesserst, teil es gern auf ClawHub.
