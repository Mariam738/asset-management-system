# --------------- Dedpulication Helper---------------
def assert_json_equal(req_json, data):
    for k, v in req_json.items():
        if k == "metadata":
            assert data.get("meta") == v
        else:
            assert data.get(k) == v


# --------------- Grpah Relationship Helper ---------------
# ensure parent ids and children ids hierarchy is correct
def assert_graph_equal(expected, actual):
    assert expected["id"] == actual["asset"]["id"] 

    assert len(expected["children"]) == len(actual["children"]) 

    for exp_child, act_child in zip(expected["children"], actual["children"]):
        assert_graph_equal(exp_child, act_child)
