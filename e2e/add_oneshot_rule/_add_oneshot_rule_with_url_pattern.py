def test_add_oneshot_rule_with_url_pattern():
    def parameterize_path():
        """("^prices/[A-Z]+$", "prices/AAPL", True)
        ("^prices/[A-Z]+$", "prices/aapl", False)
        ("^prices/[A-Z]+$", "orders/AAPL", False)
        """

    def prepare_oneshot_rule():
        """client.reset_server()
        POST /admin/mapping/oneshot
        {"url_pattern": url_pattern, "message": {"type": "path-pattern"}}
        """

    def connect_to_path():
        """ws://localhost:3003/ws/{connection_path}
        websocket.recv()
        """

    def verify_message():
        """assert (received_message is not None) is expected
        assert bool(re.fullmatch(url_pattern, connection_path)) is expected
        """
