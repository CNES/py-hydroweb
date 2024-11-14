# © CNES

import logging
import os
import re
from datetime import date
from time import sleep

import requests
from retry import retry
from tqdm import tqdm

from py_hydroweb.download_basket import DownloadBasket
from py_hydroweb.download_info import DownloadInfo
from py_hydroweb.exceptions import ApiErrorException, MissingApiKeyException, NonexistentFolderException

LOGGER = logging.getLogger(__name__)


class Client:
    """A Client for interacting with the hydroweb.next download API
    Visit https://hydroweb.next.theia-land.fr for more information about the platform.
    """

    hydroweb_api_url: str
    headers: dict

    retry_policy = {"exceptions": ApiErrorException, "tries": 3, "delay": 3, "backoff": 3, "logger": LOGGER}

    _HTTP_HEADERS_FILENAME_REXP = r"filename=(.*\.zip)"
    _DEFAULT_HYDROWEB_API_URL = "https://hydroweb.next.theia-land.fr/api"

    def __init__(self, hydroweb_api_url: str = _DEFAULT_HYDROWEB_API_URL, api_key: str = None):
        self.hydroweb_api_url = hydroweb_api_url

        # If no API key was explicitly provided, we will look for the HYDROWEB_API_KEY environment variable
        if not api_key:
            api_key = os.environ.get("HYDROWEB_API_KEY")

        # Still no API key? this is unrecoverable
        if not api_key:
            raise MissingApiKeyException(
                "Either explicitly pass api_key parameter to Client's constructor or define HYDROWEB_API_KEY environment variable"
            )

        self.headers = {"Content-Type": "application/json", "X-Api-Key": api_key}

    @retry(**retry_policy)
    def submit_download(self, download_basket: DownloadBasket) -> str:
        """Sends the download request and returns its download_id without waiting for it to be ready (not blocking)"""
        url: str = f"{self.hydroweb_api_url}/download/workflows"

        resp: requests.Response = requests.post(url, json=download_basket.as_dict(), headers=self.headers)
        if resp.ok:
            download_id: str = resp.json()["workflowId"]
            LOGGER.info(f"Successfully submitted download request {download_id}")
            return download_id

        raise ApiErrorException(url, resp.status_code, resp.json() if resp else "unknown")

    @retry(**retry_policy)
    def get_download_info(self, download_id: str) -> DownloadInfo:
        """Gets download status for this specific download_id request"""
        url: str = f"{self.hydroweb_api_url}/download/workflows/{download_id}/status"

        resp: requests.Response = requests.get(url, headers=self.headers)
        if resp.ok:
            body: dict = resp.json()
            # Status is a mandatory output
            status: str = body["status"]
            # Progress is optional
            progress: int = body.get("progress")
            return DownloadInfo(download_id, status, progress)

        raise ApiErrorException(url, resp.status_code, resp.json() if resp else "unknown")

    @retry(**retry_policy)
    def get_downloads_info(
        self, last_update: date = None, page: int = None, size: int = None
    ) -> dict:  # dict[str, DownloadInfo]
        """Gets download status for all download requests having a last update after given input date
        Return type is a map worklow_id -> status
        """
        url: str = f"{self.hydroweb_api_url}/download/workflows?sort=lastUpdate,DESC"

        # last_update is optional
        if last_update:
            url += f"&lastUpdate={last_update.isoformat()}Z"

        # page and size (pagination parameters) are optional
        if page is None and size is None:
            url += "&unpaged=true"
        else:
            if page is not None:
                url += f"&page={page}"
            if size is not None:
                url += f"&size={size}"

        resp: requests.Response = requests.get(url, headers=self.headers)
        if resp.ok:
            infos = {
                wf["workflowId"]: DownloadInfo(wf["workflowId"], wf["status"], wf["progress"])
                for wf in resp.json()["content"]
            }
            LOGGER.debug(f"Downloads details: {infos}")
            return infos

        raise ApiErrorException(url, resp.status_code, resp.json() if resp else "unknown")

    def download_zip(self, download_id: str, zip_filename: str = None, output_folder: str = None) -> str:
        """Blocking wait for given download_id to be ready, then download it and return file path"""

        # Initialize a progress bar
        LOGGER.info("Waiting for download to be ready...")
        progress_bar = tqdm(total=100, desc="Wait", leave=True)

        # Poll every 10s to check for download status
        previous_progress = 0
        info: DownloadInfo = self.get_download_info(download_id)
        while info.status in [  # pylint: disable=bad-exit-condition
            DownloadInfo.Status.CREATED,
            DownloadInfo.Status.RUNNING,
        ]:
            progress_bar.update(info.progress - previous_progress)
            previous_progress = info.progress
            sleep(10)
            info = self.get_download_info(download_id)
        progress_bar.update(100 - previous_progress)
        progress_bar.close()

        if info.status != DownloadInfo.Status.COMPLETED:
            LOGGER.error(
                "Download preparation did not complete successfully, please try again later or else contact hydroweb.next support team."
            )
            return None

        LOGGER.info("Download is ready!")

        # Proceed with download
        return self._get_zip(download_id, zip_filename, output_folder)

    def submit_and_download_zip(
        self, download_basket: DownloadBasket, zip_filename: str = None, output_folder: str = None
    ) -> str:
        """Full (blocking) version that sends the download request, wait for it to be ready, and downloads zip file"""
        download_id: str = self.submit_download(download_basket)
        return self.download_zip(download_id, zip_filename, output_folder)

    @retry(**retry_policy)
    def delete_download(self, download_id: str):
        """Delete given download_id request"""
        url: str = f"{self.hydroweb_api_url}/download/workflows/{download_id}"
        resp: requests.Response = requests.delete(url, headers=self.headers)
        if not resp.ok:
            raise ApiErrorException(url, resp.status_code, resp.json() if resp else "unknown")

    @retry(**retry_policy)
    def _get_zip(self, download_id: str, zip_filename: str = None, output_folder: str = None) -> str:
        """Downloads given download_id (warning: download request must be ready) and return file path"""
        if output_folder and not os.path.exists(output_folder):
            raise NonexistentFolderException(f"Output folder {output_folder} must exist!")

        url: str = f"{self.hydroweb_api_url}/download/workflows/{download_id}/zip"

        try:
            with requests.get(url, headers=self.headers, stream=True) as resp:
                resp.raise_for_status()
                # If zip_filename was not defined, we must look for attachment name in the headers that the API has returned to us
                output_file: str = zip_filename if zip_filename else self._get_attachment_name(resp.headers)
                # If output_path was not defined, downloaded file will be written in current folder by default
                output_path: str = os.path.join(output_folder, output_file) if output_folder else output_file

                LOGGER.info(f"Starting to download {output_file}...")
                with open(output_path, "wb") as f:
                    # Initialize a progress bar
                    total_size = int(resp.headers.get("content-length", 0))
                    progress_bar = tqdm(
                        total=total_size, unit="B", unit_scale=True, desc=output_file, leave=True
                    )
                    # Write by chunks of 500kB
                    for chunk in resp.iter_content(chunk_size=524288):
                        progress_bar.update(len(chunk))
                        f.write(chunk)
                    progress_bar.close()
        except requests.exceptions.RequestException as e:
            raise ApiErrorException(
                url, e.response.status_code, e.response.json() if e.response else "unknown"
            )

        LOGGER.info(f"File has been successfully downloaded to: {output_path}")
        return output_path

    def _get_attachment_name(self, headers: dict) -> str:
        """Fetch the attachment file name returned by the API
        In the content-disposition HTTP header we should find:  attachment; filename=<zip name>
        """
        matches = re.findall(self._HTTP_HEADERS_FILENAME_REXP, headers.get("content-disposition"))
        if matches:
            return matches[0]

        raise RuntimeError("Could not find filename in the content-disposition header returned by the API")
