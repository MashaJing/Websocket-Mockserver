def test_add_schedule_rule_with_timeout():
    def parameterize_timeout():
        """timeout: 0.1, 0.2, 0.5"""

    def prepare_schedule_rule():
        """client.reset_server()
        POST /admin/mapping/schedule
        {"message": {"type": "periodic"}, "timeout": timeout}
        """

    def receive_messages():
        """ws://localhost:3003/ws/{connection_path}
        websocket.recv(count=3)
        """

    def verify_messages():
        """assert received_messages == [{"type": "periodic"}] * 3
        assert all(interval >= timeout for interval in intervals)
        """
