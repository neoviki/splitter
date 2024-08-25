import os


class SimpleXMLParser:
    def __init__(self, filename):
        self.filename = filename
        self.config = {}

    def parse(self):
        with open(self.filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith('<') and line.endswith('>') and not line.startswith('</'):
                    tag = line[1:line.find('>')]
                    closing_tag = f"</{tag}>"
                    if closing_tag in line:
                        value = line[line.find('>') + 1:line.find(closing_tag)]
                        self.config[tag] = value

    def get(self, tag_name, default=None):
        value = self.config.get(tag_name, default)
        if value is None:
            raise ValueError(f"Tag <{tag_name}> not found in the config file.")
        return value


def merge_files():
    # Parse config file
    parser = SimpleXMLParser('config.xml')
    parser.parse()

    try:
        input_file = parser.get('input_file')
        max_file_count = int(parser.get('max_file_count'))
        file_extension = parser.get('file_extension')
        splitted_files_folder = parser.get('splitted_files_folder')
        merged_files_folder = parser.get('merged_files_folder')
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Ensure output directory exists
    os.makedirs(merged_files_folder, exist_ok=True)

    # Check if there are any files to merge
    if not os.listdir(splitted_files_folder):
        raise FileNotFoundError(f"No files found in '{splitted_files_folder}' to merge.")

    output_file_path = os.path.join(merged_files_folder, input_file)

    with open(output_file_path, 'wb') as output_file:
        for i in range(1, max_file_count + 1):
            chunk_file_path = os.path.join(splitted_files_folder, f'{i}{file_extension}')
            if os.path.exists(chunk_file_path):
                with open(chunk_file_path, 'rb') as chunk_file:
                    output_file.write(chunk_file.read())
            else:
                print(f"Warning: Expected chunk file '{chunk_file_path}' does not exist.")
                break

    print(f"Files from '{splitted_files_folder}' successfully merged into '{output_file_path}'.")


if __name__ == "__main__":
    merge_files()
