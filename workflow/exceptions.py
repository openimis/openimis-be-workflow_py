
class PythonWorkflowHandlerException(Exception):
    """
    Custom exception class for handling errors within Python Workflows.
    """

    def __init__(self, message, *args, **kwargs):
        if args or kwargs:
            message = message.format(*args, **kwargs)
        super().__init__(message)
        self.message = message

    def __str__(self):
        """
        Return the string representation of the exception.
        """
        return f"PythonWorkflowHandlerException: {self.message}"
