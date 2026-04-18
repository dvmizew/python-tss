# Testare unitară în Python

## Descrierea aplicației

Aplicația este un utilitar Python care redenumește automat fișiere audio pe baza tagurilor stocate în acestea (titlu, artist, număr de track), după formatul `NN - Titlu.ext`.

## Clasa testată

Pentru ilustrarea strategiilor de testare am ales clasa `TrackNumberParser` din modulul `audio_utils.py`. Aceasta este responsabilă de parsarea și manipularea numerelor de track ale fișierelor audio și conține trei metode: `parse()`, `format_track()` și `pad_track()`.

## Configurație

Proiectul a fost dezvoltat și testat pe trei sisteme diferite. Mai jos sunt prezentate configurațiile hardware și software utilizate de fiecare membru al echipei.

| Membru | OS | Procesor | RAM |
|--------|-----|----------|-----|
| Radu Daniel | ... | ... | ... |
| Roman Bianca | Ubuntu 24.04 | Intel Core i7-1255U (12th Gen) | 16 GB |
| Costache Carolina | ... | ... | ... |

Versiunile tool-urilor utilizate sunt identice pe toate sistemele:
- Python 3.12.3
- pytest 9.0.3
- pytest-cov 7.1.0
- pytest-mock 3.15.1
- mutagen 1.47.0

## Strategii de testare

### 1. Partiționare în clase de echivalență

#### `parse()`

Metoda primește un string cu numărul de track și returnează un tuplu de două valori întregi: numărul curent și totalul. Dacă inputul este invalid, returnează `(None, None)`.

| Clasă | Descriere | Input reprezentativ | Output așteptat |
|-------|-----------|-------------------|-----------------|
| C1 | Input gol sau None | `None`, `""` | `(None, None)` |
| C2 | Număr simplu valid | `"5"` | `(5, None)` |
| C3 | Număr cu total valid | `"5/12"` | `(5, 12)` |
| C4 | String invalid fără cifre | `"ABC"` | `(None, None)` |

**C1 — input gol sau None:**
```python
def test_parse_empty_string(self):
    current, total = TrackNumberParser.parse("")
    assert current is None
    assert total is None

def test_parse_none(self):
    current, total = TrackNumberParser.parse(None)
    assert current is None
    assert total is None
```

**C2 — număr simplu valid:**
```python
def test_parse_single_digit(self):
    current, total = TrackNumberParser.parse("5")
    assert current == 5
    assert total is None
```

**C3 — număr cu total valid:**
```python
def test_parse_normal_track_with_total(self):
    current, total = TrackNumberParser.parse("5/12")
    assert current == 5
    assert total == 12
```

**C4 — string invalid fără cifre:**
```python
def test_parse_non_numeric(self):
    current, total = TrackNumberParser.parse("ABC")
    assert current is None
    assert total is None
```

#### `format_track()`

Metoda primește numărul curent de track și opțional totalul, returnând un string formatat. Dacă totalul este furnizat, returnează formatul `"current/total"`, altfel returnează doar numărul ca string.

| Clasă | Descriere | Input | Output așteptat |
|-------|-----------|-------|-----------------|
| C1 | Fără total | `(5)` | `"5"` |
| C2 | Cu total | `(5, 12)` | `"5/12"` |

**C1 — fără total:**
```python
def test_format_without_total(self):
    result = TrackNumberParser.format_track(5)
    assert result == "5"
```

**C2 — cu total:**
```python
def test_format_with_total(self):
    result = TrackNumberParser.format_track(5, 12)
    assert result == "5/12"
```

#### `pad_track()`

Metoda primește un număr întreg și returnează un string cu zero adăugat în față dacă numărul este mai mic de 10.

| Clasă | Descriere | Input | Output așteptat |
|-------|-----------|-------|-----------------|
| C1 | Număr cu o cifră | `5` | `"05"` |
| C2 | Număr cu două cifre | `12` | `"12"` |

**C1 — număr cu o cifră:**
```python
def test_pad_single_digit(self):
    result = TrackNumberParser.pad_track(5)
    assert result == "05"
```

**C2 — număr cu două cifre:**
```python
def test_pad_double_digit(self):
    result = TrackNumberParser.pad_track(12)
    assert result == "12"
```

### 2. Analiza valorilor de frontieră

