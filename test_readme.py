"""
test_readme.py — Unit tests for readme.py visitor counter
==========================================================
Run with:
    python -m pytest test_readme.py -v
or simply:
    python test_readme.py
"""

import json
import os
import tempfile
import unittest

from readme import load_count, save_count, increment_and_get, print_visitor_count


class TestLoadCount(unittest.TestCase):
    """Tests for load_count()."""

    def test_returns_zero_when_file_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "nonexistent.json")
            self.assertEqual(load_count(path), 0)

    def test_reads_existing_count(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                        delete=False) as fh:
            json.dump({"visitors": 42}, fh)
            path = fh.name
        try:
            self.assertEqual(load_count(path), 42)
        finally:
            os.unlink(path)

    def test_returns_zero_on_corrupt_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                        delete=False) as fh:
            fh.write("not valid json{{")
            path = fh.name
        try:
            self.assertEqual(load_count(path), 0)
        finally:
            os.unlink(path)


class TestSaveCount(unittest.TestCase):
    """Tests for save_count()."""

    def test_creates_file_with_correct_value(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "count.json")
            save_count(7, path)
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self.assertEqual(data["visitors"], 7)

    def test_overwrites_existing_value(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "count.json")
            save_count(1, path)
            save_count(99, path)
            self.assertEqual(load_count(path), 99)


class TestIncrementAndGet(unittest.TestCase):
    """Tests for increment_and_get()."""

    def test_starts_at_one_from_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "count.json")
            result = increment_and_get(path)
            self.assertEqual(result, 1)

    def test_increments_sequentially(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "count.json")
            for expected in range(1, 6):
                self.assertEqual(increment_and_get(path), expected)

    def test_persists_between_calls(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "count.json")
            increment_and_get(path)   # 1
            increment_and_get(path)   # 2
            increment_and_get(path)   # 3
            self.assertEqual(load_count(path), 3)


class TestPrintVisitorCount(unittest.TestCase):
    """Tests for print_visitor_count()."""

    def test_returns_correct_count(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "count.json")
            count = print_visitor_count(path)
            self.assertEqual(count, 1)

    def test_prints_output(self):
        import io
        import sys
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "count.json")
            captured = io.StringIO()
            sys.stdout = captured
            try:
                print_visitor_count(path)
            finally:
                sys.stdout = sys.__stdout__
            output = captured.getvalue()
        self.assertIn("visitors", output.lower())
        self.assertIn("1", output)

    def test_first_visitor_message(self):
        import io
        import sys
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "count.json")
            captured = io.StringIO()
            sys.stdout = captured
            try:
                print_visitor_count(path)
            finally:
                sys.stdout = sys.__stdout__
        self.assertIn("first visitor", captured.getvalue())


if __name__ == "__main__":
    unittest.main()
