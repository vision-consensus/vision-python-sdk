from pprint import pprint

from visionpy import Vision


def exp_decode_function_input():
    client = Vision(network='vpioneer')
    txn = client.get_transaction('61df64ad3b50583a8ed139ba4f3e44cbfc38156b4ce06e35b7fadb9466289122')
    cnr = client.get_contract(txn['raw_data']['contract'][0]['parameter']['value']['contract_address'])
    decoded_data = cnr.decode_function_input(txn['raw_data']['contract'][0]['parameter']['value']['data'])
    pprint(decoded_data)
    # {
    #     'amountOutMin': 88396066,
    #     'path': ('VQokda3GiAfACiiPrHJed2dk1uRTgFVjYS', 'VVNLcKQBgywFWDCVAB6Hh5JMtSJk3NAy2c'),
    #     'to': 'VK6zWsRuXfS682qSaHjqGkFM178XLWdSiT',
    #     'deadline': 1647252114
    # }
