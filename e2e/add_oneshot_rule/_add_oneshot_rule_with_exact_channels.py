def test_add_oneshot_rule_with_exact_channels():
    def parameterize_channels():
        """("quotes,trades", "trades,orders", True)
        ("quotes,trades", "orders", False)
        ("quotes", None, False)
        """

    def prepare_oneshot_rule():
        """client.reset_server()
        POST /admin/mapping/oneshot
        {"channels": "quotes,trades", "message": {"type": "channel-exact"}}
        """

    def connect_and_receive_message():
        """ws://localhost:3003/ws/prices
        X-Websocket-Channels: channels
        websocket.recv()
        """

    def verify_message():
        """assert (received_message is not None) is expected
        assert bool(set(rule["channels"].split(",")) & set(channels.split(","))) is expected
        """
