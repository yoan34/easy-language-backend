from functools import wraps
import time


def chatgpt_log(func):
    @wraps(func)
    def wrapper(self, question, context, *args, **kwargs):
        self.logger.log(f"{' ' * 8}[CHAT_GPT_MODEL] {self.model.value}")
        self.logger.log(f"{' ' * 8}[API_CONTEXT] {context}") if context else None
        self.logger.log(f"{' ' * 8}[API_QUESTION] {question}") if question else None
        answer, tokens = func(self, question, context, *args, **kwargs)
        self.logger.log(f"{' ' * 8}[API_ANSWER] {answer.splitlines()}")
        self.logger.log(f"{' ' * 8}[API_TOKENS] {tokens}")
        return answer
    return wrapper

def retry_api_call(max_attempts=10, delay=1):
    def decorator(api_call_func):
        @wraps(api_call_func)
        def wrapper(self, *args, **kwargs):
            attempts = 0
            success = False

            while attempts < max_attempts and not success:
                try:
                    response = api_call_func(self, *args, **kwargs)
                    success = True  # L'appel API a réussi, sortir de la boucle while
                except Exception as e:
                    self.logger.log(f"[ERROR_API] Error when call API: {e}")
                    attempts += 1
                    time.sleep(delay)

            if not success:
                self.logger.log(f"[FATAL_ERROR] Échec de l'appel API après {max_attempts} tentatives.")
            return response
        return wrapper
    return decorator

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