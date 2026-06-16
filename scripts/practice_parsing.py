devices = [
    {
        "hostname": "spine1",
        "bgp_asn": 65001,
        "neighbors": [
            {"ip": "10.1.1.1", "remote_as": 65101, "state": "Established"},
            {"ip": "10.1.1.3", "remote_as": 65102, "state": "Established"},
            {"ip": "10.1.2.1", "remote_as": 65000, "state": "Active"},
        ]
    },
    {
        "hostname": "spine2",
        "bgp_asn": 65002,
        "neighbors": [
            {"ip": "10.1.1.5", "remote_as": 65101, "state": "Established"},
            {"ip": "10.1.1.7", "remote_as": 65102, "state": "Active"},
            {"ip": "10.1.2.3", "remote_as": 65000, "state": "Active"},
        ]
    }
]