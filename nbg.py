#!/usr/bin/env python

import logging
from zeep import Client

logging.getLogger('zeep.wsdl.bindings.soap').setLevel(logging.ERROR)

ccs = ['USD', 'EUR', 'GBP']

client = Client('https://nbg.gov.ge/currency.wsdl')
date   = client.service.GetDate()

for cc in ccs:
    rate = client.service.GetCurrency(cc)
    print('GEL for', cc, '-', rate, '-',date)
