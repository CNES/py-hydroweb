# © CNES


class CollectionUnicityException(Exception):
    """Raised when trying to add an already existing (collection id, correlation id) to a download basket"""

    pass


class MissingApiKeyException(Exception):
    """Raised when trying to add an already existing (collection id, correlation id) to a download basket"""

    pass


class NonexistentFolderException(Exception):
    """Raised when trying to use an output folder that does not exist"""

    pass


class ApiErrorException(Exception):
    """Raised when trying to add an already existing (collection id, correlation id) to a download basket"""

    url: str
    status_code: str
    details: any

    def __init__(self, url: str, status_code: str, details: any):
        # Call the base class constructor with the parameters it needs
        super().__init__(
            f"API call to {url} returned a {status_code} HTTP code. Error message (if provided): {details}"
        )
        self.url = url
        self.status_code = status_code
        self.details = details
