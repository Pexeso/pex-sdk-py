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

    req = pex.LicenseSearchRequest(fingerprint=ft)
    try:
        client = pex.NewClient("client01", "secret01")
        fut = client.start_license_search(req)
        # do something else in the meantime
        res = fut.get()
        blocked = res.policies.get('US') == pex.BasicPolicy.BLOCK
        print("blocked in US: {}".format(blocked))
    except pex.AEError as err:
        pass  # handle error


********************************************************************************
API reference
********************************************************************************

.. autoclass:: pex.LicenseSearchRequest

.. autoclass:: pex.RightsholderPolicy()

.. autoclass:: pex.Asset()

.. autoclass:: pex.Segment()

.. autoclass:: pex.LicenseSearchMatch()

.. autoclass:: pex.LicenseSearchResult()

.. autoclass:: pex.LicenseSearchFuture()
