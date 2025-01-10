# binance_commons.py
import calendar
from datetime import datetime
import json
import os
import ccxt
import boto3


def init_exchange():
    exchange_class = getattr(ccxt, os.environ['eid'])
    exchange = exchange_class({
        'apiKey': os.environ['key'],
        'secret': os.environ['secret'],
        'timeout': 30000,
        'enableRateLimit': True,
    })
    exchange.loadMarkets()
    return exchange


def send_market_data(market_data, interval, sqs):
    message = {
        'exchange': 'binance',
        'data_type': 'live',
        'interval': interval,
        'market_data': market_data
    }
    print(message)

    result = sqs.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/716418748259/quantegy-analyze-queue',
        MessageBody=json.dumps(message)
    )

    print(json.dumps(result, indent=4, sort_keys=True))

def go(interval, since):
    sqs = boto3.client('sqs')
    exchange = init_exchange()
    market_data = []
    if exchange.has['fetchOHLCV']:
        for symbol in exchange.markets:
            if symbol[-4:] == "USDT":
                data = json.dumps(exchange.fetch_ohlcv(symbol, interval, since=since))
                item = {
                    'symbol': symbol[:-5],
                    'data': data,
                }
                market_data.append(item)
                # if len(market_data) > 9:
                #     send_market_data(market_data, interval, sqs)
                #     market_data = []

    send_market_data(market_data, interval, sqs)