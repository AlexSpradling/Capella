class TextExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.text_blocks = self._parse_text_file()

    def _parse_text_file(self):
        with open(self.file_path, 'r') as f:
            lines = f.readlines()

        blocks = {}
        current_block_title = None
        current_block_text = []

        for line in lines:
            stripped_line = line.strip()

            # Check if the line is a title (starts with '# ')
            if stripped_line.startswith('# '):
                # If we're already capturing a block, save it and start a new one
                if current_block_title:
                    key = self._generate_key(current_block_title)
                    blocks[key] = ''.join(current_block_text).strip()
                    current_block_text = []

                current_block_title = stripped_line[2:].strip().lower().replace(' ', '_')
            else:
                current_block_text.append(line)

        # Capture the last block if needed
        if current_block_title and current_block_text:
            key = self._generate_key(current_block_title)
            blocks[key] = ''.join(current_block_text).strip()

        return blocks

    @staticmethod
    def _generate_key(title):
        return title.replace(' ', '_').lower()

    def get_text(self, key):
        return self.text_blocks.get(key, None)
