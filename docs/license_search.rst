################################################################################
License search
################################################################################

To perform a license search a :ref:`client` has to be initialized first. Once
initialized, the actual search is performed in two steps. First, the search is
started by calling :meth:`LicenseSearch.start` and passing it an instance of
:class:`LicenseSearchRequest`. This will perform a network operation and might
raise :class:`AEError` if something goes wrong, e.g. there is network problem
or the request passed as a parameter is invalid. The call will return an
instance of :class:`LicenseSearchFuture` that can then be used to retrieve the
search result.


.. code-block:: python

    req = pexae.LicenseSearchRequest(fingerprint=ft)
    try:
        client = pexae.NewClient("client01", "secret01")
        fut = client.start_license_search(req)
        # do something else in the meantime
        res = fut.get()
        blocked = res.policies.get('US') == pexae.BasicPolicy.BLOCK
        print("blocked in US: {}".format(blocked))
    except pexae.AEError as err:
        pass  # handle error


********************************************************************************
API reference
********************************************************************************

.. autoclass:: pexae.LicenseSearchRequest

.. autoclass:: pexae.RightsholderPolicy()

.. autoclass:: pexae.Asset()

.. autoclass:: pexae.Segment()

.. autoclass:: pexae.LicenseSearchMatch()

.. autoclass:: pexae.LicenseSearchResult()

.. autoclass:: pexae.LicenseSearchFuture()
