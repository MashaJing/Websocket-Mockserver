def test_add_oneshot_rule_with_exact_url_path():
    def parameterize_path():
        """("prices", "prices", True)
        ("prices", "orders", False)
        ("prices", "prices/AAPL", False)
        """

    def prepare_oneshot_rule():
        """client.reset_server()
        POST /admin/mapping/oneshot
        {"url_path": rule_path, "message": {"type": "path-exact"}}
        """

    def connect_to_path():
        """ws://localhost:3003/ws/{connection_path}
        websocket.recv()
        """

    def verify_message():
        """assert (received_message is not None) is expected
        assert (rule_path == connection_path) is expected
        """
