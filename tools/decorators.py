from functools import wraps

def chatgpt_log(func):
    @wraps(func)
    def wrapper(self, question, context, *args, **kwargs):
        self.logger.log(f"{' ' * 8}[API_CONTEXT] {context}")
        self.logger.log(f"{' ' * 8}[API_QUESTION] {question}")
        answer, tokens = func(self, question, context, *args, **kwargs)
        self.logger.log(f"{' ' * 8}[API_ANSWER] {answer}")
        self.logger.log(f"{' ' * 8}[API_TOKENS] {tokens}")
        return answer
    return wrapper

def handle_existence_errors(resource_type: str):
    def decorator(func):
        @wraps(func)
        def wrapper(self, name: str, *args, **kwargs):
            resource_path = self.path / name
            if resource_type == 'path' and resource_path.exists() or \
               resource_type == 'folder' and resource_path.is_dir() or \
               resource_type == 'file' and resource_path.is_file():
                self.logger.log(f"{resource_type.capitalize()} '{resource_path}' already exists.")
                return True
            self.logger.log(f"{resource_type.capitalize()} '{resource_path}' doesn't exist.")
            return False
        return wrapper
    return decorator