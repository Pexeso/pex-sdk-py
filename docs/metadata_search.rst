################################################################################
Metadata search
################################################################################

To perform a metadata search a :ref:`client` has to be initialized first. Once
initialized, the actual search is performed in two steps. First, the search is
started by calling :meth:`MetadataSearch.start` and passing it an instance of
:class:`MetadataSearchRequest`. This will perform a network operation and might
raise :class:`AEError` if something goes wrong, e.g. there is network problem
or the request passed as a parameter is invalid. The call will return an
instance of :class:`MetadataSearchFuture` that can then be used to retrieve the
search result.

.. code-block:: python

    req = pexae.MetadataSearchRequest(fingerprint=ft)
    try:
        client = pexae.NewClient("client01", "secret01")
        future = client.start_metadata_search(req)
        # do something else in the meantime
        res = future.get()
        print("lookup {} returned {} matches".format(res.lookup_id, len(res.matches)))
    except pexae.AEError as err:
        pass  # handle error


********************************************************************************
API reference
********************************************************************************

.. autoclass:: pexae.MetadataSearchRequest

.. autoclass:: pexae.Asset()

.. autoclass:: pexae.Segment()

.. autoclass:: pexae.MetadataSearchMatch()

.. autoclass:: pexae.MetadataSearchResult()

.. autoclass:: pexae.MetadataSearchFuture()
