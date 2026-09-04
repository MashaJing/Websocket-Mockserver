def test_get_empty_rules():
    def prepare_client():
        """http://localhost:3003
        WebSocketMockServerClient(
            base_url="http://localhost:3003",
            connection_path="prices",
        )
        client.reset_server()
        """

    def retrieve_rules():
        """client.get_rules()"""

    def verify_rules():
        """assert response.status_code == 200
        assert rules == {
            "oneshot rules": [],
            "inbound rules": [],
            "schedule rules": [],
        }
        """
