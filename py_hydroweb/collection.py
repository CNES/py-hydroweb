# © CNES

from dataclasses import dataclass
from typing import List


@dataclass
class Collection:
    """The description of a collection with all its filters"""

    # (mandatory) collection identifier
    # e.g. "HYDROWEB_LAKES_OPE"
    collection_id: str

    # (mandatory) correlation identifier (in case we find several time the same collection ID in the same download basket)
    # e.g. "HYDROWEB_LAKES_SELECTION1"
    correlation_id: str

    # (optional) Desired folder subpath in the resulting zip to be downloaded
    # e.g. "hydroweb/my/data/"
    folder: str = None

    # (optional) geographical bouding box
    # e.g. [17.6123, 4.53676, 54.7998, 18.04142]
    bbox: List[float] = None

    # (optional) geojson geometry to search for items by performing intersection between their geometry and this geometry
    # e.g. {"type":"Polygon","coordinates":[[[6,53],[7,53],[7,54],[6,54],[6,53]]]}
    intersects: dict = None

    # (optional) Single date+time, or a range ('/' separator), formatted to RFC 3339, section 5.6. Use double dots .. for open date ranges.
    # Warning: it refers to the *ingestion* datetime of the data in the catalog
    # e.g. "2019-01-01T00:00:00Z/2019-01-01T23:59:59Z"
    datetime: str = None

    # (optional) json query
    # Warning: start_datetime and end_datetime refer to the *product* datetime
    # e.g. {"start_datetime":{"lte":"2024-02-03T00:00:00.000Z"},"end_datetime":{"gte":"2023-02-02T00:00:00.000Z"}}
    query: dict = None

    def as_dict(self) -> str:
        """Transforms a collection object into a dict matching the input format expected by hydroweb.next"""
        return {
            "collectionId": self.collection_id,
            "correlationId": self.correlation_id,
            "folder": self.folder,
            "filters": {
                "bbox": self.bbox,
                "intersects": self.intersects,
                "datetime": self.datetime,
                "query": self.query,
            },
        }
