"""Unit Converter: an offline, standard-library Python course project."""
from __future__ import annotations

import argparse
import csv
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


class ConversionError(ValueError):
    """A user-facing conversion or validation failure."""


@dataclass(frozen=True)
class Unit:
    """Map a unit to its category's base: base = value * scale + offset."""
    symbol: str
    name: str
    scale: float
    offset: float = 0.0

    def to_base(self, value: float) -> float:
        return value * self.scale + self.offset

    def from_base(self, value: float) -> float:
        return (value - self.offset) / self.scale


@dataclass(frozen=True)
class Category:
    name: str
    base: str
    units: tuple[Unit, ...]
    allow_negative: bool = False

    def find_unit(self, text: str) -> Unit:
        for unit in self.units:
            if text.strip().casefold() in (unit.symbol.casefold(), unit.name.casefold()):
                return unit
        raise ConversionError(f"Unknown {self.name} unit: {text!r}")


@dataclass(frozen=True)
class Record:
    timestamp: str
    category: str
    value: float
    source: str
    target: str
    result: float

    def row(self) -> tuple:
        return (self.timestamp, self.category, self.value,
                self.source, self.target, self.result)

    def describe(self, precision: int = 8) -> str:
        return (f"{self.value:.{precision}g} {self.source} = "
                f"{self.result:.{precision}g} {self.target} ({self.category})")


def build_categories() -> dict[str, Category]:
    """Use SI bases, international inch/pound, and explicitly US liquid volume."""
    categories = (
        Category("length", "m", (
            Unit("mm", "millimeter", 0.001),
            Unit("cm", "centimeter", 0.01),
            Unit("m", "meter", 1.0),
            Unit("km", "kilometer", 1000.0),
            Unit("in", "inch", 0.0254),
            Unit("ft", "foot", 0.3048),
            Unit("yd", "yard", 0.9144),
            Unit("mi", "mile", 1609.344),
            Unit("nmi", "nautical mile", 1852.0),
        )),
        Category("mass", "kg", (
            Unit("mg", "milligram", 0.000001),
            Unit("g", "gram", 0.001),
            Unit("kg", "kilogram", 1.0),
            Unit("t", "metric tonne", 1000.0),
            Unit("oz", "ounce", 0.028349523125),
            Unit("lb", "pound", 0.45359237),
            Unit("st", "stone", 6.35029318),
        )),
        Category("temperature", "K", (
            Unit("C", "celsius", 1.0, 273.15),
            Unit("F", "fahrenheit", 5.0 / 9.0, 273.15 - 32.0 * 5.0 / 9.0),
            Unit("K", "kelvin", 1.0),
        ), True),
        Category("area", "m2", (
            Unit("cm2", "square centimeter", 0.0001),
            Unit("m2", "square meter", 1.0),
            Unit("km2", "square kilometer", 1000000.0),
            Unit("ha", "hectare", 10000.0),
            Unit("in2", "square inch", 0.00064516),
            Unit("ft2", "square foot", 0.09290304),
            Unit("acre", "acre", 4046.8564224),
        )),
        Category("volume", "L", (
            Unit("mL", "milliliter", 0.001),
            Unit("L", "liter", 1.0),
            Unit("m3", "cubic meter", 1000.0),
            Unit("tsp_us", "US teaspoon", 0.00492892159375),
            Unit("tbsp_us", "US tablespoon", 0.01478676478125),
            Unit("cup_us", "US cup", 0.2365882365),
            Unit("pt_us", "US pint", 0.473176473),
            Unit("qt_us", "US quart", 0.946352946),
            Unit("gal_us", "US gallon", 3.785411784),
        )),
        Category("time", "s", (
            Unit("ms", "millisecond", 0.001),
            Unit("s", "second", 1.0),
            Unit("min", "minute", 60.0),
            Unit("h", "hour", 3600.0),
            Unit("day", "day", 86400.0),
            Unit("week", "week", 604800.0),
        )),
        Category("speed", "m/s", (
            Unit("m/s", "meters per second", 1.0),
            Unit("km/h", "kilometers per hour", 1.0 / 3.6),
            Unit("mph", "miles per hour", 0.44704),
            Unit("ft/s", "feet per second", 0.3048),
            Unit("kn", "knot", 1852.0 / 3600.0),
        )),
        Category("data", "B", (
            Unit("bit", "bit", 0.125),
            Unit("B", "byte", 1.0),
            Unit("kB", "kilobyte", 1000.0),
            Unit("MB", "megabyte", 1000000.0),
            Unit("GB", "gigabyte", 1000000000.0),
            Unit("KiB", "kibibyte", 1024.0),
            Unit("MiB", "mebibyte", 1048576.0),
            Unit("GiB", "gibibyte", 1073741824.0),
        )),
        Category("pressure", "Pa", (
            Unit("Pa", "pascal", 1.0),
            Unit("kPa", "kilopascal", 1000.0),
            Unit("bar", "bar", 100000.0),
            Unit("atm", "standard atmosphere", 101325.0),
            Unit("psi", "pounds per square inch", 6894.757293168),
        )),
        Category("energy", "J", (
            Unit("J", "joule", 1.0),
            Unit("kJ", "kilojoule", 1000.0),
            Unit("cal", "thermochemical calorie", 4.184),
            Unit("kcal", "thermochemical kilocalorie", 4184.0),
            Unit("Wh", "watt hour", 3600.0),
            Unit("kWh", "kilowatt hour", 3600000.0),
        )),
    )
    return {category.name: category for category in categories}


