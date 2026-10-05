#!/usr/bin/env python3

import argparse
from pathlib import Path


DEFAULT_SPLIT_SIZE = 10 * 1024 * 1024


def parse_size(value):
    value = value.lower().strip()
    units = {"k": 1024, "kb": 1024, "m": 1024 * 1024, "mb": 1024 * 1024, "g": 1024 * 1024 * 1024, "gb": 1024 * 1024 * 1024}
    for unit, multiplier in units.items():
        if value.endswith(unit):
            return int(float(value[:-len(unit)]) * multiplier)
    return int(value)


def create_merge_script(split_dir, data_dir, original_name):
    merge_py = data_dir / "merge.py"
    merge_file = split_dir / "merge"
    readme_file = split_dir / "README.md"

    merge_code = f'''#!/usr/bin/env python3

from pathlib import Path


ORIGINAL_FILE = {original_name!r}
DATA_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = DATA_DIR.parent / ORIGINAL_FILE


def get_parts():
    parts = [path for path in DATA_DIR.iterdir() if path.is_file() and path.name.isdigit()]
    parts.sort(key=lambda path: int(path.name))
    return parts


def check_parts(parts):
    expected = 1
    for part in parts:
        if int(part.name) != expected:
            print(f"Error: missing part {{expected}}")
            return False
        expected += 1
    return True


def merge_file():
    parts = get_parts()
    if not parts:
        print("Error: no data chunks found.")
        return False
    if not check_parts(parts):
        return False

    if OUTPUT_FILE.exists():
        answer = input(f"{{OUTPUT_FILE.name}} already exists. Overwrite? [y/N]: ").strip().lower()
        if answer != "y":
            print("Skipped.")
            return False

    print(f"Merging {{len(parts)}} parts...")
    print(f"Output: {{OUTPUT_FILE}}")

    with open(OUTPUT_FILE, "wb") as output:
        for part in parts:
            print(f"  Adding: {{part.name}}")
            with open(part, "rb") as source:
                while True:
                    data = source.read(1024 * 1024)
                    if not data:
                        break
                    output.write(data)

    print(f"Done: {{OUTPUT_FILE}}")
    return True


def main():
    merge_file()


if __name__ == "__main__":
    main()
'''

    merge_script = '''#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "$SCRIPT_DIR/data_chunks/merge.py"
'''

    readme_code = f'''# {original_name}.split

This directory contains a split version of:

```text
{original_name}
```

This split file was created using **splitter**:

https://github.com/neoviki/splitter

## Merge

To recreate the original file, simply execute:

```bash
./merge
```

The recreated file will be placed in this directory:

```text
{original_name}
```

## Split Large Files

If you want to split a large file into smaller chunks, you can use **splitter**.

Install it with pipx:

```bash
pipx install git+https://github.com/neoviki/splitter.git
```

Then:

```bash
splitter your-large-file.zip
```

The default chunk size is 10 MB.

You can specify another chunk size:

```bash
splitter your-large-file.zip -s 100m
```

For more information:

https://github.com/neoviki/splitter
'''

    merge_py.write_text(merge_code)
    merge_file.write_text(merge_script)
    readme_file.write_text(readme_code)
    merge_py.chmod(0o755)
    merge_file.chmod(0o755)


def split_file(file_path, split_size):
    split_dir = Path(str(file_path) + ".split")
    data_dir = split_dir / "data_chunks"

    if split_dir.exists():
        print(f"Error: already exists: {split_dir}")
        return

    split_dir.mkdir()
    data_dir.mkdir()
    create_merge_script(split_dir, data_dir, file_path.name)

    part_number = 1
    with open(file_path, "rb") as source:
        while True:
            data = source.read(split_size)
            if not data:
                break
            part_path = data_dir / str(part_number)
            with open(part_path, "wb") as part:
                part.write(data)
            print(f"  Created: {part_path}")
            part_number += 1

    print()
    print(f"Done: {part_number - 1} parts")
    print(f"Output: {split_dir}")


def ask_to_split(file_path):
    answer = input(f"Split '{file_path}'? [y/N]: ").strip().lower()
    return answer == "y"


def process_files(files, split_size):
    for file_path in files:
        if not file_path.is_file() or file_path.name.endswith(".split"):
            continue
        file_size = file_path.stat().st_size
        if file_size <= split_size:
            continue
        print()
        print(f"File: {file_path}")
        print(f"Size: {file_size / (1024 * 1024):.2f} MB")
        if ask_to_split(file_path):
            split_file(file_path, split_size)
        else:
            print("Skipped.")


def load_files(file_name):
    if file_name:
        file_path = Path(file_name)
        if not file_path.exists():
            print(f"Error: file not found: {file_path}")
            return []
        if not file_path.is_file():
            print(f"Error: not a file: {file_path}")
            return []
        return [file_path]
    return list(Path(".").iterdir())


def main():
    parser = argparse.ArgumentParser(description="Split large files into numbered chunks.")
    parser.add_argument("file", nargs="?", help="file to split; if omitted, check current directory")
    parser.add_argument("-s", "--size", default="10m", help="split size, default: 10m")
    args = parser.parse_args()

    try:
        split_size = parse_size(args.size)
    except ValueError:
        print(f"Error: invalid size: {args.size}")
        return

    if split_size <= 0:
        print("Error: split size must be greater than zero.")
        return

    files = load_files(args.file)
    if files:
        process_files(files, split_size)


if __name__ == "__main__":
    main()
