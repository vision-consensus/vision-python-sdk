CONF_MAINNET = {
    "fullnode": "https://infragrid.v.network",
    "event": "https://infragrid.v.network",
}

# testNet Maintained by the official team
CONF_VIPONEER = {
    "fullnode": "https://vpioneer.infragrid.v.network/",
    "event": "https://vpioneer.infragrid.v.network/",
}

ALL = {
    "mainnet": CONF_MAINNET,
    "vpioneer": CONF_VIPONEER,
}


def conf_for_name(name: str) -> dict:
    return ALL.get(name, None)
