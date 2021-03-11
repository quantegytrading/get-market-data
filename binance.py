# binance.py
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


def main(event, context):
    sns = boto3.client('sns')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('market-data')
    exchange = init_exchange()
    market_data = []
    # time.sleep(exchange.rateLimit / 1000)  # time.sleep wants seconds
    if exchange.has['fetchOHLCV']:
        for symbol in exchange.markets:
            # time.sleep(exchange.rateLimit / 1000)  # time.sleep wants seconds
            if symbol[-4:] == "/USD":
                now = datetime.utcnow()
                unixtime = calendar.timegm(now.utctimetuple())
                # (unixtime - num mins * sixty seconds) * 1000 ms
                since = (unixtime - 10 * 60) * 1000  # UTC timestamp in milliseconds

                data = json.dumps(exchange.fetch_ohlcv(symbol, '1m', since=since))
                item = {
                    'symbol': symbol[:-4],
                    'data': data,
                }
                market_data.append(item)
                with table.batch_writer() as batch:
                    batch.put_item(
                        Item=item
                    )
    print(exchange.currencies.keys())

    message = {
        'exchange': 'binance',
        'data_type': 'live',
        'market_data': market_data
    }

    sns.publish(
        TargetArn='arn:aws:sns:us-east-1:716418748259:analyze-quantegy-data',
        Message=json.dumps(message)
    )


if __name__ == "__main__":
    main('', '')