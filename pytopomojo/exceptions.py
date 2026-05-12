class TopomojoException(Exception):
    """Exception raised when the TopoMojo API returns an error."""

    def __init__(self, status_code, response_message) -> None:
        """Initialize the exception with a status code and API message."""

        self.status_code = status_code
        self.response_message = response_message
        super().__init__(
            f"Topomojo API Error - Status Code: {status_code}, Response: {response_message}")
