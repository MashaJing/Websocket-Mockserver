def test_receive_oneshot_messages():
    def parameterize_messages_and_reconnection():
        """messages: [{"sequence": 1}], [{"sequence": 1}, {"sequence": 2}]
        reconnect: False, True
        """

    def prepare_oneshot_rules():
        """client.reset_server()
        POST /admin/mapping/oneshot
        {"url_path": "prices", "message": {"sequence": 1}}
        {"url_path": "prices", "message": {"sequence": 2}}
        """

    def receive_messages():
        """ws://localhost:3003/ws/prices
        websocket.recv()
        websocket.close()
        ws://localhost:3003/ws/prices
        websocket.recv()
        """

    def verify_messages():
        """assert received_messages == [{"sequence": 1}, {"sequence": 2}]
        assert received_messages.count(message) == 1
        """
