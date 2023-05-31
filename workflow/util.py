from typing import Any, Dict


def result(success: Any, data: Dict[str, Any] = None, message: str = None, details: str = None):
    """
        Default result dict structure used by all components of the module
    """
    result_dict = {'success': success}

    if data:
        result_dict['data'] = data
    if message:
        result_dict['message'] = message
    if details:
        result_dict['details'] = details

    return result_dict
