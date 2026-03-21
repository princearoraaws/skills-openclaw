#!/usr/bin/env node

/**
 * humanize-de.js – Deutscher KI-Text-Detektor (CLI)
 *
 * Befehle:
 *   score <datei>     Berechnet den KI-Score (0-100)
 *   analyze <datei>   Detaillierte Analyse mit allen Signalen
 *   suggest <datei>   Zeigt Ersetzungsvorschläge
 *   fix <datei>       Automatische Tier-1-Ersetzungen (schreibt neue Datei)
 *
 * Nur fs und path als Dependencies. Kein Netzwerk. Alles lokal.
 *
 * Autor: OpenClaw
 * Lizenz: MIT
 */

const fs = require('fs');
const path = require('path');

// ============================================================
//  DATENBANKEN
// ============================================================

/**
 * Tier 1 – VERBOTEN (immer ersetzen, +3 Punkte pro Treffer)
 * Format: [KI-Wort, Ersetzungsvorschlag]
 */
const TIER1 = [
  ['grundlegend', 'wichtig'],
  ['nahtlos', 'reibungslos'],
  ['robust', 'stabil'],
  ['skalierbar', 'erweiterbar'],
  ['ganzheitlich', 'umfassend'],
  ['bahnbrechend', 'wichtig'],
  ['wegweisend', 'einflussreich'],
  ['transformativ', 'verändernd'],
  ['synergetisch', 'ergänzend'],
  ['facettenreich', 'vielseitig'],
  ['Eckpfeiler', 'Basis'],
  ['Katalysator', 'Antrieb'],
  ['ermächtigen', 'befähigen'],
  ['unschätzbar', 'sehr wertvoll'],
  ['eingebettet', 'integriert'],
  ['Tapisserie', 'Geflecht'],
  ['Wandteppich', 'Geflecht'],
  ['herausragend', 'stark'],
  ['maßgeblich', 'stark'],
  ['tiefgreifend', 'spürbar'],
  ['hochgradig', 'sehr'],
  ['zweifellos', 'sicher'],
  ['unbestreitbar', 'klar'],
  ['Paradigmenwechsel', 'Umdenken'],
  ['unverzichtbar', 'nötig'],
  ['überwältigend', 'stark'],
  ['federführend', 'führend'],
  ['richtungsweisend', 'wichtig'],
  ['Meilenstein', 'wichtiger Schritt'],
  ['Wendepunkt', 'Umbruch'],
  ['Schlüsselrolle', 'wichtige Rolle'],
  ['Vorreiter', 'Pionier'],
  ['zukunftsweisend', 'vorausschauend'],
  ['beispiellos', 'einmalig'],
  ['außerordentlich', 'besonders'],
];

/**
 * Tier 2 – SPARSAM (max 1x pro 500 Wörter, +1 Punkt über Limit)
 */
const TIER2 = [
  'darüber hinaus', 'des Weiteren', 'zudem', 'nuanciert',
  'erleichtern', 'beleuchten', 'umfassen', 'proaktiv',
  'wesentlich', 'darauf abzielen', 'in der Lage sein',
  'ermöglichen', 'gewährleisten', 'berücksichtigen',
  'Aspekt', 'Kontext', 'relevant', 'optimieren',
  'implementieren', 'integrieren', 'adressieren',
  'transparent', 'signifikant', 'elementar', 'essenziell',
  'komplex', 'Potenzial', 'effektiv', 'effizient',
  // Erweiterung v1.1 (Session 48)
  'nutzerorientiert', 'datengetrieben', 'zukunftsfähig',
  'evidenzbasiert', 'praxiserprobt', 'niedrigschwellig',
  'Handlungsempfehlung', 'Zielsetzung', 'Fragestellung',
  'Problemstellung', 'Herangehensweise', 'Gegebenheiten',
  'fungieren', 'aufweisen', 'darstellen', 'verorten',
];

/**
 * Verbotene Phrasen (+4 Punkte pro Treffer)
 */
