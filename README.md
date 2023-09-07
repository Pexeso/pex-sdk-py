[![docs](https://img.shields.io/badge/docs-reference-blue.svg)](https://docs.ae.pex.com/python/)
[![Language](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

# Attribution Engine SDK for Python

Python bindings for the [Attribution Engine SDK](https://docs.ae.pex.com).

### Installation

You can install the Python language bindings like this:

```
python3 -m venv env
. env/bin/activate
pip install git+https://github.com/Pexeso/ae-sdk-py.git
```

### Client

Before you can do any operation with the SDK you need to initialize a client.

```python
import pexae

client = pexae.Client(CLIENT_ID, CLIENT_SECRET)
```

If you want to test the SDK using the mockserver you need to mock the client:

```python
pexae.mock_client(client)
```

### Fingerprinting

A fingerprint is how the SDK identifies a piece of digital content.
It can be generated from a media file or from a memory buffer. The
content must be encoded in one of the supported formats and must be
longer than 1 second.

You can generate a fingerprint from a media file:

```python
ft = client.fingerprint_file("/path/to/file.mp4")
```

Or you can generate a fingerprint from a memory buffer:

```python
with open("/path/to/file.mp4", "rb") as fp:
    ft = client.fingerprint_buffer(fp.read())
```

Both the files and the memory buffers must be valid media content in
following formats:

```
Audio: aac
Video: h264, h265
```

**Important!** Keep in mind that generating a fingerprint is CPU bound
operation and might consume a significant amount of your CPU time.


### Metadata search

After the fingerprint is generated, you can use it to perform a metadata search.

```python
# Build the request.
request = pexae.MetadataSearchRequest(fingerprint=ft)

# Start the search.
future = client.start_metadata_search(request)

# Do something while waiting for the search to finish.

# Retrieve the result. This operation will block until
# the search is finished.
result = future.get()

# Do something with the result.
# ...
```


### License search

Performing a license search is very similar to metadata search.

```python
# Build the request.
request = pexae.LicenseSearchRequest(fingerprint=ft)

# Start the search.
future = client.start_license_search(request)

# Do something while waiting for the search to finish.

# Retrieve the result. This operation will block until
# the search is finished.
result = future.get()

# Do something with the result.
# ...
```

The most significant difference between the searches currently is in the
results they return. See MetadataSearchResult and LicenseSearchResult for
more information.
