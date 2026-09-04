def test_add_oneshot_rule_with_timeout():
    def parameterize_timeout():
        """timeout: 0, 0.2, 0.5"""

    def prepare_oneshot_rule():
        """client.reset_server()
        POST /admin/mapping/oneshot
        {"message": {"type": "delayed-oneshot"}, "timeout": timeout}
        """

    def connect_and_receive_message():
        """ws://localhost:3003/ws/{connection_path}
        connected_at = time.monotonic()
        websocket.recv()
        received_at = time.monotonic()
        """

    def verify_message():
        """assert received_at - connected_at >= timeout
        assert received_messages == [{"type": "delayed-oneshot"}]
        """
