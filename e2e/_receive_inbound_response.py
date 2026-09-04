def test_receive_inbound_response():
    def parameterize_matching_criteria():
        """channel, path, type, payload
        expected: bool
        """

    def prepare_inbound_rule():
        """client.reset_server()
        POST /admin/mapping/inbound
        {
            "channels": "quotes",
            "url_path": "prices",
            "type": "subscribe",
            "payload": {"instrument": "AAPL"},
            "response": {
                "type": "subscribed",
                "payload": {"instrument": "AAPL"},
            },
        }
        """

    def send_message():
        """ws://localhost:3003/ws/{connection_path}
        X-Websocket-Channels: {channels}
        websocket.send(message)
        websocket.recv()
        """

    def verify_response():
        """assert (received_message == rule["response"]) is expected"""
