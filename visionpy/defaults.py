CONF_MAINNET = {
    "fullnode": "https://visionexplorer.bkbos.space",
    "event": "https://visionexplorer.bkbos.space",
}

# Maintained by the official team
CONF_VTEST = {
    "fullnode": "https://vtest.infragrid.v.network",
    "event": "https://vtest.infragrid.v.network",
}

ALL = {
    "mainnet": CONF_MAINNET,
    "vtest": CONF_VTEST,
}


def conf_for_name(name: str) -> dict:
    return ALL.get(name, None)
