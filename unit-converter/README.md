# Unit Converter

An offline Python 3.10+ console application with ten measurement categories,
conversion history, CSV export, and batch conversion. No third-party packages required.

## Run

Install Python 3.10 or later from python.org if needed. Open a terminal in this folder:

```sh
python unit_converter.py
python unit_converter.py convert length 1 mi km
python unit_converter.py convert temperature 32 F C
python unit_converter.py units
python unit_converter.py batch example_batch.csv batch_results.csv
python -m unittest discover -s tests -v
```

On Windows, `py` can be used instead of `python` if the Python launcher is installed.
Batch exit code 1 means at least one row was rejected; 2 indicates a file or validation
failure. The supplied batch deliberately contains two invalid rows to demonstrate errors.

## Features

- Length, mass, temperature, area, volume, time, speed, data, pressure, and energy.
- Convert between two units or from one unit to every unit in its category.
- Find units by symbol or full singular name; matching ignores case.
- List the conversion scales and offsets used by the engine.
- Track successful conversions during the session and export them to CSV.
- Process CSV rows independently, writing errors beside rejected rows.
- Reject invalid numbers, incompatible units, infinity, numeric overflow, negative
  quantities, and temperatures below absolute zero.
- Choose 1–15 significant digits for display. CSV retains Python float precision.
- Cancel an interactive action with q; exit cleanly on EOF or Ctrl+C.

## Design

`Unit`, `Category`, and `Record` are immutable data classes. `Converter` owns the
conversion rules and history; `ConsoleApp` owns the menu and input/output. Both the
menu and command-line interface use the same engine.

Each unit maps to a shared base: `base = value * source.scale + source.offset`.
Then `result = (base - target.offset) / target.scale`. Temperature uses offsets;
other categories use a zero offset. This avoids maintaining a separate formula for
every possible unit pair. Lookup is linear in the small tuple of units per category.
Batch processing reads the input rows into memory before writing output.

See [rubric alignment](docs/RUBRIC_ALIGNMENT.md), [demo guide](docs/DEMO_GUIDE.md),
and [GitHub setup](docs/GITHUB_SETUP.md).

## Limits

Results use floating-point arithmetic and may have small rounding errors. Negative
non-temperature quantities are intentionally rejected. Pressure is absolute, not gauge.
Volume units are US liquid measures, not Imperial. `cal` means thermochemical calorie;
`kcal` means 1000 cal. kB/MB/GB are decimal; KiB/MiB/GiB are binary.
History is in memory and disappears on exit unless exported. CSV output replaces an
existing destination file. This educational tool is not intended for precision-critical
engineering calculations. No currency conversion or online rates are included.

## Authorship and references

The implementation was generated with assistance from OpenAI Codex for this request;
no third-party converter source was copied. Review and understand the code and disclose
assistance as your course requires. Generated code does not establish that 400 lines
were written by the student group; confirm that requirement with your instructor.

Reference material for reviewing units and Python concepts:

- Python standard library: https://docs.python.org/3/library/
- NIST Guide to the SI: https://www.nist.gov/pml/special-publication-811
- NIST binary prefixes: https://physics.nist.gov/cuu/Units/binary.html

These are reference links, not a claim that the pages were consulted during generation.
The two supplied assignment documents were used as grading criteria.
