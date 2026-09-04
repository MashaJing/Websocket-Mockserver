def test_add_inbound_rule_with_payload():
    def parameterize_payload():
        """({"instrument": "AAPL", "depth": 2}, True)
        ({"instrument": "AAPL"}, True)
        ({"instrument": "MSFT"}, False)
        ({}, False)
        """

    def prepare_inbound_rule():
        """client.reset_server()
        POST /admin/mapping/inbound
        {
            "type": "subscribe",
            "payload": {"instrument": "AAPL"},
            "response": {"type": "payload-matched"},
        }
        """

    def send_message():
        """ws://localhost:3003/ws/{connection_path}
        websocket.send({"type": "subscribe", "payload": incoming_payload})
        """

    def verify_response():
        """assert (received_message is not None) is expected
        assert (rule["payload"].items() <= incoming_payload.items()) is expected
        """
