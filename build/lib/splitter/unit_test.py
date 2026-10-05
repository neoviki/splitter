#!/usr/bin/env python3

import shutil
import tempfile
import unittest
from pathlib import Path

import splitter

class TestSplitter(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_parse_size(self):
        self.assertEqual(splitter.parse_size("1k"), 1024)
        self.assertEqual(splitter.parse_size("1kb"), 1024)
        self.assertEqual(splitter.parse_size("1m"), 1024 * 1024)
        self.assertEqual(splitter.parse_size("10m"), 10 * 1024 * 1024)
        self.assertEqual(splitter.parse_size("1g"), 1024 * 1024 * 1024)
        self.assertEqual(splitter.parse_size("100"), 100)

    def test_parse_size_case(self):
        self.assertEqual(splitter.parse_size("10M"), 10 * 1024 * 1024)
        self.assertEqual(splitter.parse_size("1GB"), 1024 * 1024 * 1024)

    def test_split_file(self):
        source_file = self.test_dir / "test.bin"

        data = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        source_file.write_bytes(data)

        splitter.split_file(source_file, 10)

        split_dir = Path(str(source_file) + ".split")
        data_dir = split_dir / "data_chunks"

        self.assertTrue(split_dir.exists())
        self.assertTrue((split_dir / "README.md").exists())
        self.assertTrue((split_dir / "merge").exists())
        self.assertTrue((data_dir / "merge.py").exists())

        self.assertTrue((data_dir / "1").exists())
        self.assertTrue((data_dir / "2").exists())
        self.assertTrue((data_dir / "3").exists())

        self.assertEqual((data_dir / "1").read_bytes(), b"ABCDEFGHIJ")
        self.assertEqual((data_dir / "2").read_bytes(), b"KLMNOPQRST")
        self.assertEqual((data_dir / "3").read_bytes(), b"UVWXYZ")

    def test_split_and_merge(self):
        source_file = self.test_dir / "test.bin"

        original_data = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 100
        source_file.write_bytes(original_data)

        splitter.split_file(source_file, 100)

        split_dir = Path(str(source_file) + ".split")
        data_dir = split_dir / "data_chunks"
        merge_py = data_dir / "merge.py"

        # Run the generated merge program.
        import subprocess

        result = subprocess.run(
            ["python3", str(merge_py)],
            cwd=split_dir,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)

        recreated_file = split_dir / "test.bin"

        self.assertTrue(recreated_file.exists())
        self.assertEqual(recreated_file.read_bytes(), original_data)

    def test_small_file_is_not_split(self):
        source_file = self.test_dir / "small.bin"
        source_file.write_bytes(b"12345")

        splitter.process_files([source_file], 10)

        split_dir = Path(str(source_file) + ".split")

        self.assertFalse(split_dir.exists())

    def test_invalid_size(self):
        with self.assertRaises(ValueError):
            splitter.parse_size("invalid")

if __name__ == "__main__":
    unittest.main()


