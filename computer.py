
from pathlib import Path

class Computer:
    def __init__(self, path):
      self.path = Path(path).resolve()
      self.data = []

    def create_folder(self):
      self.path.mkdir(parents=True, exist_ok=True)
      return self

    def does_folder_exists(self):
      return self.path.is_dir()
    
    def does_file_exists(self):
      return self.path.is_file()

    def read_file(self, filename):
      file_path = self.path / filename
      return file_path.read_text()

    def write_file(self, filename, content):
      file_path = self.path / filename
      file_path.write_text(content)

    def go_to(self, path):
      self.path = Path(path).resolve()
      return self
    
    def change_directory(self, new_path):
        self.path = (self.path / new_path).resolve()

    @property
    def list_folders(self):
      return [item for item in self.path.iterdir() if item.is_dir()]

    @property
    def list_files(self):
      return [item for item in self.path.iterdir() if item.is_file()]

    @property
    def list_folders_and_files(self):
      return list(self.path.iterdir())



if __name__ == "__main__":
  computer = Computer('.')

  print(computer.path)
  computer.change_directory('../..')
  print(computer.path)
  files = computer.list_folders_and_files
  print(files)
