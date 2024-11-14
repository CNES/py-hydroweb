# © CNES

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

import pytest

import py_hydroweb

LOGGER = logging.getLogger(__name__)


@pytest.mark.skip("Integration test deactivated by default")
class TestPyHydroweb:
    """
    Disclaimer: To run this tests, you must define:
        HYDROWEB_ENDPOINT environment variable with a valid hydroweb endpoint API
        HYDROWEB_API_KEY environment variable with a valid api key for this endpoint
    """

    @pytest.fixture
    def hydroweb_endpoint(self) -> str:
        hydroweb_endpoint: str = os.environ.get("HYDROWEB_ENDPOINT")
        if hydroweb_endpoint:
            return hydroweb_endpoint
        raise ValueError("HYDROWEB_ENDPOINT environment variable must be defined to run integration tests!")

    def test_integration_without_mock(self, hydroweb_endpoint: str):

        # Create a client
        client: py_hydroweb.Client = py_hydroweb.Client(hydroweb_endpoint)

        # Initiate a new download basket
        basket: py_hydroweb.DownloadBasket = py_hydroweb.DownloadBasket("my_first_download")

        # Add a few collections in our basket
        basket.add_collection("HYDROWEB_LAKES_RESEARCH")
        basket.add_collection("HYDROWEB_LAKES_OPE", bbox=[17.6123, 4.53676, 54.7998, 18.04142])
        basket.add_collection(
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

        # Submit download request
        download_id: str = client.submit_download(basket)
        LOGGER.info(f"Download ID: {download_id}")
        assert download_id is not None

        # Get all workflows status
        last_update = datetime.now() + timedelta(hours=-1)
        statuses: dict[str, py_hydroweb.DownloadInfo] = client.get_downloads_info(last_update)
        LOGGER.info(f"All workflow statuses: {statuses}")
        assert download_id in statuses
        assert statuses[download_id].status in (
            py_hydroweb.DownloadInfo.Status.RUNNING,
            py_hydroweb.DownloadInfo.Status.CREATED,
            py_hydroweb.DownloadInfo.Status.COMPLETED,
        )

        # Get download status
        status: py_hydroweb.DownloadInfo = client.get_download_info(download_id)
        LOGGER.info(f"Status: {status}")
        assert status.status in (
            py_hydroweb.DownloadInfo.Status.RUNNING,
            py_hydroweb.DownloadInfo.Status.CREATED,
            py_hydroweb.DownloadInfo.Status.COMPLETED,
        )

        # Download file
        output_path: str = client.download_zip(download_id)
        LOGGER.info(f"Output file path: {output_path}")
        assert output_path is not None
        assert Path(output_path).is_file

        # Remove workflow
        client.delete_download(download_id)

        # Get download status again (not found since it does not exist any more)
        with pytest.raises(py_hydroweb.exceptions.ApiErrorException, match="404"):
            client.get_download_info(download_id)

    def test_template_example_full(self, hydroweb_endpoint: str):

        # Create a client
        client: py_hydroweb.Client = py_hydroweb.Client(hydroweb_endpoint)

        # Initiate a new download basket
        basket: py_hydroweb.DownloadBasket = py_hydroweb.DownloadBasket("test_template_example_full")

        # Add a few collections in our basket
        basket.add_collection("HYDROWEB_LAKES_OPE", bbox=[17.6123, 4.53676, 54.7998, 18.04142])

        # Submit download request
        download_id: str = client.submit_download(basket)

        # Download file
        downloaded_zip_path: str = client.download_zip(
            download_id, zip_filename="test_template_example_full.zip", output_folder="/app/tests/output"
        )
        print(downloaded_zip_path)

        # Remove workflow
        client.delete_download(download_id)

    def test_template_example_short(self, hydroweb_endpoint: str):

        # Create a client
        client: py_hydroweb.Client = py_hydroweb.Client(hydroweb_endpoint)

        # Initiate a new download basket
        basket: py_hydroweb.DownloadBasket = py_hydroweb.DownloadBasket("test_template_example_short")

        # Add a few collections in our basket
        basket.add_collection("HYDROWEB_LAKES_OPE", bbox=[17.6123, 4.53676, 54.7998, 18.04142])

        # Do download
        downloaded_zip_path: str = client.submit_and_download_zip(
            basket, zip_filename="test_template_example_short.zip", output_folder="/app/tests/output"
        )
        assert downloaded_zip_path == "/app/tests/output/test_template_example_short.zip"
