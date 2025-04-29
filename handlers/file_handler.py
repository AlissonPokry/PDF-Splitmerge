import os

class FileHandler:
    @staticmethod
    def extract_number(filename):
        numbers = ''.join(char for char in filename if char.isdigit())
        return int(numbers) if numbers else float('inf')

    @staticmethod
    def sort_files_alphabetically(files):
        return sorted(files, key=lambda x: os.path.basename(x).lower())

    @staticmethod
    def sort_files_numerically(files):
        return sorted(files, key=lambda x: FileHandler.extract_number(os.path.basename(x)))

    @staticmethod
    def process_dropped_files(files_data):
        return [f.strip('{}') for f in files_data.split('} {') if f.lower().endswith('.pdf')]