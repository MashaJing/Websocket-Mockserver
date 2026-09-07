def test_delete_oneshot_rule():
    def parameterize_rules():
        """rule: dict, list[dict]"""

    def prepare_rules():
        """client.reset_server()
        POST /admin/mapping/oneshot
        {"channels": channels, "url_path": url_path, "message": message, "timeout": timeout}
        client.get_rules()
        """

    def delete_and_retrieve_rules():
        """DELETE /admin/mapping/oneshot
        client.get_rules()
        """

    def verify_rules():
        """assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["oneshot_rules_removed"] == 1
        assert rules["oneshot rules"] == []
        assert rules["inbound rules"] == initial_inbound_rules
        assert rules["schedule rules"] == initial_schedule_rules
        """
