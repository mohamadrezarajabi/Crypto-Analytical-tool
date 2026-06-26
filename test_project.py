import pytest
import pandas as pd
import os
from project import Crypto


@pytest.fixture
def last_row_data():
    df = pd.read_csv('market_data.csv')
    return df.iloc[-1].to_dict()


@pytest.fixture
def crypto_instance(last_row_data):
    symbol,convert = last_row_data['symbol'].split('/')
    return Crypto(symbol=symbol, convert_fee=convert)


def test_price_data(crypto_instance, last_row_data):
    crypto_instance.data = last_row_data.copy()
    assert 'price' in crypto_instance.data
    assert 'name' in crypto_instance.data
    assert float(crypto_instance.data['price']) > 0


def test_get_indicator(crypto_instance, last_row_data):
    crypto_instance.data = last_row_data.copy()
    crypto_instance.data['price'] = float(last_row_data['price'])
    crypto_instance.get_indicator()
    assert 'EMA_20' in crypto_instance.data
    assert 'EMA_50' in crypto_instance.data
    assert 'ATR' in crypto_instance.data
    assert 'Swing' in crypto_instance.data


def test_determine_trend(crypto_instance, last_row_data):
    crypto_instance.data = last_row_data.copy()
    crypto_instance.data['price'] = float(last_row_data['price'])
    crypto_instance.data['ATR'] = float(last_row_data.get('ATR'))
    crypto_instance.get_indicator()
    crypto_instance.determine_trend()
    assert 'TP' in crypto_instance.data
    assert 'Breakout_Signal' in crypto_instance.data
    assert 'Risk/Reward' in crypto_instance.data
    crypto_instance.data['level'] = crypto_instance.data['Break_Level']

def test_day_before_ema(crypto_instance, last_row_data):
    crypto_instance.data = last_row_data.copy()
    trend = crypto_instance.day_before_ema()
    assert trend in {"Bullish", "Bearish", "Sideways", None}


def test_csv_save(crypto_instance, last_row_data):
    crypto_instance.data = last_row_data.copy()
    if os.path.exists('market_data.csv'):
        original = os.path.getmtime('market_data.csv')
    else:
        original = None

    crypto_instance.csv_save()

    assert os.path.exists('market_data.csv')
    if original is not None:
        assert os.path.getmtime('market_data.csv') >= original

