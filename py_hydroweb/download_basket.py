# © CNES

from typing import List

from py_hydroweb.collection import Collection
from py_hydroweb.exceptions import CollectionUnicityException


class DownloadBasket:
    """A description of a basket of collections to be downloaded"""

    # User-chosen name for this download
    download_name: str

    # Map of collections indexed by (collection_id, correlation_id) tuple
    collections: dict  # dict[str, dict[str, Collection]]

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
        datetime: str = None,
        query: dict = None,
    ):
        """Add a collection to a download basket"""

        # If no correlation identifier was given, we will have 3 cases:
        # - First product for this collection: correlation_id is simply equal to collection_id
        # - Second product for this collection: we rename the first correlation_id into product-1 and second will be product-2
        # - More than second product for this collection: we create a product-N correlation_id
        if not correlation_id:
            current_count = len(self.collections.get(collection_id, {}))
            if current_count == 0:
                correlation_id = collection_id
            else:
                if current_count == 1 and collection_id in self.collections[collection_id]:
                    # Rename the correlation id of the first element of this collection
                    first_collection: Collection = self.collections[collection_id].pop(collection_id)
                    first_collection.correlation_id = "product-1"
                    self.collections[collection_id][first_collection.correlation_id] = first_collection
                correlation_id = f"product-{current_count+1}"

        # If the (collection id, correlation id) entry already exists, raise an error
        if collection_id in self.collections and correlation_id in self.collections[collection_id]:
            raise CollectionUnicityException(
                f"Collection with ID {collection_id} and correlation ID {correlation_id} already exists in this basket!"
            )

        # We add this collection to this basket
        new_collection: Collection = Collection(
            collection_id, correlation_id, folder, bbox, intersects, datetime, query
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
