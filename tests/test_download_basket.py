# © CNES

import logging

from pytest import raises

import py_hydroweb.download_basket
from py_hydroweb.exceptions import CollectionUnicityException

LOGGER = logging.getLogger(__name__)


class TestDownloadBasket:
    def test_download_basket_1(self):
        basket: py_hydroweb.DownloadBasket = py_hydroweb.DownloadBasket("test_download_basket_1")

        # Add a first collection with a custom correlation id
        basket.add_collection("HYDROWEB_LAKES_RESEARCH", correlation_id="my awesome correlation id")

        assert basket.as_dict() == {
            "workflowName": "test_download_basket_1",
            "collections": [
                {
                    "collectionId": "HYDROWEB_LAKES_RESEARCH",
                    "correlationId": "my awesome correlation id",
                    "folder": "HYDROWEB_LAKES_RESEARCH",
                    "filters": {
                        "bbox": None,
                        "intersects": None,
                        "intersectsRefs": None,
                        "datetime": None,
                        "query": None,
                    },
                }
            ],
        }

        # Add a second collection without correlation id
        # (it is going to be generated)
        basket.add_collection("HYDROWEB_LAKES_RESEARCH")

        assert basket.as_dict() == {
            "workflowName": "test_download_basket_1",
            "collections": [
                {
                    "collectionId": "HYDROWEB_LAKES_RESEARCH",
                    "correlationId": "my awesome correlation id",
                    "folder": "HYDROWEB_LAKES_RESEARCH/my awesome correlation id",
                    "filters": {
                        "bbox": None,
                        "intersects": None,
                        "intersectsRefs": None,
                        "datetime": None,
                        "query": None,
                    },
                },
                {
                    "collectionId": "HYDROWEB_LAKES_RESEARCH",
                    "correlationId": "HYDROWEB_LAKES_RESEARCH_2",
                    "folder": "HYDROWEB_LAKES_RESEARCH/HYDROWEB_LAKES_RESEARCH_2",
                    "filters": {
                        "bbox": None,
                        "intersects": None,
                        "intersectsRefs": None,
                        "datetime": None,
                        "query": None,
                    },
                },
            ],
        }

        # Add a third collection without correlation id
        # (it is also going to be generated)
        basket.add_collection("HYDROWEB_LAKES_RESEARCH")

        assert basket.as_dict() == {
            "workflowName": "test_download_basket_1",
            "collections": [
                {
                    "collectionId": "HYDROWEB_LAKES_RESEARCH",
                    "correlationId": "my awesome correlation id",
                    "folder": "HYDROWEB_LAKES_RESEARCH/my awesome correlation id",
                    "filters": {
                        "bbox": None,
                        "intersects": None,
                        "intersectsRefs": None,
                        "datetime": None,
                        "query": None,
                    },
                },
                {
                    "collectionId": "HYDROWEB_LAKES_RESEARCH",
                    "correlationId": "HYDROWEB_LAKES_RESEARCH_2",
                    "folder": "HYDROWEB_LAKES_RESEARCH/HYDROWEB_LAKES_RESEARCH_2",
                    "filters": {
                        "bbox": None,
                        "intersects": None,
                        "intersectsRefs": None,
                        "datetime": None,
                        "query": None,
                    },
                },
                {
                    "collectionId": "HYDROWEB_LAKES_RESEARCH",
                    "correlationId": "HYDROWEB_LAKES_RESEARCH_3",
                    "folder": "HYDROWEB_LAKES_RESEARCH/HYDROWEB_LAKES_RESEARCH_3",
                    "filters": {
                        "bbox": None,
                        "intersects": None,
                        "intersectsRefs": None,
                        "datetime": None,
                        "query": None,
                    },
                },
            ],
        }

    def test_download_basket_2(self):
        basket: py_hydroweb.DownloadBasket = py_hydroweb.DownloadBasket("test_download_basket_2")

        # Add a first collection without correlation id
        # (collection id will be used by default since it is the first occurrence of this collection)
        basket.add_collection("HYDROWEB_LAKES_RESEARCH")

        assert basket.as_dict() == {
            "workflowName": "test_download_basket_2",
            "collections": [
                {
                    "collectionId": "HYDROWEB_LAKES_RESEARCH",
                    "correlationId": "HYDROWEB_LAKES_RESEARCH",
                    "folder": "HYDROWEB_LAKES_RESEARCH",
                    "filters": {
                        "bbox": None,
                        "intersects": None,
                        "intersectsRefs": None,
                        "datetime": None,
                        "query": None,
                    },
                }
            ],
        }

        # Add a second collection without correlation id
        # (it is going to be generated and first correlation id will be modified)
        basket.add_collection("HYDROWEB_LAKES_RESEARCH")

        assert basket.as_dict() == {
            "workflowName": "test_download_basket_2",
            "collections": [
                {
                    "collectionId": "HYDROWEB_LAKES_RESEARCH",
                    "correlationId": "HYDROWEB_LAKES_RESEARCH",
                    "folder": "HYDROWEB_LAKES_RESEARCH/HYDROWEB_LAKES_RESEARCH",  # folder has been modified automatically
                    "filters": {
                        "bbox": None,
                        "intersects": None,
                        "intersectsRefs": None,
                        "datetime": None,
                        "query": None,
                    },
                },
                {
                    "collectionId": "HYDROWEB_LAKES_RESEARCH",
                    "correlationId": "HYDROWEB_LAKES_RESEARCH_2",
                    "folder": "HYDROWEB_LAKES_RESEARCH/HYDROWEB_LAKES_RESEARCH_2",
                    "filters": {
                        "bbox": None,
                        "intersects": None,
                        "intersectsRefs": None,
                        "datetime": None,
                        "query": None,
                    },
                },
            ],
        }

        # Add a (collection id, correlation id) tuple that already exists
        with raises(CollectionUnicityException):
            basket.add_collection("HYDROWEB_LAKES_RESEARCH", "HYDROWEB_LAKES_RESEARCH_2")
