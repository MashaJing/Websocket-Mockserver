def test_delete_schedule_rule():
    def parameterize_rules():
        """rule: dict, list[dict]"""

    def prepare_rules():
        """client.reset_server()
        POST /admin/mapping/schedule
        {"channels": channels, "url_path": url_path, "message": message, "timeout": timeout}
        client.get_rules()
        """

    def delete_and_retrieve_rules():
        """DELETE /admin/mapping/schedule
        client.get_rules()
        """

    def verify_rules():
        """assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["schedule_rules_removed"] == 1
        assert rules["schedule rules"] == []
        assert rules["inbound rules"] == initial_inbound_rules
        assert rules["oneshot rules"] == initial_oneshot_rules
        """