Analiza valorilor de frontieră este o metodă complementară partiționării în clase de echivalență, care se concentrează pe testarea valorilor exact la limita dintre clase, unde de obicei apar cele mai multe erori.

#### `parse()`

Frontierele identificate pentru metoda `parse()` sunt:

| Valoare de frontieră | Descriere | Input | Output așteptat |
|---------------------|-----------|-------|-----------------|
| Track zero fără total | Cel mai mic număr valid posibil | `"0"` | `(0, None)` |
| Track zero cu total | Cel mai mic track cu total | `"0/1"` | `(0, 1)` |
| Track egal cu total | Limita superioară normală | `"12/12"` | `(12, 12)` |
| Track mai mare ca total | Dincolo de limita superioară normală | `"15/10"` | `(15, 10)` |
| Doar separator | Fără cifre, doar `/` | `"/"` | `(None, None)` |

```python
def test_parse_zero_without_total(self):
    """BVA: Zero without total - lowest valid single number."""
    current, total = TrackNumberParser.parse("0")
    assert current == 0
    assert total is None

def test_parse_track_zero(self):
    """BVA: Track 0 with total."""
    current, total = TrackNumberParser.parse("0/1")
    assert current == 0
    assert total == 1

def test_parse_same_track_and_total(self):
    """BVA: Track = Total."""
    current, total = TrackNumberParser.parse("12/12")
    assert current == 12
    assert total == 12

def test_parse_track_exceeds_total(self):
    """BVA: Track number > total."""
    current, total = TrackNumberParser.parse("15/10")
    assert current == 15
    assert total == 10

def test_parse_only_separator(self):
    """BVA: Only separator, no digits."""
    current, total = TrackNumberParser.parse("/")
    assert current is None
    assert total is None
```

#### `format_track()`

Metoda primește numărul curent de track și opțional totalul, returnând un string formatat. Dacă totalul este furnizat, returnează formatul `"current/total"`, altfel returnează doar numărul ca string.

| Valoare de frontieră | Descriere | Input | Output așteptat |
|---------------------|-----------|-------|-----------------|
| Zero fără total | Limita inferioară fără total | `(0)` | `"0"` |
| Zero cu total zero | Limita inferioară cu total | `(0, 0)` | `"0/0"` |
| Unu fără total | Primul track normal fără total | `(1)` | `"1"` |
| Unu cu total unu | Cel mai mic track cu total | `(1, 1)` | `"1/1"` |

```python
def test_format_zero_without_total(self):
    """BVA: Zero without total - lowest possible value."""
    result = TrackNumberParser.format_track(0)
    assert result == "0"

def test_format_zero_with_zero_total(self):
    """BVA: Zero with zero total."""
    result = TrackNumberParser.format_track(0, 0)
    assert result == "0/0"

def test_format_one_without_total(self):
    """BVA: First normal track without total."""
    result = TrackNumberParser.format_track(1)
    assert result == "1"

def test_format_track_one_of_one(self):
    """BVA: Minimum track with total."""
    result = TrackNumberParser.format_track(1, 1)
    assert result == "1/1"
```

#### `pad_track()`

Metoda primește un număr întreg și returnează un string cu zero adăugat în față dacă numărul este mai mic de 10. Frontiera dintre cele două comportamente este exact la 9 și 10.

| Valoare de frontieră | Descriere | Input | Output așteptat |
|---------------------|-----------|-------|-----------------|
| Zero | Cel mai mic număr posibil | `0` | `"00"` |
| 9 | Ultimul număr cu o cifră | `9` | `"09"` |
| 10 | Primul număr cu două cifre | `10` | `"10"` |
| 99 | Număr mare cu două cifre | `99` | `"99"` |

```python
def test_pad_zero(self):
    """BVA: Zero."""
    result = TrackNumberParser.pad_track(0)
    assert result == "00"

def test_pad_nine(self):
    """BVA: Last single digit number."""
    result = TrackNumberParser.pad_track(9)
    assert result == "09"

def test_pad_ten(self):
    """BVA: First double digit number."""
    result = TrackNumberParser.pad_track(10)
    assert result == "10"

def test_pad_99(self):
    """BVA: Large double digit number."""
    result = TrackNumberParser.pad_track(99)
    assert result == "99"
```