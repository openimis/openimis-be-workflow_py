import logging
from typing import Dict
from urllib.parse import urljoin

import requests

from workflow.util import result

logger = logging.getLogger(__name__)


class LightningClient:
    def __init__(self):
        from workflow.apps import WorkflowConfig
        self._url = f'{WorkflowConfig.lightning_url}:{WorkflowConfig.lightning_port}'
        self._api_key = WorkflowConfig.lightning_api_key

    def __enter__(self):
        self._current_session = requests.Session()
        self._current_session.headers.update({'Authorization': f'Bearer {self._api_key}'})
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._current_session:
            self._current_session.close()
        if exc_type is not None:
            # re-raise exceptions
            return False

    def get_projects(self):
        return self._get('api/projects/')

    def get_provisions(self, project_uuid: str):
        return self._get(urljoin('api/provision/', project_uuid))

    def trigger_workflow(self, trigget_id: str, data: Dict):
        return self._post(urljoin('i/', trigget_id), data)

    def _get(self, path) -> Dict:
        try:
            url = urljoin(self._url, path)
            response = self._current_session.get(url)
            return self._handle_response(response)
        except Exception as e:
            return self._handle_error(e)

    def _post(self, path, payload: Dict) -> requests.Response:
        try:
            url = urljoin(self._url, path)
            response = self._current_session.post(url, data=payload)
            return self._handle_response(response)
        except Exception as e:
            return self._handle_error(e)

    def _handle_response(self, response):
        if response.ok:
            return result(success=True, data=response.json())
        else:
            logger.error("openFN/Lightning request failed, code: {}".format(response.status_code))
            return result(success=False,
                          message='openFN/Lightning request failed',
                          details=str(response.status_code))

    def _handle_error(self, error):
        logger.error("Error during openFN/Lightning get request", exc_info=e)
        return result(success=False,
                      message='Error during openFN/Lightning request',
                      details=str(error))
