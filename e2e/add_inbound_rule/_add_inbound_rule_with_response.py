def test_add_inbound_rule_with_response():
    def parameterize_response():
        """({"type": "pong"}, {"type": "pong"})
        ("pong", "pong")
        (42, "42")
        """

    def prepare_inbound_rule():
        """client.reset_server()
        POST /admin/mapping/inbound
        {"type": "ping", "response": response}
        """

    def send_message():
        """ws://localhost:3003/ws/{connection_path}
        websocket.send({"type": "ping"})
        websocket.recv()
        """

    def verify_response():
        """assert received_message == expected_message"""
