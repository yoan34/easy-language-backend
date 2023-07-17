from typing import List, Union
from pathlib import Path
from models.logger import Logger
from tools.decorators import handle_existence_errors


class Computer:
    def __init__(self, path: str, logger: Logger) -> None:
        self.path = Path(path).resolve()
        self.base_path = self.path
        self.logger = logger
        if path == ".":
            path = Path(__file__).parent.resolve()
        else:
            self.create_folder(str(self.path))
        if not self.path_exists(""):
            raise ValueError(f"Path '' does not exist.")


    @handle_existence_errors('path')
    def path_exists(self, path: str) -> bool:
        ...

    @handle_existence_errors('folder')
    def folder_exists(self, name: str) -> bool:
        ...

    @handle_existence_errors('file')
    def file_exists(self, name: str) -> bool:
        ...

    def create_folder(self, folder_path: str) -> 'Computer':
        full_path = self.path / folder_path
        full_path.mkdir(parents=True, exist_ok=True)
        self.logger.log(f"folder '{folder_path}' created successfully.")
        return self

    def read_file(self, filename: str) -> list[str]:
        file_path = self.path / filename
        return file_path.read_text().splitlines()

    def write_file(self, filename: str, content: Union[str, List[str]], separator: str = '\n') -> None:
        if isinstance(content, str):
            content = content.splitlines()
        file_path = self.path / filename
        file_path.write_text(separator.join(content))
        self.logger.log(f"File '{file_path}' created and written successfully.")

    def go_to(self, path: str) -> 'Computer':
        if self.path_exists(path):
            self.path = Path(path).resolve()
        else:
            print(f"{self.path} doesn't exist.")
        return self

    def change_directory(self, new_path: str) -> 'Computer':
        full_path = self.path / new_path
        if self.path_exists(str(full_path)):
            self.path = full_path.resolve()
            self.logger.log(f"New path: {full_path}")
        else:
            self.logger.log(f"{full_path} doesn't exist.")
        return self

    def comeback_to_base_path(self):
        self.path = self.base_path
        return self

    @property
    def list_folders(self) -> List[Path]:
        return [item for item in self.path.iterdir() if item.is_dir()]

    @property
    def list_files(self) -> List[Path]:
        return [item for item in self.path.iterdir() if item.is_file()]

    @property
    def list_folders_and_files(self) -> List[Path]:
        return list(self.path.iterdir())



if __name__ == "__main__":
    computer = Computer('../data')
    print(computer.path)
    print(computer.base_path)
    print(computer.change_directory('french_english'))
    print(computer.path)
    print(computer.base_path)