class Converter:
    """Conversion engine shared by interactive and command-line interfaces."""
    def __init__(self) -> None:
        self.categories = build_categories()
        self.history: list[Record] = []

    def category(self, name: str) -> Category:
        key = name.strip().casefold()
        if key not in self.categories:
            raise ConversionError(f"Unknown category: {name!r}")
        return self.categories[key]

    @staticmethod
    def parse_number(text: str | float) -> float:
        try:
            value = float(text)
        except (ValueError, TypeError, OverflowError) as error:
            raise ConversionError("Enter a number, such as 12.5 or 1e3.") from error
        if not math.isfinite(value):
            raise ConversionError("NaN and infinity are not supported.")
        return value

    def convert(self, category_name: str, value: str | float,
                source_name: str, target_name: str,
                remember: bool = True) -> Record:
        category = self.category(category_name)
        source = category.find_unit(source_name)
        target = category.find_unit(target_name)
        number = self.parse_number(value)
        if number < 0 and not category.allow_negative:
            raise ConversionError("This category requires a nonnegative quantity.")
        base_value = source.to_base(number)
        if category.name == "temperature":
            if base_value < -1e-10:
                raise ConversionError("Temperature cannot be below absolute zero.")
            base_value = max(0.0, base_value)
        result = target.from_base(base_value)
        if not math.isfinite(base_value) or not math.isfinite(result):
            raise ConversionError("The converted value exceeds floating-point range.")
        record = Record(datetime.now(timezone.utc).isoformat(), category.name,
                        number, source.symbol, target.symbol, result)
        if remember:
            self.history.append(record)
        return record

    def convert_all(self, category_name: str, value: str,
                    source_name: str) -> list[Record]:
        category = self.category(category_name)
        records = [self.convert(category.name, value, source_name, unit.symbol, False)
                   for unit in category.units]
        self.history.extend(records)
        return records

    def search(self, query: str) -> list[tuple[str, Unit]]:
        query = query.strip().casefold()
        return [(category.name, unit)
                for category in self.categories.values()
                for unit in category.units
                if query in unit.name.casefold() or query in unit.symbol.casefold()]

    def export_history(self, path: Path) -> int:
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(("timestamp", "category", "value", "source", "target", "result"))
            for record in self.history:
                writer.writerow(record.row())
        return len(self.history)

    def batch(self, input_path: Path, output_path: Path) -> tuple[int, int]:
        if input_path.resolve() == output_path.resolve():
            raise ConversionError("Input and output CSV paths must be different.")
        with input_path.open(newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            required = {"category", "value", "source", "target"}
            if not required.issubset(set(reader.fieldnames or [])):
                raise ConversionError("CSV needs category,value,source,target columns.")
            rows = list(reader)
        successes = 0
        failures = 0
        with output_path.open("w", newline="", encoding="utf-8") as stream:
            fields = ("category", "value", "source", "target", "result", "error")
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                output = {key: row.get(key, "") for key in fields[:4]}
                try:
                    record = self.convert(row["category"], row["value"],
                                          row["source"], row["target"])
                    output["result"] = record.result
                    output["error"] = ""
                    successes += 1
                except ConversionError as error:
                    output["result"] = ""
                    output["error"] = str(error)
                    failures += 1
                writer.writerow(output)
        return successes, failures


class ConsoleApp:
    """Friendly looping console interface; q cancels any input prompt."""
    def __init__(self, converter: Converter) -> None:
        self.converter = converter
        self.precision = 8
        self.running = True
        self.actions = {
            "1": self.single_conversion,
            "2": self.all_units,
            "3": self.list_units,
            "4": self.search_units,
            "5": self.show_history,
            "6": self.export_history,
            "7": self.batch_conversion,
            "8": self.change_precision,
            "9": self.clear_history,
            "0": self.stop,
        }

    @staticmethod
    def ask(prompt: str) -> str:
        value = input(prompt).strip()
        if value.casefold() == "q":
            raise ConversionError("Action cancelled.")
        if not value:
            raise ConversionError("An input is required.")
        return value

    def choose_category(self) -> Category:
        names = tuple(self.converter.categories)
        for index, name in enumerate(names, 1):
            print(f"  {index:2}. {name}")
        answer = self.ask("Category name or number: ")
        if answer.isdecimal():
            index = int(answer) - 1
            if not 0 <= index < len(names):
                raise ConversionError("Category number is out of range.")
            answer = names[index]
        return self.converter.category(answer)

    @staticmethod
    def print_units(category: Category) -> None:
        print(f"\n{category.name.title()} units (base: {category.base})")
        for unit in category.units:
            print(f"  {unit.symbol:10} {unit.name}")

    def get_conversion_inputs(self) -> tuple[Category, str, str]:
        category = self.choose_category()
        self.print_units(category)
        source = self.ask("From unit symbol or full name: ")
        value = self.ask("Value: ")
        return category, source, value

    def single_conversion(self) -> None:
        category, source, value = self.get_conversion_inputs()
        target = self.ask("To unit symbol or full name: ")
        record = self.converter.convert(category.name, value, source, target)
        print("Result:", record.describe(self.precision))

    def all_units(self) -> None:
        category, source, value = self.get_conversion_inputs()
        records = self.converter.convert_all(category.name, value, source)
        for record in records:
            print(record.describe(self.precision))

    def list_units(self) -> None:
        category = self.choose_category()
        self.print_units(category)
        print("Formula: base = value * source scale + source offset")
        print("Result = (base - target offset) / target scale")
        for unit in category.units:
            print(f"  {unit.symbol}: scale={unit.scale:.12g}, offset={unit.offset:.12g}")

    def search_units(self) -> None:
        query = self.ask("Search unit name or symbol: ")
        matches = self.converter.search(query)
        if not matches:
            print("No matching units.")
            return
        for category, unit in matches:
            print(f"  {category:12} {unit.symbol:10} {unit.name}")
        print(f"{len(matches)} match(es).")

    def show_history(self) -> None:
        if not self.converter.history:
            print("No conversions yet.")
            return
        for index, record in enumerate(self.converter.history, 1):
            print(f"{index:3}. {record.describe(self.precision)}")
        print(f"Total: {len(self.converter.history)} conversion(s).")

    def export_history(self) -> None:
        if not self.converter.history:
            print("Nothing to export yet.")
            return
        path = Path(self.ask("Output CSV path (existing files are replaced): ")).expanduser()
        count = self.converter.export_history(path)
        print(f"Exported {count} conversion(s) to {path}.")

    def batch_conversion(self) -> None:
        print("Required CSV header: category,value,source,target")
        source = Path(self.ask("Input CSV path: ")).expanduser()
        target = Path(self.ask("Output CSV path (existing files are replaced): ")).expanduser()
        successes, failures = self.converter.batch(source, target)
        print(f"Batch finished: {successes} converted, {failures} rejected.")
        print(f"Results and row errors: {target}")

    def change_precision(self) -> None:
        text = self.ask("Significant digits (1-15): ")
        try:
            precision = int(text)
        except ValueError as error:
            raise ConversionError("Precision must be an integer.") from error
        if not 1 <= precision <= 15:
            raise ConversionError("Choose between 1 and 15 digits.")
        self.precision = precision
        print(f"Display precision set to {precision} significant digits.")

    def clear_history(self) -> None:
        answer = self.ask("Type YES to clear this session's history: ")
        if answer == "YES":
            self.converter.history.clear()
            print("History cleared.")
        else:
            print("History kept.")

    def stop(self) -> None:
        self.running = False
        print("Goodbye! Export history before exiting if you want to keep it.")

    @staticmethod
    def print_menu() -> None:
        print("\n=== UNIT CONVERTER ===")
        print("1. Convert between two units")
        print("2. Convert to every unit in a category")
        print("3. List units and formulas")
        print("4. Search units")
        print("5. View session history")
        print("6. Export history to CSV")
        print("7. Batch convert a CSV file")
        print("8. Set display precision")
        print("9. Clear session history")
        print("0. Exit | q cancels an action")

    def run(self) -> None:
        print("Offline converter | US liquid volumes | decimal and binary data units")
        while self.running:
            self.print_menu()
            try:
                choice = input("Choose an option: ").strip()
                action = self.actions.get(choice)
                if action is None:
                    print("Choose an option from 0 through 9.")
                    continue
                action()
            except (ConversionError, OSError, csv.Error) as error:
                print(f"Error: {error}")
            except (EOFError, KeyboardInterrupt):
                print("\nSession ended.")
                self.running = False


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command")
    convert = subparsers.add_parser("convert", help="Convert one value")
    convert.add_argument("category")
    convert.add_argument("value")
    convert.add_argument("source")
    convert.add_argument("target")
    convert.add_argument("--precision", type=int, default=8, choices=range(1, 16))
    listing = subparsers.add_parser("units", help="List available units")
    listing.add_argument("category", nargs="?")
    batch = subparsers.add_parser("batch", help="Convert CSV rows")
    batch.add_argument("input", type=Path)
    batch.add_argument("output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    converter = Converter()
    try:
        if args.command == "convert":
            record = converter.convert(args.category, args.value, args.source, args.target)
            print(record.describe(args.precision))
        elif args.command == "units":
            if args.category:
                ConsoleApp.print_units(converter.category(args.category))
            else:
                for category in converter.categories.values():
                    ConsoleApp.print_units(category)
        elif args.command == "batch":
            successes, failures = converter.batch(args.input, args.output)
            print(f"Converted: {successes}; rejected: {failures}; output: {args.output}")
            return 1 if failures else 0
        else:
            ConsoleApp(converter).run()
    except (ConversionError, OSError, csv.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
