def test_add_inbound_rule_with_exact_type():
    def parameterize_type():
        """("subscribe", True)
        ("unsubscribe", False)
        ("Subscribe", False)
        """

    def prepare_inbound_rule():
        """client.reset_server()
        POST /admin/mapping/inbound
        {"type": "subscribe", "response": {"type": "subscribed"}}
        """

    def send_messages():
        """ws://localhost:3003/ws/{connection_path}
        websocket.send({"type": message_type})
        """

    def verify_response():
        """assert (received_message is not None) is expected"""
