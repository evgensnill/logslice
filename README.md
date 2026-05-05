# logslice

Fast log file parser and filter utility with regex and time-range support.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/youruser/logslice.git && cd logslice && pip install .
```

---

## Usage

```bash
# Filter log lines matching a pattern
logslice --file app.log --pattern "ERROR"

# Filter by time range
logslice --file app.log --start "2024-01-15 08:00:00" --end "2024-01-15 09:00:00"

# Combine regex and time range
logslice --file app.log --pattern "WARN|ERROR" --start "2024-01-15 08:00:00" --end "2024-01-15 09:00:00"

# Output results to a file
logslice --file app.log --pattern "CRITICAL" --output results.log
```

You can also use logslice as a library:

```python
from logslice import LogParser

parser = LogParser("app.log")
results = parser.filter(pattern=r"ERROR", start="2024-01-15 08:00:00")

for line in results:
    print(line)
```

---

## Features

- ⚡ Fast line-by-line streaming — handles large log files with low memory usage
- 🔍 Full regex pattern support
- 🕐 Time-range filtering with flexible timestamp formats
- 📤 Output to stdout or file

---

## License

This project is licensed under the [MIT License](LICENSE).