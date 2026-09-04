def test_add_oneshot_rule_with_channel_pattern():
    def parameterize_channels():
        """("^quotes-[0-9]+$", "quotes-42", True)
        ("^quotes-[0-9]+$", "quotes-live", False)
        ("^quotes-[0-9]+$", "orders,quotes-7", True)
        """

    def prepare_oneshot_rule():
        """client.reset_server()
        POST /admin/mapping/oneshot
        {"channels_pattern": channels_pattern, "message": {"type": "channel-pattern"}}
        """

    def connect_and_receive_message():
        """ws://localhost:3003/ws/prices
        X-Websocket-Channels: channels
        websocket.recv()
        """

    def verify_message():
        """assert (received_message is not None) is expected
        assert any(
            re.fullmatch(channels_pattern, channel)
            for channel in channels.split(",")
        ) is expected
        """