const VERBOTENE_PHRASEN = [
  'es ist wichtig zu beachten',
  'nicht nur... sondern auch',
  'nicht nur',
  'in der heutigen welt',
  'in einer welt, in der',
  'in einer welt in der',
  'lass uns ehrlich sein',
  'um ehrlich zu sein',
  'darüber hinaus',
  'des weiteren',
  'ermöglicht es',
  'bietet die möglichkeit',
  'grundlegend anders',
  'im kern',
  'im grunde',
  'zusammenfassend lässt sich sagen',
  'es lässt sich festhalten',
  'abschließend sei gesagt',
  'wie bereits erwähnt',
  'an dieser stelle sei erwähnt',
  'es sei darauf hingewiesen',
  'in anbetracht der tatsache',
  'aufgrund der tatsache',
  'im folgenden wird erläutert',
  'es gilt zu beachten',
  'nicht zuletzt',
  'zu guter letzt',
  'last but not least',
  // Erweiterung v1.1 (Session 48)
  'in diesem zusammenhang',
  'vor dem hintergrund',
  'im rahmen von',
  'unter berücksichtigung',
  'es zeigt sich, dass',
  'es zeigt sich dass',
  'es wird deutlich, dass',
  'es wird deutlich dass',
  'eine vielzahl von',
  'eine reihe von',
  'einen wesentlichen beitrag',
  'im hinblick auf',
  'hinsichtlich',
  'dies unterstreicht',
  'es bleibt abzuwarten',
  'es bleibt spannend',
  'die zukunft wird zeigen',
  'spielt eine entscheidende rolle',
  'von entscheidender bedeutung',
  'stellt einen wichtigen schritt dar',
];

/**
 * Chatbot-Artefakte (+5 Punkte pro Treffer)
 */
const CHATBOT_ARTEFAKTE = [
  'tolle frage',
  'gute frage',
  'hervorragende frage',
  'ausgezeichnete frage',
  'ich hoffe, das hilft',
  'ich hoffe das hilft',
  'lass mich wissen',
  'lassen sie mich wissen',
  'gerne!',
  'natürlich!',
  'selbstverständlich!',
  'da haben sie völlig recht',
  'da hast du völlig recht',
  'stand meiner letzten schulung',
  'soweit mir bekannt',
  'zum zeitpunkt meines wissens',
];

// ============================================================
//  HILFSFUNKTIONEN
// ============================================================

/**
 * Text in Sätze aufteilen (einfache Heuristik)
 */
function splitSentences(text) {
  // Sätze an . ! ? trennen, aber nicht bei Abkürzungen wie "z.B." oder "etc."
  const raw = text.replace(/([.!?])\s+/g, '$1\n').split('\n');
  return raw
    .map(s => s.trim())
    .filter(s => s.length > 0 && s.split(/\s+/).length >= 1);
}

/**
 * Wörter aus Text extrahieren (lowercase, ohne Satzzeichen)
 */
function tokenize(text) {
  return text
    .toLowerCase()
    .replace(/[^\wäöüß\s-]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 0);
}

/**
 * Standardabweichung berechnen
 */
function stddev(arr) {
  const n = arr.length;
  if (n === 0) return 0;
  const mean = arr.reduce((a, b) => a + b, 0) / n;
  const variance = arr.reduce((sum, val) => sum + (val - mean) ** 2, 0) / n;
  return Math.sqrt(variance);
}

/**
 * Mittelwert berechnen
 */
function mean(arr) {
  if (arr.length === 0) return 0;
  return arr.reduce((a, b) => a + b, 0) / arr.length;
}

// ============================================================
//  ANALYSE-FUNKTIONEN
// ============================================================

/**
 * Tier-1-Wörter finden
 */
