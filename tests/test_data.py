# --------------- Dedpulication Test Data ---------------
asset_req_json = {
    "id": "a9",
    "type": "domain",
    "value": "CloudOrbit.com",
    "status": "stale",
    "source": "scan",
    "tags": [
        "root"
    ],
    "metadata": {
        "email": "@CloudOrbit.com"
    }
}

updated_asset_req_json = {
    "id": "a9",
    "type": "domain",
    "value": "CloudOrbit.com",
    "status": "active",
    "source": "import",
    "tags": [
        "prod", "production"
    ],
    "metadata": {
        "description": "Domain for Cloud Orbit Company",
    }
}

merged_expected_res_json = {
    "id": "a9",
    "type": "domain",
    "value": "CloudOrbit.com",
    "status": "active",
    "source": "import",
    "tags": [
        "prod", "production", "root"
    ],
    "metadata": {
        "email": "@CloudOrbit.com",
        "description": "Domain for Cloud Orbit Company",
    }
}

# --------------- Graph and Filtering Test Data ---------------
filter_value_ex_ids = ["a1", "a2","a3","a8"] # value like ex
sort_desc_by_first_seen_ids = ["a8", "a7","a6","a5", "a4", "a3", "a2", "a1"] # desc order of first_seen
filter_value_ex_tags_pub_ids = ["a1","a3","a8"] # value like ex & tags = pub
filter_value_ex_tags_pub_root_ids = ["a1"] # value like ex & tags = pub & tags = root

bulk_related_assets_json =  [
    {
        "id": "a1",
        "type": "domain",
        "value": "example.com",
        "status": "active",
        "source": "scan",
        "tags": [
            "root","pub"
        ],
        "metadata": {}
    },
    {
        "id": "a2",
        "type": "subdomain",
        "value": "api.example.com",
        "status": "active",
        "source": "scan",
        "tags": [
            "prod"
        ],
        "metadata": {},
        "parent": "a1"
    },
    {
        "id": "a3",
        "type": "certificate",
        "value": "CN=api.example.com",
        "status": "active",
        "source": "scan",
        "tags": [
            "pub"
        ],
        "metadata": {
            "issuer": "Let’s Encrypt",
            "expires": "2025-01-02"
        },
        "covers": "a2"
    },
    {
        "id": "a4",
        "type": "ip_address",
        "value": "10.10.10.1",
        "status": "active",
        "source": "scan",
        "parent": "a2",
        "tags": [
            "pub"
        ]
    },
    {
        "id": "a5",
        "type": "technology",
        "value": "SSL",
        "status": "active",
        "source": "scan",
        "parent": "a2",
        "tags": [
            "public"
        ]
    },
    {
        "id": "a6",
        "type": "service",
        "value": "Web Browsing",
        "status": "active",
        "source": "scan",
        "parent": "a4",
        "tags": [
            "pub"
        ],
        "metadata": {
            "expires": "2026-06-25"
        }
    },
    {
        "id": "a7",
        "type": "technology",
        "value": "High Availability",
        "status": "active",
        "source": "scan",
        "parent": "a6",
        "tags": [
            "test"
        ],
        "metadata": {
            "expires": "2026-07-26"
        }
    },
    {
        "id": "a8",
        "type": "certificate",
        "value": "CN=example.com",
        "status": "active",
        "source": "scan",
        "tags": [
            "prod","pub"
        ],
        "metadata": {
            "issuer": "Let’s Secure",
            "expires": "2026-06-26"
        },
        "parent": "a1"
    },
]

expected_graph_ids = {
    "id": "a1",
    "children": [
        {
            "id": "a2",
            "children": [
                {
                    "id": "a3",
                    "children": []
                },
                {
                    "id": "a4",
                    "children": [
                        {
                            "id": "a6",
                            "children": [
                                {
                                    "id": "a7",
                                    "children": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "a5",
                    "children": []
                }
            ]
        },
        {
            "id": "a8",
            "children": []
        }
    ]
}

