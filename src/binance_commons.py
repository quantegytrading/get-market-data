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


def go(interval, since):
    sns = boto3.client('sns')
    dynamodb = boto3.resource('dynamodb')
    exchange = init_exchange()
    market_data = []
    if exchange.has['fetchOHLCV']:
        for symbol in exchange.markets:
            if symbol[-4:] == "USDT":
                data = json.dumps(exchange.fetch_ohlcv(symbol, interval, since=since))
                item = {
                    'symbol': symbol[:-4],
                    'data': data,
                }
                market_data.append(item)
    print(exchange.currencies.keys())

    message = {
        'exchange': 'binance',
        'data_type': 'live',
        'interval': interval,
        'market_data': market_data
    }
    # print(message)

    result = sns.publish(
        TargetArn='arn:aws:sns:us-east-1:716418748259:analyze-quantegy-data-soak',
        Message=json.dumps(market_data)
    )

    print(json.dumps(result, indent=4, sort_keys=True))
