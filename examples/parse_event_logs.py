from pprint import pprint

from visionpy import Vision, Contract


def parse_event_logs():
    client = Vision(network='vpioneer')
    cnr: Contract = client.get_contract('VE2sE7iXbSyESQKMPLav5Q84EXEHZCnaRX')   # USDT Contract
    txi = client.get_transaction_info('31e2cac2866d976c4c532542624ac55f8141f6c516407393d0c94caaca9c2c94')
    events = list(cnr.events.Transfer.process_receipt(txi))
    pprint(events)


if __name__ == '__main__':
    parse_event_logs()
