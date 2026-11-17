import csv
import io
import math
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from unit_converter import Converter, ConversionError, ConsoleApp, main


class ConverterTests(unittest.TestCase):
    def setUp(self):
        self.engine = Converter()

    def test_known_values(self):
        cases = [
            ('length', 1, 'mi', 'km', 1.609344),
            ('mass', 1, 'lb', 'kg', .45359237),
            ('temperature', 32, 'F', 'C', 0),
            ('temperature', 100, 'C', 'F', 212),
            ('temperature', -273.15, 'C', 'K', 0),
            ('temperature', -459.67, 'F', 'K', 0),
            ('area', 1, 'acre', 'm2', 4046.8564224),
            ('volume', 1, 'gal_us', 'L', 3.785411784),
            ('time', 1, 'day', 'h', 24),
            ('speed', 36, 'km/h', 'm/s', 10),
            ('data', 1, 'KiB', 'B', 1024),
            ('data', 1, 'kB', 'bit', 8000),
            ('pressure', 1, 'atm', 'Pa', 101325),
            ('energy', 1, 'kcal', 'J', 4184),
        ]
        for category, value, source, target, expected in cases:
            with self.subTest(category=category, source=source):
                self.assertAlmostEqual(self.engine.convert(category, value, source, target).result, expected)

    def test_every_pair_round_trip(self):
        for category in self.engine.categories.values():
            for source in category.units:
                for target in category.units:
                    with self.subTest(category=category.name, source=source.symbol, target=target.symbol):
                        forward = self.engine.convert(category.name, 300, source.symbol, target.symbol, False)
                        back = self.engine.convert(category.name, forward.result, target.symbol, source.symbol, False)
                        self.assertTrue(math.isclose(back.result, 300, rel_tol=1e-9, abs_tol=1e-8))
        self.assertEqual(self.engine.history, [])

    def test_invalid_inputs_do_not_change_history(self):
        cases = [('bogus', 1, 'm', 'ft'), ('length', 1, 'm', 'kg'),
                 ('length', -1, 'm', 'ft'), ('length', 'abc', 'm', 'ft'),
                 ('length', 'nan', 'm', 'ft'), ('length', 'inf', 'm', 'ft'),
                 ('length', 1e308, 'km', 'mm'), ('temperature', -1, 'K', 'C')]
        for args in cases:
            with self.subTest(args=args), self.assertRaises(ConversionError):
                self.engine.convert(*args)
        self.assertEqual(self.engine.history, [])

    def test_search_aliases_all_and_history(self):
        self.assertTrue(self.engine.search('meter'))
        self.assertFalse(self.engine.search('does-not-exist'))
        self.assertEqual(self.engine.convert(' LENGTH ', '1e3', 'meter', 'km').result, 1)
        rows = self.engine.convert_all('temperature', '0', 'C')
        self.assertEqual(len(rows), 3)
        self.assertEqual(len(self.engine.history), 4)

    def test_export_and_batch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, target = root / 'input.csv', root / 'output.csv'
            source.write_text('category,value,source,target\nlength,1,km,m\ntemperature,-1,K,C\n', encoding='utf-8')
            self.assertEqual(self.engine.batch(source, target), (1, 1))
            with target.open(newline='', encoding='utf-8') as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(float(rows[0]['result']), 1000)
            self.assertIn('absolute zero', rows[1]['error'])
            self.assertEqual(self.engine.export_history(root / 'history.csv'), 1)
            with self.assertRaises(ConversionError):
                self.engine.batch(source, source)
            source.write_text('bad,header\n1,2\n', encoding='utf-8')
            with self.assertRaises(ConversionError):
                self.engine.batch(source, target)

    def test_cli_and_menu_recovery(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(['convert', 'length', '1', 'km', 'm']), 0)
            with patch('builtins.input', side_effect=['bad', '1', 'length', 'm', 'abc', 'ft', '0']):
                ConsoleApp(self.engine).run()
        self.assertIn('1000 m', output.getvalue())
        self.assertIn('Error:', output.getvalue())
        self.assertIn('Goodbye', output.getvalue())


if __name__ == '__main__':
    unittest.main()
