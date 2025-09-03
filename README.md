
# 🔍 Log Analyzer
Questo tool python consente di evidenziare eventi sospetti o critici nei file di log utilizzando **Pattern regex** definiti in un file JSON esterno.  
L’output è leggibile a console e, se richiesto, può essere esportato in un file CSV.

---

## ✨ Funzionalità principali
- Analisi di file di log tramite **regex personalizzabili**
- Evidenziazione eventi con **colori e livelli di severità**
- Estrazione automatica di **IP, utenti e porte**
- Ordinamento cronologico degli eventi
- Possibilità di esportazione report in **CSV**
- Modalità per mostrare solo eventi critici o **tutti i log**

---

## 📂 Struttura del progetto
```
.
├── log_analyzer.py
├── patterns
│   └── default.json
└── reports/   (creata automaticamente)
```

- `log_analyzer.py` → lo script principale  
- `patterns/default.json` → file contenente le regex e la configurazione dei colori/severità  
- `reports/` → cartella dove vengono salvati i report in CSV  

---

### Requisiti
- Python 3.x
- Librerie: `pandas`, `colorama`, `tabulate`

Puoi installare manualmente le dipendenze con:
```bash
pip install pandas colorama tabulate
```

---

## 🚀 Utilizzo

Esegui lo script passando il file di log da analizzare:
```bash
python log_analyzer.py /var/log/auth.log
```

Mostrare **tutti i log**, inclusi quelli normali:
```bash
python log_analyzer.py /var/log/auth.log --all
```

Salvare un **report CSV**:
```bash
python log_analyzer.py /var/log/auth.log --report
```

Combinare entrambe le opzioni:
```bash
python log_analyzer.py /var/log/auth.log -a -r
```

---

## 📝 Esempio di `default.json`
Il file `patterns/default.json` definisce gli eventi da cercare con regex.  
Ogni evento ha: `pattern`, `color`, `severity`.

```json
{
  "SSH Failed Password": {
    "pattern": "Failed password for (?P<user>\S+) from (?P<ip>\d+\.\d+\.\d+\.\d+) port (?P<port>\d+)",
    "color": "RED",
    "severity": "high"
  },
  "SSH Accepted Password": {
    "pattern": "Accepted password for (?P<user>\S+) from (?P<ip>\d+\.\d+\.\d+\.\d+) port (?P<port>\d+)",
    "color": "GREEN",
    "severity": "medium"
  }
}
```

---

## 📊 Output di esempio

Esempio di tabella in console:

```
+---------------------+----------------------+--------+---------------+-------+------------------------------------------------------------+
| Timestamp           | Event                | User   | IP            | Port  | Log                                                        |
+=====================+======================+========+===============+=======+============================================================+
| 2025-09-03 16:41:22 | SSH Failed Password  | root   | 203.0.113.14  | 54872 | Sep  3 16:41:22 server sshd[1234]: Failed password for ... |
+---------------------+----------------------+--------+---------------+-------+------------------------------------------------------------+
| 2025-09-03 16:43:01 | SSH Accepted Password| gigi   | 198.51.100.5  | 51432 | Sep  3 16:43:01 server sshd[1337]: Accepted password for.. |
+---------------------+----------------------+--------+---------------+-------+------------------------------------------------------------+
```

Gli eventi sono colorati a seconda della severità.

---

## ⚠️ Limiti e considerazioni
- Il parsing del timestamp presuppone log in formato `Mese Giorno Ora:min:sec` (es. `Sep 03 16:41:22`).
- Le regex vengono valutate in ordine: la prima che corrisponde viene applicata.
- Se i log hanno formati diversi, è necessario adattare il file `default.json`.
- La colorazione funziona solo su terminali che supportano escape ANSI.

---
