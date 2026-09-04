def test_reset_all_rule_types():
    def parameterize_initial_rules():
        """initial_rules: 1, n
        rule_types: "inbound", "oneshot", "schedule"
        """

    def prepare_rules():
        """POST /admin/mapping/inbound
        POST /admin/mapping/oneshot
        POST /admin/mapping/schedule
        client.get_rules()
        """

    def reset_and_retrieve_rules():
        """POST /admin/mapping/reset
        client.reset_server()
        client.get_rules()
        """

    def verify_rules():
        """assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert rules["inbound rules"] == []
        assert rules["oneshot rules"] == []
        assert rules["schedule rules"] == []
        """
