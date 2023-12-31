#!/usr/bin/env python3

import json
import pex


CLIENT_ID = "#YOUR_CLIENT_ID_HERE"
CLIENT_SECRET = "#YOUR_CLIENT_SECRET_HERE"
#INPUT_FILE = "/path/to/file.mp3"
INPUT_FILE = "/Users/stepan/Downloads/query04.mp3"


def main():
    # Initialize and authenticate the client.
    client = pex.PexSearchClient(CLIENT_ID, CLIENT_SECRET)

    # Optionally mock the client. If a client is mocked, it will only
    # communicate with the local mockserver instead of production servers. This
    # is useful for testing.
    pex.mock_client(client)

    # Fingerprint a file. You can also fingerprint a buffer with
    #
    #   client.FingerprintBuffer([]byte).
    #
    # Both the files and the memory buffers
    # must be valid media content in following formats:
    #
    #   Audio: aac
    #   Video: h264, h265
    #
    # Keep in mind that generating a fingerprint is CPU bound operation and
    # might consume a significant amount of your CPU time.
    ft = client.fingerprint_file(INPUT_FILE)

    # Build the request.
    req = pex.PexSearchRequest(fingerprint=ft)

    # Start the search.
    future = client.start_search(req)

    # Retrieve the result.
    result = future.get()

    # Print the result.
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
