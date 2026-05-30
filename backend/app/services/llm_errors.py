class LLMProviderError(Exception):
    status_code = 500

    def __init__(self, public_message: str) -> None:
        super().__init__(public_message)
        self.public_message = public_message


class LLMConfigurationError(LLMProviderError):
    status_code = 400


class LLMProviderAPIError(LLMProviderError):
    status_code = 502


class LLMProviderTimeoutError(LLMProviderError):
    status_code = 504


class LLMResponseError(LLMProviderError):
    status_code = 502
