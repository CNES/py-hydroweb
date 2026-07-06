# Py Hydroweb

**py_hydroweb** is a simple library providing python facilities to search and download hydrological data from the [hydroweb.next](https://hydroweb.next.theia-land.fr) platform.

[![hydroweb.next](https://raw.githubusercontent.com/CNES/py-hydroweb/main/ressources/opengraph-image.jpg)](https://hydroweb.next.theia-land.fr)

For more information about the platform, to create an account and an API key, visit our website at https://hydroweb.next.theia-land.fr.


```python
>>> import py_hydroweb
>>> client = py_hydroweb.Client(api_key="<my_personal_hydroweb_api_key>")
>>> basket = py_hydroweb.DownloadBasket("my_download_basket")
>>> basket.add_collection("HYDROWEB_LAKES_OPE", bbox=[17.6123, 4.53676, 54.7998, 18.04142])
>>> client.submit_and_download_zip(basket)
```

After you created your account and your api key on the website, this simple piece of code will download (in your current folder) a zip file containing the collection(s) you asked for. 
Products are filtered according to how you called `add_collection` (in this example with a simple bbox, but no temporal filter).

## Installing Py Hydroweb and Supported Versions

Py Hydroweb is available on PyPI and can be installed like any other Python package (also works with conda or other environment managers):

```console
$ python -m pip install py_hydroweb
```

Py Hydroweb officially supports Python 3.8+.

## API Reference and User Guide

To prepare and run a download request, follow step by step instruction below.

### 1. Create an instance of a client

```python
>>> client: py_hydroweb.Client = py_hydroweb.Client(
        hydroweb_api_url="<an_hydroweb_api_endpoint>", 
        api_key="<my_personal_hydroweb_api_key>"
    )
```

Client's constructor parameters:
- `hydroweb_api_url: str` (optional) Hydroweb API base URL. Default value is https://hydroweb.next.theia-land.fr/api and except for test purpose, there is no need to change it.
- `api_key: str = None` (optional) Hydroweb API Key that you can get from our website once you created your account
 
__Alternative__: if **not** passed in the above constructor, the API Key **must be** defined by setting the **HYDROWEB_API_KEY** environment variable: `export HYDROWEB_API_KEY=<my_personal_hydroweb_api_key>`

### 2. Create a new empty download basket

```python
>>> basket: py_hydroweb.DownloadBasket = py_hydroweb.DownloadBasket(download_name="my_download_basket")
```

DownloadBasket's constructor parameters:
- `download_name: str` (mandatory) Name for the download to be prepared

### 3. Add as many collections as you want to this basket

```python
>>> basket.add_collection(
        collection_id="HYDROWEB_LAKES_OPE", 
        bbox=[17.6123, 4.53676, 54.7998, 18.04142]
    )
>>> basket.add_collection(
        collection_id="LIS_SNT_YEARLY",
        correlation_id="LIS_SNT_YEARLY",
        folder="lis/snt/",
        bbox=[17.6123, 4.53676, 54.7998, 18.04142],
        intersects={
            "coordinates": [
                [[21.282, 17.656], [21.282, 14.221], [26.797, 14.221], [26.797, 17.656], [21.282, 17.656]]
            ],
            "type": "Polygon",
        },
        intersects_refs=["NATURAL_EARTH_COUNTRIES.Sudan"],
        datetime="2022-01-01T00:00:00Z/2022-12-31T23:59:59Z",
        query={
            "start_datetime": {"lte": "2024-02-03T00:00:00.000Z"},
            "end_datetime": {"gte": "2023-02-02T00:00:00.000Z"},
        },
    )
```

add_collection method parameters:
- `collection_id: str` (mandatory) Collection identifier (as specified by hydroweb.next platform, browse [here](https://radiantearth.github.io/stac-browser/#/external/hydroweb.next.theia-land.fr/api/catalog/stac) to discover available collection ids)
- `correlation_id: str = None` (optional) Correlation identifier (in case we find several time the same collection ID in the download basket). If not provided, it defaults to *COLLECTION_ID* for first occurrence of given collection, then *COLLECTION_ID_2*, ..., *COLLECTION_ID_N*.
- `folder: str = None` (optional) Desired folder subpath in the resulting zip to be downloaded. If not provided, zip structure defaults as follow:
    - For a single occurence of a collection in basket: *COLLECTION_ID/...*
    - For several occurences in basket: *COLLECTION_ID/CORRELATION_ID/...* 
        - with *CORRELATION_ID* itself defaulting to *COLLECTION_ID_N* if not provided, leading to a final default structure like:
            - *COLLECTION_ID/COLLECTION_ID/...*
            - *COLLECTION_ID/COLLECTION_ID_2/...*
            - *...*
            - *COLLECTION_ID/COLLECTION_ID_N/...*
- `bbox: List[float] = None` (optional) Geographical bounding box
    - for more information see [here](https://github.com/radiantearth/stac-api-spec/blob/release/v1.0.0/item-search/README.md)
- `intersects: dict = None` (optional) Geojson geometry to search for items by performing intersection between their own geometry and this geometry 
    - for more information see [here](https://github.com/radiantearth/stac-api-spec/blob/release/v1.0.0/item-search/README.md)
- `intersects_refs: List[str] = None` (optional) List of toponyms (aliases) to search for items by performing intersection between their own geometry and this geometry  
    - toponyms are feature identifiers that are drawn from a predefined set of collections 
    - to discover them, you can use the `Where` search bar on [hydroweb-next](https://hydroweb.next.theia-land.fr)
    - non-exhaustive list of examples:
        - NATURAL_EARTH_COUNTRIES.France
        - HYDRO_BASINS_03.456
        - HYDRO_BASINS_04.4561
        - HYDRO_BASINS_05.45610
        - HYDRO_BASINS_06.456100
        - S2_TILES_MASK.32TMN
        - HYDROWEB_LAKES_OPE.L_leman
        - HYDROWEB_LAKES_RESEARCH.L_lagullinas
        - HYDROWEB_RIVERS_OPE.R_GARONNE_GARONNE_KM0191
        - HYDROWEB_RIVERS_RESEARCH.R_GARONNE_GARONNE_KM0164
        - SWOT_PRIOR_LAKE_DATABASE.2160028212
        - SWOT_PRIOR_RIVER_DATABASE.23214400101
        - SWOT_L2_HRMASK_SCENES_NOM.456_002F
        - SWOT_L2_HRMASK_TILES_NOM.001_095L
        - HUBEAU_HYDROMETRIE.1232000101
        - S3_LPP_LAKE_WATER_LEVEL.L_1230001592_S3A_554
- `datetime: str = None` (optional) Single date+time, or a range ('/' separator) 
    - for more information see [here](https://github.com/radiantearth/stac-api-spec/blob/release/v1.0.0/item-search/README.md)
    - **warning**: this parameter refers to the **ingestion** datetime of the data in the catalog and should generally not be used. If you want to refer to product date and time, use the `query` parameter below
- `query: dict = None` (optional) Json query as specified by the query plugin of STAC API 
    - for more information see [here](https://github.com/stac-api-extensions/query/blob/v1.0.0/README.md)
    - **warning 1**: start_datetime and end_datetime refer to the **product** datetime. They are common-metadata as defined [here](https://github.com/radiantearth/stac-api-spec/blob/v1.0.0/stac-spec/item-spec/common-metadata.md#date-and-time-range).
    - **warning 2**: in case of a "reference collection" (without a temporal dimension), start_datetime and end_datetime will be ignored.

### 4. Submit your request and download your basket

#### 4.A. (Option A) Dissociated submission and download

##### Step 1: submit your download request

Once you are done adding collections to your basket, you can now submit your download request.

This will return an identifier that you will be able to use later to download your zip file.

```python
>>> download_id: str = client.submit_download(download_basket=basket)
```

submit_download method parameters:
- `download_basket: DownloadBasket` (mandatory) Download basket containing requested collections

submit_download return value:
- `download_id: str` identifier of your download request

##### Step 2: download your zip file

Once you submitted your download request, you can ask to download the resulting zip file.

This method automatically waits for your download request to be ready before it proceeds with zip download.

```python
>>> downloaded_zip_path: str = client.download_zip(
        download_id=download_id, zip_filename="my_data.zip", output_folder="./output"
    )
```

download_zip method parameters:
- `download_id: str` (mandatory) The identifier of the previously submitted download request
- `zip_filename: str = None` (optional) An output file name for the resulting zip - if not provided, file name will be <download_id>.zip
- `output_folder: str = None` (optional) A (relative or absolute) path to an **existing** folder - if not provided, download will happen in current folder

download_zip return value:
- `downloaded_zip_path: str` The (relative or absolute) path of the downloaded zip file

#### 4.B. (Option B) Grouped submission and download

##### Single step: submit your download request and download your zip file

Alternatively, once you are done adding collections to your basket, you can all together submit your download request, wait for it to be ready and proceed with zip download.

```python
>>> downloaded_zip_path: str = client.submit_and_download_zip(
        download_basket=basket, zip_filename="my_data.zip", output_folder="./output"
    )
```

submit_and_download_zip method parameters:
- `download_basket: DownloadBasket` (mandatory) Download basket containing requested collections
- `zip_filename: str = None` (optional) An output file name for the resulting zip - if not provided, file name will be <download_id>.zip
- `output_folder: str = None` (optional) A (relative or absolute) path to an **existing** folder - if not provided, download will happen in current folder

submit_and_download_zip return value:
- `downloaded_zip_path: str` The (relative or absolute) path of the downloaded zip file

### 5. Other methods provided by the Client class

#### Check the status/progress of a single download request

```python
>>> status: py_hydroweb.DownloadInfo = client.get_download_info(download_id=download_id)
```

get_download_info method parameters:
- `download_id: str` (mandatory) The identifier of the previously submitted download request

get_download_info return value:
- `status: py_hydroweb.DownloadInfo` Object containing a status (CREATED, RUNNING, COMPLETED, FAILED, ...) and a percentage of progress

#### Check the status/progress of all you download requests (paginated)

```python
>>> last_update = datetime.now() + timedelta(hours=-1)
>>> statuses: dict[str, py_hydroweb.DownloadInfo] = client.get_downloads_info(
        last_update=last_update, page=0, size=20
    )
```

get_downloads_info method parameters:
- `last_update: date = None` (optional) An optional date to retrieve only download requests updated after this date - if not provided, all your requests will be retrieved
- `page: int = None` (optional) Pagination parameter: index (starting at 0) of the page we want to retrieve - if neither `page` nor `size` are provided, there will be no pagination and all results will be returned at once
- `size: int = None` (optional) Pagination parameter: number of elements per page - if neither `page` nor `size` are provided, there will be no pagination and all results will be returned at once

get_downloads_info return value:
- `statuses: dict[str, py_hydroweb.DownloadInfo]` Dict where keys are download id and values are objects containing a status (CREATED, RUNNING, COMPLETED, FAILED, ...) and a percentage of progress

#### Delete a download request

The history of your download requests will automatically get cleaned after a certain amout of time. 
You can also clean it manually provided that status is no longer CREATED nor RUNNING.

```python
>>> client.delete_download(download_id=download_id)
```

delete_download method parameters:
- `download_id: str` (mandatory) The identifier of the download request to be removed

## Troubleshooting

### Error code

In case of an error during the downloading process, a specific message and an error code are included in the download information payload.
- `UNEXPECTED_ERROR` : Please contact support team to handle this unexpected issue.
- `EMPTY_SELECTION` : Your basket does not contain any data.
- `WHOLE_QUOTA_EXCEEDED` : The total size of the files to download exceeds the whole quota.
- `BLOCKED_WORKFLOWS_LIMIT_REACHED` : Total blocked workflows exceeds the maximum allowed.