function findTier1(text) {
  const lower = text.toLowerCase();
  const hits = [];
  for (const [word, replacement] of TIER1) {
    const regex = new RegExp(word.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
    let match;
    while ((match = regex.exec(lower)) !== null) {
      hits.push({
        word: word,
        replacement: replacement,
        position: match.index,
        tier: 1,
      });
    }
  }
  return hits;
}

/**
 * Tier-2-Wörter finden und Dichte prüfen
 */
function findTier2(text) {
  const lower = text.toLowerCase();
  const wordCount = tokenize(text).length;
  const maxAllowed = Math.max(1, Math.floor(wordCount / 500));
  const hits = [];

  for (const word of TIER2) {
    const regex = new RegExp(word.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
    let count = 0;
    let match;
    while ((match = regex.exec(lower)) !== null) {
      count++;
      if (count > maxAllowed) {
        hits.push({
          word: word,
          position: match.index,
          tier: 2,
          count: count,
          maxAllowed: maxAllowed,
        });
      }
    }
  }
  return hits;
}

/**
 * Verbotene Phrasen finden
 */
function findVerbotenePhrasen(text) {
  const lower = text.toLowerCase();
  const hits = [];
  for (const phrase of VERBOTENE_PHRASEN) {
    const regex = new RegExp(phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
    let match;
    while ((match = regex.exec(lower)) !== null) {
      hits.push({
        phrase: phrase,
        position: match.index,
      });
    }
  }
  return hits;
}

/**
 * Chatbot-Artefakte finden
 */
function findChatbotArtefakte(text) {
  const lower = text.toLowerCase();
  const hits = [];
  for (const artifact of CHATBOT_ARTEFAKTE) {
    if (lower.includes(artifact)) {
      hits.push({ artifact: artifact });
    }
  }
  return hits;
}

/**
 * Burstiness berechnen
 */
function calcBurstiness(sentences) {
  if (sentences.length < 20) return { value: null, note: 'Zu wenige Sätze (<20)' };
  const lengths = sentences.map(s => tokenize(s).length);
  const m = mean(lengths);
  const s = stddev(lengths);
  if (s + m === 0) return { value: 0, note: 'Alle Sätze gleich lang' };
  return { value: (s - m) / (s + m) };
}

/**
 * Type-Token-Ratio berechnen (gleitendes 100-Wort-Fenster)
 */
function calcTTR(text) {
  const tokens = tokenize(text);
  if (tokens.length < 50) return { value: null, note: 'Zu wenige Wörter (<50)' };

  const windowSize = 100;
  const ttrs = [];

  for (let i = 0; i <= tokens.length - windowSize; i += 50) {
    const window = tokens.slice(i, i + windowSize);
    const unique = new Set(window);
    ttrs.push(unique.size / window.length);
  }

  if (ttrs.length === 0) {
    const unique = new Set(tokens);
    return { value: unique.size / tokens.length };
  }

  return { value: mean(ttrs) };
}

/**
 * Satzlängen-CoV berechnen
 */
function calcCoV(sentences) {
  if (sentences.length < 5) return { value: null, note: 'Zu wenige Sätze (<5)' };
  const lengths = sentences.map(s => tokenize(s).length);
  const m = mean(lengths);
  if (m === 0) return { value: 0 };
  const s = stddev(lengths);
  return { value: s / m };
}

/**
 * Trigramm-Wiederholung berechnen
 */
function calcTrigramRepeat(text) {
  const sentences = splitSentences(text);
  const trigramCounts = {};
  let totalTrigrams = 0;

  for (const sentence of sentences) {
    const tokens = tokenize(sentence);
    for (let i = 0; i < tokens.length - 2; i++) {
      const trigram = `${tokens[i]} ${tokens[i + 1]} ${tokens[i + 2]}`;
      trigramCounts[trigram] = (trigramCounts[trigram] || 0) + 1;
      totalTrigrams++;
    }
  }

  if (totalTrigrams === 0) return { value: 0 };

  const repeated = Object.values(trigramCounts).filter(c => c > 1).length;
  return { value: repeated / totalTrigrams };
}

/**
 * Deutsche Silbenzählung (vereinfacht)
 */
function countSyllablesDE(word) {
  word = word.toLowerCase().replace(/[^a-zäöüß]/g, '');
  if (word.length <= 2) return 1;

  // Diphthonge als 1 Silbe zählen
  let processed = word
    .replace(/ei/g, 'X')
    .replace(/ai/g, 'X')
    .replace(/au/g, 'X')
    .replace(/eu/g, 'X')
    .replace(/äu/g, 'X')
    .replace(/ie/g, 'X');

  const vowels = processed.match(/[aeiouäöüX]/g);
  return vowels ? Math.max(1, vowels.length) : 1;
}

/**
 * Flesch-DE Lesbarkeit berechnen
 */
function calcFleschDE(text) {
  const sentences = splitSentences(text);
  const tokens = tokenize(text);
  if (sentences.length < 3 || tokens.length < 30) {
    return { value: null, note: 'Zu wenig Text für Flesch-Berechnung' };
  }

  const totalSyllables = tokens.reduce((sum, w) => sum + countSyllablesDE(w), 0);
  const avgSentenceLength = tokens.length / sentences.length;
  const avgSyllablesPerWord = totalSyllables / tokens.length;

  // Deutsche Flesch-Formel
  const flesch = 180 - avgSentenceLength - (58.5 * avgSyllablesPerWord);
  return { value: Math.max(0, Math.min(100, flesch)) };
}

/**
 * Co-Occurrence-Sets prüfen (Wort-Cluster in Absätzen)
 */
const CO_OCCURRENCE_SETS = [
  // Set 1: Bedeutungs-Aufblasung
  ['grundlegend', 'maßgeblich', 'entscheidend', 'tiefgreifend', 'bahnbrechend',
   'wegweisend', 'meilenstein', 'wendepunkt', 'paradigmenwechsel'],
  // Set 2: Werbesprache
  ['nahtlos', 'robust', 'skalierbar', 'ganzheitlich', 'umfassend',
   'herausragend', 'innovativ', 'zukunftsweisend'],
  // Set 3: Abstrakte Metaphern
  ['landschaft', 'eckpfeiler', 'katalysator', 'facettenreich',
   'tapisserie', 'eingebettet', 'ökosystem'],
  // Set 4: Aktions-Verben
  ['ermächtigen', 'befähigen', 'ermöglichen', 'gewährleisten',
   'erleichtern', 'optimieren', 'implementieren', 'integrieren'],
  // Set 5: Übergangs-Füller
  ['darüber hinaus', 'des weiteren', 'zudem', 'nicht zuletzt',
   'abschließend', 'zusammenfassend', 'im folgenden'],
  // Set 6: Anglizismen-Cluster (v1.1)
  ['benchmark', 'best practice', 'use case', 'alignment', 'empowerment',
   'impact', 'leverage', 'onboarding', 'upskilling', 'gamechanger'],
  // Set 7: Nominalstil-Cluster (v1.1)
  ['zielsetzung', 'fragestellung', 'problemstellung',
   'handlungsempfehlung', 'herangehensweise', 'gegebenheiten'],
];

function findCoOccurrences(text) {
  // Absätze trennen
  const paragraphs = text.split(/\n\s*\n/).filter(p => p.trim().length > 0);
  const alarms = [];

  for (let pi = 0; pi < paragraphs.length; pi++) {
    const lower = paragraphs[pi].toLowerCase();
    for (let si = 0; si < CO_OCCURRENCE_SETS.length; si++) {
      const matches = CO_OCCURRENCE_SETS[si].filter(word => lower.includes(word));
      if (matches.length >= 3) {
        alarms.push({
          paragraph: pi + 1,
          set: si + 1,
          matches: matches,
          count: matches.length,
        });
      }
    }
  }
  return alarms;
}

/**
 * Personality-Bonus berechnen
 */
function calcPersonalityBonus(text) {
  let bonus = 0;
  const details = [];

  // Einschübe in Klammern
  const klammerMatches = text.match(/\([^)]{5,60}\)/g);
  if (klammerMatches && klammerMatches.length > 0) {
    bonus -= 3;
    details.push(`Einschübe in Klammern: ${klammerMatches.length}x (-3)`);
  }

  // Satzrhythmus prüfen
  const sentences = splitSentences(text);
  const lengths = sentences.map(s => tokenize(s).length);
  let monotone = false;
  for (let i = 0; i < lengths.length - 2; i++) {
    if (Math.abs(lengths[i] - lengths[i + 1]) < 3 &&
        Math.abs(lengths[i + 1] - lengths[i + 2]) < 3) {
      monotone = true;
      break;
    }
  }
  if (!monotone && sentences.length >= 5) {
    bonus -= 5;
    details.push('Satzrhythmus variiert (-5)');
  }

  // Kontraktionen
  const kontraktionen = text.match(/\b(gibt's|ist's|hat's|geht's|war's|kann's|muss's|werd's|wär's|hätt's)\b/gi);
  if (kontraktionen && kontraktionen.length > 0) {
    bonus -= 2;
    details.push(`Kontraktionen: ${kontraktionen.length}x (-2)`);
  }

  // Konkrete Zahlen
  const zahlen = text.match(/\d+[.,]?\d*\s*(%|€|\$|Prozent|Euro|Dollar|Stunden|Tage|Wochen|Monate|Jahre)/g);
  if (zahlen && zahlen.length >= 2) {
    bonus -= 3;
    details.push(`Konkrete Zahlen/Einheiten: ${zahlen.length}x (-3)`);
  }

  // Satzfragmente (Sätze unter 4 Wörtern)
  const fragmente = sentences.filter(s => tokenize(s).length <= 3 && tokenize(s).length > 0);
  if (fragmente.length > 0) {
    bonus -= 2;
    details.push(`Satzfragmente: ${fragmente.length}x (-2)`);
  }

  return { bonus, details };
}

// ============================================================
//  SCORE-BERECHNUNG
// ============================================================

function calculateScore(text) {
  let score = 0;
  const report = {
    tier1: [],
    tier2: [],
    phrasen: [],
    chatbot: [],
    statistik: {},
    coOccurrence: [],
    personality: {},
    details: [],
  };

  // Tier 1
  const t1 = findTier1(text);
  report.tier1 = t1;
  score += t1.length * 3;
  if (t1.length > 0) report.details.push(`Tier-1-Wörter: ${t1.length}x (+${t1.length * 3})`);

  // Tier 2
  const t2 = findTier2(text);
  report.tier2 = t2;
  score += t2.length * 1;
  if (t2.length > 0) report.details.push(`Tier-2-Überschuss: ${t2.length}x (+${t2.length})`);

  // Verbotene Phrasen
  const vp = findVerbotenePhrasen(text);
  report.phrasen = vp;
  score += vp.length * 4;
  if (vp.length > 0) report.details.push(`Verbotene Phrasen: ${vp.length}x (+${vp.length * 4})`);

  // Chatbot-Artefakte
  const ca = findChatbotArtefakte(text);
  report.chatbot = ca;
  score += ca.length * 5;
  if (ca.length > 0) report.details.push(`Chatbot-Artefakte: ${ca.length}x (+${ca.length * 5})`);

  // Statistik
  const sentences = splitSentences(text);

  const burstiness = calcBurstiness(sentences);
  report.statistik.burstiness = burstiness;
  if (burstiness.value !== null && burstiness.value < 0.3) {
    score += 10;
    report.details.push(`Burstiness: ${burstiness.value.toFixed(3)} (<0.3 → +10)`);
  }

  const ttr = calcTTR(text);
  report.statistik.ttr = ttr;
  if (ttr.value !== null && ttr.value < 0.5) {
    score += 5;
    report.details.push(`TTR: ${ttr.value.toFixed(3)} (<0.5 → +5)`);
  }

  const cov = calcCoV(sentences);
  report.statistik.cov = cov;
  if (cov.value !== null && cov.value < 0.3) {
    score += 5;
    report.details.push(`CoV: ${cov.value.toFixed(3)} (<0.3 → +5)`);
  }

  const trigram = calcTrigramRepeat(text);
  report.statistik.trigram = trigram;
  if (trigram.value > 0.10) {
    score += 5;
    report.details.push(`Trigramm-Rate: ${trigram.value.toFixed(3)} (>0.10 → +5)`);
  }

  // Flesch-DE (Signal 5)
  const flesch = calcFleschDE(text);
  report.statistik.flesch = flesch;
  if (flesch.value !== null && flesch.value >= 40 && flesch.value <= 50) {
    score += 3;
    report.details.push(`Flesch-DE: ${flesch.value.toFixed(1)} (KI-Sweetspot 40–50 → +3)`);
  }

  // Co-Occurrence-Sets
  const coOcc = findCoOccurrences(text);
  report.coOccurrence = coOcc;
  if (coOcc.length > 0) {
    const coOccScore = coOcc.length * 5;
    score += coOccScore;
    report.details.push(`Co-Occurrence-Alarm: ${coOcc.length} Cluster (+${coOccScore})`);
  }

  // Personality Bonus
  const personality = calcPersonalityBonus(text);
  report.personality = personality;
  score += personality.bonus;

  // Clamp
  score = Math.max(0, Math.min(100, score));
  report.score = score;

  return report;
}

// ============================================================
//  BEWERTUNG
// ============================================================

function getBewertung(score) {
  if (score <= 20) return 'Klingt menschlich';
  if (score <= 40) return 'Leicht maschinell';
  if (score <= 60) return 'Gemischt';
  if (score <= 80) return 'Offensichtlich KI';
  return 'ChatGPT-Standard';
}

// ============================================================
//  OUTPUT-FORMATIERUNG
// ============================================================

function formatScore(report) {
  const bewertung = getBewertung(report.score);
  return `\n  SCORE: ${report.score} / 100  →  ${bewertung}\n`;
}

function formatAnalyze(report, text) {
  const lines = [];
  const wordCount = tokenize(text).length;
  const sentenceCount = splitSentences(text).length;

  lines.push('');
  lines.push('═══════════════════════════════════════════');
  lines.push('  HUMANIZER-DE · Analyse-Report');
  lines.push('═══════════════════════════════════════════');
  lines.push('');
  lines.push(`  SCORE: ${report.score} / 100  →  ${getBewertung(report.score)}`);
  lines.push(`  Wörter: ${wordCount} | Sätze: ${sentenceCount}`);
  lines.push('');

  // Tier 1
  lines.push('───────────────────────────────────────────');
  lines.push(`  1. TIER-1-WÖRTER (${report.tier1.length} gefunden, +${report.tier1.length * 3} Pkt)`);
  lines.push('───────────────────────────────────────────');
  if (report.tier1.length === 0) {
    lines.push('  Keine Tier-1-Wörter gefunden. Gut!');
  } else {
    // Deduplizieren
    const seen = new Set();
    for (const hit of report.tier1) {
      const key = hit.word.toLowerCase();
      if (!seen.has(key)) {
        seen.add(key);
        const count = report.tier1.filter(h => h.word.toLowerCase() === key).length;
        lines.push(`  ▸ "${hit.word}" (${count}x) → "${hit.replacement}"`);
      }
    }
  }
  lines.push('');

  // Verbotene Phrasen
  lines.push('───────────────────────────────────────────');
  lines.push(`  2. VERBOTENE PHRASEN (${report.phrasen.length} gefunden, +${report.phrasen.length * 4} Pkt)`);
  lines.push('───────────────────────────────────────────');
  if (report.phrasen.length === 0) {
    lines.push('  Keine verbotenen Phrasen gefunden. Gut!');
  } else {
    const seen = new Set();
    for (const hit of report.phrasen) {
      if (!seen.has(hit.phrase)) {
        seen.add(hit.phrase);
        lines.push(`  ▸ "${hit.phrase}"`);
      }
    }
  }
  lines.push('');

  // Chatbot-Artefakte
  if (report.chatbot.length > 0) {
    lines.push('───────────────────────────────────────────');
    lines.push(`  3. CHATBOT-ARTEFAKTE (${report.chatbot.length} gefunden, +${report.chatbot.length * 5} Pkt)`);
    lines.push('───────────────────────────────────────────');
    for (const hit of report.chatbot) {
      lines.push(`  ▸ "${hit.artifact}"`);
    }
    lines.push('');
  }

  // Statistik
  lines.push('───────────────────────────────────────────');
  lines.push('  4. STATISTIK');
  lines.push('───────────────────────────────────────────');

  const b = report.statistik.burstiness;
  if (b.value !== null) {
    const status = b.value >= 0.3 ? '✓ menschlich' : '✗ KI-typisch';
    lines.push(`  Burstiness:       ${b.value.toFixed(3)}  ${status}`);
  } else {
    lines.push(`  Burstiness:       – (${b.note})`);
  }

  const t = report.statistik.ttr;
  if (t.value !== null) {
    const status = t.value >= 0.5 ? '✓ menschlich' : '✗ KI-typisch';
    lines.push(`  TTR:              ${t.value.toFixed(3)}  ${status}`);
  } else {
    lines.push(`  TTR:              – (${t.note})`);
  }

  const c = report.statistik.cov;
  if (c.value !== null) {
    const status = c.value >= 0.3 ? '✓ menschlich' : '✗ KI-typisch';
    lines.push(`  Satzlängen-CoV:   ${c.value.toFixed(3)}  ${status}`);
  } else {
    lines.push(`  Satzlängen-CoV:   – (${c.note})`);
  }

  const tr = report.statistik.trigram;
  const trStatus = tr.value <= 0.10 ? '✓ normal' : '✗ KI-typisch';
  lines.push(`  Trigramm-Rate:    ${tr.value.toFixed(3)}  ${trStatus}`);

  const fl = report.statistik.flesch;
  if (fl && fl.value !== null) {
    const flStatus = (fl.value >= 40 && fl.value <= 50) ? '✗ KI-Sweetspot' : '✓ ok';
    lines.push(`  Flesch-DE:        ${fl.value.toFixed(1)}   ${flStatus}`);
  } else if (fl) {
    lines.push(`  Flesch-DE:        – (${fl.note})`);
  }
  lines.push('');

  // Co-Occurrence
  if (report.coOccurrence && report.coOccurrence.length > 0) {
    lines.push('───────────────────────────────────────────');
    lines.push(`  4b. CO-OCCURRENCE-ALARM (${report.coOccurrence.length} Cluster, +${report.coOccurrence.length * 5} Pkt)`);
    lines.push('───────────────────────────────────────────');
    for (const alarm of report.coOccurrence) {
      lines.push(`  ▸ Absatz ${alarm.paragraph}, Set ${alarm.set}: ${alarm.matches.join(', ')} (${alarm.count} Treffer)`);
    }
    lines.push('');
  }

  // Personality
  lines.push('───────────────────────────────────────────');
  lines.push(`  5. PERSONALITY-BONUS (${report.personality.bonus} Pkt)`);
  lines.push('───────────────────────────────────────────');
  if (report.personality.details.length === 0) {
    lines.push('  Keine menschlichen Stilmittel erkannt.');
  } else {
    for (const d of report.personality.details) {
      lines.push(`  ▸ ${d}`);
    }
  }
  lines.push('');

  // Score-Aufschlüsselung
  lines.push('───────────────────────────────────────────');
  lines.push('  6. SCORE-DETAILS');
  lines.push('───────────────────────────────────────────');
  for (const d of report.details) {
    lines.push(`  ▸ ${d}`);
  }
  lines.push('');
  lines.push('═══════════════════════════════════════════');

  return lines.join('\n');
}

function formatSuggest(report) {
  const lines = [];
  lines.push('');
  lines.push('  ERSETZUNGSVORSCHLÄGE');
  lines.push('  ────────────────────');

  if (report.tier1.length === 0 && report.phrasen.length === 0) {
    lines.push('  Keine Ersetzungen nötig!');
    return lines.join('\n');
  }

  // Tier 1
  const seen = new Set();
  for (const hit of report.tier1) {
    const key = hit.word.toLowerCase();
    if (!seen.has(key)) {
      seen.add(key);
      lines.push(`  "${hit.word}" → "${hit.replacement}"`);
    }
  }

  // Phrasen
  for (const hit of report.phrasen) {
    lines.push(`  "${hit.phrase}" → [streichen oder umschreiben]`);
  }

  lines.push('');
  return lines.join('\n');
}

// ============================================================
//  FIX-FUNKTION
// ============================================================

function fixText(text) {
  let fixed = text;

  // Tier-1-Wörter ersetzen
  for (const [word, replacement] of TIER1) {
    const regex = new RegExp(`\\b${word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
    fixed = fixed.replace(regex, replacement);
  }

  // Verbotene Phrasen ersetzen (die einfachen Fälle)
  const phrasenReplace = [
    ['es ist wichtig zu beachten, dass ', ''],
    ['es ist wichtig zu beachten dass ', ''],
    ['darüber hinaus ', 'Außerdem '],
    ['des weiteren ', 'Außerdem '],
    ['aufgrund der tatsache, dass ', 'Weil '],
    ['aufgrund der tatsache dass ', 'Weil '],
    ['in anbetracht der tatsache, dass ', 'Da '],
    ['in anbetracht der tatsache dass ', 'Da '],
    ['zusammenfassend lässt sich sagen, dass ', ''],
    ['zusammenfassend lässt sich sagen dass ', ''],
    ['es lässt sich festhalten, dass ', ''],
    ['es lässt sich festhalten dass ', ''],
    ['im folgenden wird erläutert', ''],
    ['es gilt zu beachten, dass ', ''],
    ['es gilt zu beachten dass ', ''],
    ['wie bereits erwähnt ', ''],
    ['nicht zuletzt ', 'Außerdem '],
    ['zu guter letzt ', 'Zum Schluss: '],
    ['last but not least ', 'Und: '],
  ];

  for (const [phrase, replacement] of phrasenReplace) {
    const regex = new RegExp(phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
    fixed = fixed.replace(regex, replacement);
  }

  return fixed;
}

// ============================================================
//  CLI
// ============================================================

function printUsage() {
  console.log(`
  humanize-de.js – Deutscher KI-Text-Detektor

  Verwendung:
    node humanize-de.js score <datei>     Score (0-100)
    node humanize-de.js analyze <datei>   Detaillierte Analyse
    node humanize-de.js suggest <datei>   Ersetzungsvorschläge
    node humanize-de.js fix <datei>       Auto-Fix (schreibt <datei>.fixed.md)

  Score-Skala:
    0-20   Klingt menschlich
    21-40  Leicht maschinell
    41-60  Gemischt
    61-80  Offensichtlich KI
    81-100 ChatGPT-Standard
  `);
}

function main() {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    printUsage();
    process.exit(1);
  }

  const command = args[0];
  const filePath = args[1];

  // Datei lesen
  if (!fs.existsSync(filePath)) {
    console.error(`  Fehler: Datei nicht gefunden: ${filePath}`);
    process.exit(1);
  }

  const text = fs.readFileSync(filePath, 'utf-8');

  if (text.trim().length === 0) {
    console.error('  Fehler: Datei ist leer.');
    process.exit(1);
  }

  // Markdown-Formatierung entfernen (nur Text analysieren)
  const cleanText = text
    .replace(/^#+\s.*/gm, '')          // Überschriften entfernen
    .replace(/^\s*[-*]\s/gm, '')       // Bullet Points entfernen
    .replace(/\*\*([^*]+)\*\*/g, '$1') // Fett entfernen
    .replace(/\*([^*]+)\*/g, '$1')     // Kursiv entfernen
    .replace(/`[^`]+`/g, '')           // Inline-Code entfernen
    .replace(/```[\s\S]*?```/g, '')    // Code-Blöcke entfernen
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Links entfernen
    .replace(/^\s*>\s/gm, '')          // Blockquotes entfernen
    .replace(/^\s*\|.*\|.*$/gm, '')    // Tabellen entfernen
    .replace(/---+/g, '')              // Horizontale Linien entfernen
    .replace(/\n{3,}/g, '\n\n')        // Mehrfache Leerzeilen reduzieren
    .trim();

  const report = calculateScore(cleanText);

  switch (command) {
    case 'score':
      console.log(formatScore(report));
      break;

    case 'analyze':
      console.log(formatAnalyze(report, cleanText));
      break;

    case 'suggest':
      console.log(formatSuggest(report));
      break;

    case 'fix': {
      const fixed = fixText(text);
      const ext = path.extname(filePath);
      const base = path.basename(filePath, ext);
      const dir = path.dirname(filePath);
      const outPath = path.join(dir, `${base}.fixed${ext}`);
      fs.writeFileSync(outPath, fixed, 'utf-8');

      // Score vorher/nachher
      const reportBefore = calculateScore(cleanText);
      const fixedClean = fixed
        .replace(/^#+\s.*/gm, '')
        .replace(/\*\*([^*]+)\*\*/g, '$1')
        .replace(/`[^`]+`/g, '')
        .replace(/```[\s\S]*?```/g, '')
        .trim();
      const reportAfter = calculateScore(fixedClean);

      console.log(`
  Fix angewendet!
  ────────────────
  Vorher:  ${reportBefore.score} / 100
  Nachher: ${reportAfter.score} / 100
  Differenz: ${reportBefore.score - reportAfter.score} Punkte verbessert

  Gespeichert: ${outPath}
      `);
      break;
    }

    default:
      console.error(`  Unbekannter Befehl: ${command}`);
      printUsage();
      process.exit(1);
  }
}

main();
