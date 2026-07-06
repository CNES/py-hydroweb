# © CNES

"""
DownloadBasket class
"""

from typing import List

from py_hydroweb.collection import Collection
from py_hydroweb.exceptions import CollectionUnicityException


class DownloadBasket:
    """A description of a basket of collections to be downloaded"""

    # User-chosen name for this download
    download_name: str

    # Map of collections indexed by (collection_id, correlation_id) tuple
    collections: dict

    def __init__(
        self,
        download_name: str,
    ):
        self.download_name = download_name
        # Initialize an empty set of collections
        self.collections = {}

    def add_collection(
        self,
        collection_id: str,
        correlation_id: str = None,
        folder: str = None,
        bbox: List[float] = None,
        intersects: dict = None,
        intersects_refs: List[str] = None,
        datetime: str = None,
        query: dict = None,
    ):
        """Add a collection to a download basket"""

        # Count number of occurrences for this collection
        current_count = len(self.collections.get(collection_id, {}))

        # Unless "folders" are explicitely provided, zip content will be organized as follow:
        # For one occurence of a collection: COLLECTION_ID/<data>
        # For several occurences: COLLECTION_ID/CORRELLATION_ID/<data_1>
        #                         COLLECTION_ID/CORRELLATION_ID_2/<data_2>
        #                         ...
        #                         COLLECTION_ID/CORRELLATION_ID_N/<data_3>
        # with correlation ids themselves defaulting to collection ids is not provided
        if current_count == 0:
            # First occurrence for this collection: correlation id and folder default to collection id (unless provided)
            correlation_id = correlation_id if correlation_id else collection_id
            folder = folder if folder else collection_id
        else:
            # 2nd or more occurrence for this collection
            if current_count == 1:
                # 2nd occurrence for this collection: adapt the folder of the first occurrence
                first_collection = next(iter(self.collections[collection_id].values()))
                if first_collection.folder == collection_id:
                    first_collection.folder = f"{collection_id}/{first_collection.correlation_id}"
            # general case for a multi-occurrence collection
            correlation_id = correlation_id if correlation_id else f"{collection_id}_{current_count+1}"
            folder = folder if folder else f"{collection_id}/{correlation_id}"

        # If the (collection id, correlation id) entry already exists, raise an error
        if collection_id in self.collections and correlation_id in self.collections[collection_id]:
            raise CollectionUnicityException(
                f"Collection with ID {collection_id} and correlation ID {correlation_id} already exists in this basket!"
            )

        # We add this collection to this basket
        new_collection: Collection = Collection(
            collection_id, correlation_id, folder, bbox, intersects, intersects_refs, datetime, query
        )
        if collection_id in self.collections:
            self.collections[collection_id][correlation_id] = new_collection
        else:
            self.collections[collection_id] = {correlation_id: new_collection}

    def as_dict(self) -> str:
        """Transforms a download object into a dict matching the input format expected by hydroweb.next"""
        return {
            "workflowName": self.download_name,
            "collections": [c2.as_dict() for c1 in self.collections.values() for c2 in c1.values()],
        }
