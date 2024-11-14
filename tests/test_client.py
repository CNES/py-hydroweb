# © CNES

import logging
import os
from datetime import datetime
from unittest.mock import patch

import pytest

import py_hydroweb

LOGGER = logging.getLogger(__name__)


class TestClient:

    # Create Hydroweb client
    client: py_hydroweb.Client = py_hydroweb.Client("https://test/api", "my_api_key")
    basket: py_hydroweb.DownloadBasket = py_hydroweb.DownloadBasket("my_first_download")

    DOWNLOAD_ID: str = "ABCDEF"
    EXPECTED_HEADERS: dict = {"Content-Type": "application/json", "X-Api-Key": "my_api_key"}

    @pytest.fixture(scope="session", autouse=True)
    def fill_download_basket(self):
        # Add a few collections in our basket
        self.basket.add_collection("HYDROWEB_LAKES_RESEARCH", correlation_id="HYDROWEB_LAKES_RESEARCH")
        self.basket.add_collection(
            "HYDROWEB_LAKES_OPE",
            correlation_id="HYDROWEB_LAKES_OPE",
            bbox=[17.6123, 4.53676, 54.7998, 18.04142],
        )
        self.basket.add_collection(
            "LIS_SNT_YEARLY",
            correlation_id="LIS_SNT_YEARLY",
            folder="lis/snt/",
            bbox=[17.6123, 4.53676, 54.7998, 18.04142],
            intersects={
                "coordinates": [
                    [[21.282, 17.656], [21.282, 14.221], [26.797, 14.221], [26.797, 17.656], [21.282, 17.656]]
                ],
                "type": "Polygon",
            },
            datetime="2022-01-01T00:00:00Z/2022-12-31T23:59:59Z",
            query={
                "start_datetime": {"lte": "2024-02-03T00:00:00.000Z"},
                "end_datetime": {"gte": "2023-02-02T00:00:00.000Z"},
            },
        )

    @patch("requests.post")
    def test_submit_download(self, mock):

        # Expected API call
        expected_url: str = "https://test/api/download/workflows"

        expected_body: dict = {
            "workflowName": "my_first_download",
            "collections": [
                {
                    "collectionId": "HYDROWEB_LAKES_RESEARCH",
                    "correlationId": "HYDROWEB_LAKES_RESEARCH",
                    "folder": None,
                    "filters": {"bbox": None, "intersects": None, "datetime": None, "query": None},
                },
                {
                    "collectionId": "HYDROWEB_LAKES_OPE",
                    "correlationId": "HYDROWEB_LAKES_OPE",
                    "folder": None,
                    "filters": {
                        "bbox": [17.6123, 4.53676, 54.7998, 18.04142],
                        "intersects": None,
                        "datetime": None,
                        "query": None,
                    },
                },
                {
                    "collectionId": "LIS_SNT_YEARLY",
                    "correlationId": "LIS_SNT_YEARLY",
                    "folder": "lis/snt/",
                    "filters": {
                        "bbox": [17.6123, 4.53676, 54.7998, 18.04142],
                        "intersects": {
                            "coordinates": [
                                [
                                    [21.282, 17.656],
                                    [21.282, 14.221],
                                    [26.797, 14.221],
                                    [26.797, 17.656],
                                    [21.282, 17.656],
                                ]
                            ],
                            "type": "Polygon",
                        },
                        "datetime": "2022-01-01T00:00:00Z/2022-12-31T23:59:59Z",
                        "query": {
                            "start_datetime": {"lte": "2024-02-03T00:00:00.000Z"},
                            "end_datetime": {"gte": "2023-02-02T00:00:00.000Z"},
                        },
                    },
                },
            ],
        }

        # Mocked return value
        mock.return_value.json.return_value = {
            "workflowId": self.DOWNLOAD_ID,
            "status": "CREATED",
        }

        download_id: str = self.client.submit_download(self.basket)
        assert download_id == self.DOWNLOAD_ID

        mock.assert_called_once_with(expected_url, json=expected_body, headers=self.EXPECTED_HEADERS)

    @patch("requests.get")
    def test_get_download_info(self, mock):

        # Expected API call
        expected_url: str = f"https://test/api/download/workflows/{self.DOWNLOAD_ID}/status"

        # Mocked return value
        mock.return_value.json.return_value = {
            "workflowId": self.DOWNLOAD_ID,
            "status": "RUNNING",
            "progress": 17,
        }

        infos: py_hydroweb.DownloadInfo = self.client.get_download_info(self.DOWNLOAD_ID)
        assert infos.download_id == self.DOWNLOAD_ID
        assert infos.progress == 17
        assert infos.status == py_hydroweb.DownloadInfo.Status.RUNNING

        mock.assert_called_once_with(expected_url, headers=self.EXPECTED_HEADERS)

    @patch("requests.get")
    def test_get_downloads_info_with_last_update(self, mock):

        last_update: datetime = datetime.fromisoformat("2022-10-22")

        # Expected API call
        expected_url: str = "https://test/api/download/workflows?sort=lastUpdate,DESC&lastUpdate=2022-10-22T00:00:00Z&unpaged=true"

        # Mocked return value
        mock.return_value.json.return_value = {
            "content": [
                {"workflowId": "1", "status": "RUNNING", "progress": 15},
                {"workflowId": "2", "status": "CREATED", "progress": 0},
                {"workflowId": "3", "status": "COMPLETED", "progress": None},
            ]
        }

        infos: dict[str, py_hydroweb.DownloadInfo] = self.client.get_downloads_info(last_update)
        assert len(infos) == 3
        assert infos["1"] == py_hydroweb.DownloadInfo("1", py_hydroweb.DownloadInfo.Status.RUNNING, 15)
        assert infos["2"] == py_hydroweb.DownloadInfo("2", py_hydroweb.DownloadInfo.Status.CREATED, 0)
        assert infos["3"] == py_hydroweb.DownloadInfo("3", py_hydroweb.DownloadInfo.Status.COMPLETED, None)

        mock.assert_called_once_with(expected_url, headers=self.EXPECTED_HEADERS)

    @patch("requests.get")
    def test_get_downloads_info_paginated(self, mock):

        # Expected API call
        expected_url: str = "https://test/api/download/workflows?sort=lastUpdate,DESC&page=0&size=10"

        # Mocked return value
        mock.return_value.json.return_value = {
            "content": [
                {"workflowId": "1", "status": "RUNNING", "progress": 15},
                {"workflowId": "2", "status": "CREATED", "progress": 0},
                {"workflowId": "3", "status": "COMPLETED", "progress": None},
            ]
        }

        infos: dict[str, py_hydroweb.DownloadInfo] = self.client.get_downloads_info(page=0, size=10)
        assert len(infos) == 3
        assert infos["1"] == py_hydroweb.DownloadInfo("1", py_hydroweb.DownloadInfo.Status.RUNNING, 15)
        assert infos["2"] == py_hydroweb.DownloadInfo("2", py_hydroweb.DownloadInfo.Status.CREATED, 0)
        assert infos["3"] == py_hydroweb.DownloadInfo("3", py_hydroweb.DownloadInfo.Status.COMPLETED, None)

        mock.assert_called_once_with(expected_url, headers=self.EXPECTED_HEADERS)

    @patch("requests.get")
    def test__get_zip_filename(self, mock):

        # Expected API call
        expected_url: str = f"https://test/api/download/workflows/{self.DOWNLOAD_ID}/zip"

        # Mocked return value
        mock.return_value.__enter__.return_value.content = b"54sdF4G5vd2dRREZdsxv55v9ssfbpDKopj"

        output_path: str = self.client._get_zip(self.DOWNLOAD_ID, "myfile.zip", "/app/tests/output/")
        assert output_path == "/app/tests/output/myfile.zip"
        assert os.path.exists("/app/tests/output/myfile.zip")

        mock.assert_called_once_with(expected_url, headers=self.EXPECTED_HEADERS, stream=True)

    @patch("requests.get")
    def test__get_zip_no_filename(self, mock):

        # Expected API call
        expected_url: str = f"https://test/api/download/workflows/{self.DOWNLOAD_ID}/zip"

        # Mocked return value
        mock.return_value.__enter__.return_value.content = b"54sdF4G5vd2dRREZdsxv55v9ssfbpDKopj"
        mock.return_value.__enter__.return_value.headers = {
            "content-disposition": f"attachment; filename={self.DOWNLOAD_ID}.zip"
        }

        output_path: str = self.client._get_zip(self.DOWNLOAD_ID, output_folder="/app/tests/output/")
        assert output_path == f"/app/tests/output/{self.DOWNLOAD_ID}.zip"
        assert os.path.exists(f"/app/tests/output/{self.DOWNLOAD_ID}.zip")

        mock.assert_called_once_with(expected_url, headers=self.EXPECTED_HEADERS, stream=True)

    @patch("requests.delete")
    def test_delete_download_OK(self, mock):

        # Expected API call
        expected_url: str = f"https://test/api/download/workflows/{self.DOWNLOAD_ID}"

        self.client.delete_download(self.DOWNLOAD_ID)
        mock.assert_called_once_with(expected_url, headers=self.EXPECTED_HEADERS)

    @patch("requests.delete")
    def test_delete_download_KO(self, mock):

        # Expected API call
        expected_url: str = f"https://test/api/download/workflows/{self.DOWNLOAD_ID}"

        mock.return_value.ok = False
        mock.return_value.status_code = "404"

        with pytest.raises(py_hydroweb.exceptions.ApiErrorException, match="404"):
            self.client.delete_download(self.DOWNLOAD_ID)
        mock.assert_called_with(expected_url, headers=self.EXPECTED_HEADERS)

    @patch("py_hydroweb.client.Client.get_download_info")
    @patch("py_hydroweb.client.Client._get_zip")
    def test_download_zip(self, mock__get_zip, mock_get_download_info):
        # Mocked return value
        mock_get_download_info.return_value.status = py_hydroweb.DownloadInfo.Status.COMPLETED
        mock__get_zip.return_value = "/my/file.zip"

        assert self.client.download_zip(self.DOWNLOAD_ID) == "/my/file.zip"

        mock_get_download_info.assert_called_once_with(self.DOWNLOAD_ID)
        mock__get_zip.assert_called_once_with(self.DOWNLOAD_ID, None, None)

    @patch("py_hydroweb.client.Client.get_download_info")
    def test_download_zip_failed(self, mock_get_download_info):
        # Mocked return value
        mock_get_download_info.return_value.status = py_hydroweb.DownloadInfo.Status.FAILED

        assert self.client.download_zip(self.DOWNLOAD_ID) is None

        mock_get_download_info.assert_called_once_with(self.DOWNLOAD_ID)

    @patch("py_hydroweb.client.Client.submit_download")
    @patch("py_hydroweb.client.Client.download_zip")
    def test_submit_and_download_zip(self, mock_download_zip, mock_submit_download):
        # Mocked return value
        mock_submit_download.return_value = self.DOWNLOAD_ID
        mock_download_zip.return_value = "output/test.zip"

        assert self.client.submit_and_download_zip(self.basket, "test.zip", "output") == "output/test.zip"

        mock_submit_download.assert_called_once_with(self.basket)
        mock_download_zip.assert_called_once_with(self.DOWNLOAD_ID, "test.zip", "output")
