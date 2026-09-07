def test_receive_schedule_messages():
    def parameterize_schedule_rules():
        """timeout: 0.1, 0.2, 0.5
        message: {"type": "quote", "payload": {"instrument": "AAPL"}}
        schedule_rules: 1, n
        """

    def prepare_schedule_rule():
        """client.reset_server()
        POST /admin/mapping/schedule
        {
            "url_path": "prices",
            "message": {"type": "quote", "payload": {"instrument": "AAPL"}},
            "timeout": timeout,
        }
        """

    def receive_messages():
        """ws://localhost:3003/ws/prices
        websocket.recv(count=3)
        websocket.close()
        """

    def verify_messages():
        """assert received_messages == [rule["message"]] * 3
        assert all(interval >= timeout for interval in intervals)
        assert websocket.closed
        """
