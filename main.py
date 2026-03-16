import os
from argparse import ArgumentParser
from websocket_mockserver.server import RemoteMockServer

mock_server = RemoteMockServer()
app = mock_server.app

if __name__ == "__main__":
    parser = ArgumentParser(description="Websocket mock server runner")
    parser.add_argument(
        "--port", "-p",
        type=int,
        help="The port on which the server will run (default: 8000)."
    )

    args = parser.parse_args()
    port = args.port or int(os.environ.get("PORT", 8000))

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)