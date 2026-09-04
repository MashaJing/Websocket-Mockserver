import os
from argparse import ArgumentParser
from websocket_mockserver.server import RemoteMockServer

DEFAULT_PORT = 8000

mock_server = RemoteMockServer()
app = mock_server.app

if __name__ == "__main__":
    parser = ArgumentParser(description="Websocket mock server runner")
    parser.add_argument(
        "--port", "-p",
        type=int,
        help=f"The port on which the server will run (default: {DEFAULT_PORT})."
    )

    args = parser.parse_args()
    port = args.port or int(os.environ.get("PORT", DEFAULT_PORT))

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)