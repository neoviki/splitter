import os
import sys


class SimpleXMLWriter:
    def __init__(self, filename):
        self.filename = filename
        self.config = {}

    def set(self, tag_name, value):
        self.config[tag_name] = value

    def save(self):
        with open(self.filename, 'w') as file:
            file.write('<config>\n')
            for tag, value in self.config.items():
                file.write(f'  <{tag}>{value}</{tag}>\n')
            file.write('</config>\n')


def split_file(input_file, chunk_size_mb):
    # Convert chunk size to bytes
    chunk_size = chunk_size_mb * 1024 * 1024

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    # Create the folder for file chunks if it doesn't exist
    splitted_files_folder = 'file_chunks'
    if not os.path.exists(splitted_files_folder):
        os.makedirs(splitted_files_folder)
    else:
        # If the folder already exists, check if it contains files
        if os.listdir(splitted_files_folder):
            print(
                f"Error: The folder '{splitted_files_folder}' already contains files. Please clear the folder or choose a different location.")
            sys.exit(1)

    file_extension = '.bin'
    max_file_count = 1000
    file_size = os.path.getsize(input_file)
    num_chunks = file_size // chunk_size + (file_size % chunk_size > 0)

    if num_chunks > max_file_count:
        print("Error: Maximum file splitting size reached. Cannot split into more than 1000 chunks.")
        sys.exit(1)

    # Split the file into chunks
    with open(input_file, 'rb') as file:
        for i in range(1, num_chunks + 1):
            chunk = file.read(chunk_size)
            with open(os.path.join(splitted_files_folder, f'{i}{file_extension}'), 'wb') as chunk_file:
                chunk_file.write(chunk)

    # Create and save config.xml
    config_writer = SimpleXMLWriter('config.xml')
    config_writer.set('input_file', input_file)
    config_writer.set('chunk_size_mb', str(chunk_size_mb))
    config_writer.set('max_file_count', str(num_chunks))
    config_writer.set('file_extension', file_extension)
    config_writer.set('splitted_files_folder', splitted_files_folder)
    config_writer.set('merged_files_folder', 'merged_file')
    config_writer.save()

    print(f"File '{input_file}' successfully split into {num_chunks} chunks.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python splitter.py <input_file> <chunk_size_mb>")
        sys.exit(1)

    input_file = sys.argv[1]
    chunk_size_mb = int(sys.argv[2])

    split_file(input_file, chunk_size_mb)
