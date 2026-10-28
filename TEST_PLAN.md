# Testplan – Weather Data

Grundlage: README und Docstrings in `weather.py`. Eine eigene `SPECIFICATION.md` gibt es im Repository nicht.

Legende: **N** = Normalfall, **G** = Grenzwert, **S** = Spezialfall, **U** = ungültige Eingabe, **E** = Seiteneffekt

## `parse_time(time_text)`

| Klasse | Fall | Erwartung |
|---|---|---|
| N | `"14:21"` | 861 |
| G | `"00:00"` | 0 |
| G | `"23:59"` | 1439 |
| G | `"00:59"`, `"01:00"` | 59, 60 (Stunde mal 60 plus Minute) |
| U | `"24:00"`, `"25:00"` | `ValueError` (Stunde zu groß) |
| U | `"12:60"`, `"12:99"` | `ValueError` (Minute zu groß) |
| U | `"-1:30"`, `"12:-5"` | `ValueError` (Vorzeichen) |
| U | `"1430"` | `ValueError` (kein Doppelpunkt) |
| U | `"12:30:45"` | `ValueError` (zu viele Teile) |
| U | `""`, `":"`, `"12:"`, `":30"` | `ValueError` (leere Teile) |
| U | `"ab:cd"`, `"1a:30"`, `"12:3x"` | `ValueError` (nicht numerisch) |
| U | `"12.5:30"` | `ValueError` |

## `parse_measurement(line)`

| Klasse | Fall | Erwartung |
|---|---|---|
| N | `"Köln;14:21;21.7"` | `("Köln", 861, 21.7)` |
| S | negative Temperatur `-5.5` | `-5.5` |
| S | ganzzahlige Temperatur `"20"` | `20.0` als `float` |
| S | Leerzeichen um alle Felder | werden entfernt |
| S | Stadt mit Leerzeichen innen (`"Bad Honnef"`) | bleibt erhalten |
| G | Zeit `00:00` und `23:59` | richtig umgerechnet |
| U | Eingabe ist kein String (`None`, `123`, `["a"]`) | `ValueError` |
| U | zu wenige Felder (`"Köln;14:21"`, `""`) | `ValueError` |
| U | zu viele Felder (`"Köln;14:21;21.7;x"`, Semikolon am Ende) | `ValueError` |
| U | leere Stadt (`";14:21;1.0"`, `"   ;14:21;1.0"`) | `ValueError` |
| U | ungültige Zeit (`"Köln;25:00;1.0"`) | `ValueError` |
| U | Temperatur leer oder nicht numerisch (`"abc"`, `""`) | `ValueError` |

## `filter_by_temperature(measurements, lower, upper)`

| Klasse | Fall | Erwartung |
|---|---|---|
| N | Werte teils innerhalb, teils außerhalb | nur die inneren |
| G | Temperatur genau `lower` | enthalten |
| G | Temperatur genau `upper` | enthalten |
| G | knapp unter `lower` und knapp über `upper` | nicht enthalten |
| G | `lower == upper` | nur exakte Treffer, kein Fehler |
| S | leere Liste | `[]` |
| S | kein Treffer | `[]` |
| S | negative Bereiche | richtig gefiltert |
| S | Reihenfolge der Eingabe | bleibt erhalten |
| S | Dubletten | bleiben beide erhalten |
| U | `lower > upper` | `ValueError` |
| E | Eingabeliste | bleibt unverändert |
| E | Ergebnis | ist eine neue Liste |

## `average_temperature(measurements, city)`

| Klasse | Fall | Erwartung |
|---|---|---|
| N | zwei Messungen einer Stadt | Mittelwert |
| S | andere Städte im Datensatz | werden ignoriert |
| S | genau eine Messung | dieser Wert |
| S | drei Werte, nicht ganzzahliger Mittelwert | Summe geteilt durch Anzahl (nicht durch alle Messungen) |
| S | negative und positive Werte | richtig gemittelt |
| S | Schreibweise (`"köln"` statt `"Köln"`) | kein Treffer, `ValueError` |
| U | Stadt nicht vorhanden | `ValueError` |
| U | leere Liste | `ValueError` |
| E | Eingabe | bleibt unverändert |

## `hottest_measurement(measurements)`

| Klasse | Fall | Erwartung |
|---|---|---|
| N | eindeutiges Maximum in der Mitte | dieses |
| G | Maximum an erster Stelle | dieses |
| G | Maximum an letzter Stelle | dieses |
| G | genau eine Messung | diese |
| S | Gleichstand, früherer Eintrag hat frühere Zeit | früherer Eintrag |
| S | Gleichstand, späterer Eintrag hat frühere Zeit | späterer Eintrag |
| S | Gleichstand bei mehr als zwei Einträgen | früheste Zeit |
| S | Gleichstand bei verschiedenen Städten | früheste Zeit |
| S | nur negative Temperaturen | höchste (am wenigsten negative) |
| U | leere Liste | `ValueError` |
| E | Eingabe | bleibt unverändert |

## Ergänzungen nach `SPECIFICATION.md`

- `parse_time`: Führende Nullen sind optional, `"9:05"`, `"09:05"` und `"9:5"` sind gültig (N/S).
- `hottest_measurement`: Gleiche Temperatur und gleiche Uhrzeit: die zuerst vorkommende Messung gewinnt (S).
- `average_temperature`: Groß- und Kleinschreibung der Stadt zählt, das ist jetzt Spezifikation und keine Annahme mehr.

## Bewusst nicht getestet

- `"nan"` und `"inf"` als Temperatur: `float()` akzeptiert sie, die Spezifikation verlangt keine Plausibilitätsprüfung.
- Andere falsche Typen als Strings bei `parse_measurement` jenseits des Tests auf `ValueError`.
