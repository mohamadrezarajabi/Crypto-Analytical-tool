import requests
import sys
import os
import csv
import pandas as pd



class Crypto:
    API_KEY = "35829bac0a8a4f858f0e8303b523ae6a"
    URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    url = f"https://api.kucoin.com/api/v1/market/candles?"

    def __init__(self,symbol="BTC" ,convert_fee="USD",interval="1h"):
        self.df = None
        self.symbol = symbol.upper()
        self.convert = convert_fee.upper()
        self.interval = interval
        self.convertT = "USDT"
        self.data = {}

    def main(self):
        print("Getting price information...")
        self.price_data()

        print("Calculating indicator...")
        self.get_indicator()
        print("Doing technical analysis...")
        self.determine_trend()
        self.data['Trend'] = self.day_before_ema()
        self.csv_save()

        return "success"



    def price_data(self):
        params = {"symbol": self.symbol,"convert": self.convert}

        headers = {"X-CMC_PRO_API_KEY": self.API_KEY}

        try:
            response = requests.get(self.URL, params=params, headers=headers,timeout=15).json()
            coin = response['data'][self.symbol]
            usd = coin["quote"]["USD"]
            raw_time = usd["last_updated"]
            only_date = raw_time.split("T")[0]

            self.data.update({
                "name": coin["name"],
                "symbol": f"{self.symbol}/{self.convert}T",
                "price": round(usd["price"],3),
                "market_cap": round(usd["market_cap"]),
                "volume": round(usd["volume_24h"],2),
                "percent_1h": round(usd["percent_change_1h"],2),
                "percent_24h": round(usd["percent_change_24h"],2),
                "percent_7d": round(usd["percent_change_7d"],2),
                "time": only_date
            })
        except (ValueError,KeyError,ConnectionError):
            sys.exit("The request was not sent correctly. Please try again in a few minutes.")

    def get_indicator(self):

        kucoin_interval_map = {
            "1m": "1min", "3m": "3min", "5m": "5min",
            "15m": "15min", "30m": "30min", "1h": "1hour",
            "2h": "2hour", "4h": "4hour", "6h": "6hour",
            "12h": "12hour", "1d": "1day"
        }

        ku_interval = kucoin_interval_map.get(self.interval, "1hour")
        params = {
            "type": ku_interval,
            "symbol": f"{self.symbol}-{self.convertT}",
            "limit": "200",
        }
        try:
            response = requests.get(self.url, params=params, timeout=10).json()

            data = response["data"]

            if not data:
                raise ValueError("No file found. Please try again in a few minutes.")

            df = pd.DataFrame(data)
            df.columns = ["time", "open", "high", "low", "close", "volume","_"]

            df[df.columns] = df[df.columns].astype(float)

            # EMA
            df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
            df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
            self.data["EMA_20"] = round(df["ema_20"].iloc[8],3)
            self.data["EMA_50"] = round(df["ema_50"].iloc[24],3)

            # ATR
            df["hl"] = df["high"] - df["low"]
            df["hc"] = (df["high"] - df["close"].shift(1)).abs()
            df["lc"] = (df["low"] - df["close"].shift(1)).abs()
            df["tr"] = df[["hl","hc","lc"]].max(axis=1)
            df["atr_14"] = df["tr"].ewm(span=14, adjust=False).mean()
            atr = round(df["atr_14"].iloc[-1],3)
            self.data["ATR"] = atr

            self.df = df

            # Swing
            volatility = atr / self.data['price']
            if volatility < 0.01:
                swing = "Low volatility"
            elif volatility <= 0.03:
                swing = "Normal volatility"
            else:
                swing = "High volatility"
            self.data["Swing"] = swing

        except Exception as e:
            sys.exit(f"Connection failed, please try again in a few minutes: {e}")


    def determine_trend(self):
        price = float(self.data['price'])
        atr = float(self.data['ATR'])

        df = self.df


        prev_high = df['high'].iloc[-2]
        prev_low = df['low'].iloc[-2]
        prev_close = df['close'].iloc[-2]

        pivot = (prev_high + prev_low + prev_close) / 3

        zone_size = atr * 0.7

        resistance = pivot + (prev_high - pivot) + zone_size
        support = pivot - (pivot - prev_low) - zone_size

        resistance = (resistance + (prev_close + zone_size)) / 2
        support = (support + (prev_close - zone_size)) / 2

        result = {
            "signal": "No Trade",
            "SL": None,
            "TP": None,
            "level": None
        }

        # ======================
        # Breakout resistance
        # ======================

        # VALID BREAKOUT ↑
        if abs(price - resistance) >= atr * 0.7:
            result = {
                "signal": "Valid Breakout (BUY)",
                "SL": round(resistance - atr * 1.75, 3),
                "TP": round(price + atr * 2.5, 3),
                "level": f"SR {round(resistance,5)}"
             }

            #FAIL BREAKOUT ↑
        elif abs(price - resistance) <= atr * 0.45:
            result = {
                "signal": "Fail Breakout (SHORT)",
                "SL": round(price + atr * 1.5, 3),
                "TP": round(resistance - atr * 2, 3),
                "level": f"SR {round(resistance,5)}"
            }

        # ================
        # Breakout Support
        # ================

            #VALID BREAKOUT ↓
        elif abs(support - price) >= atr * 0.7:
            result = {
                "signal": "Valid Breakout (SHORT)",
                "SL": round(support + atr * 1.75, 3),
                "TP": round(price - atr * 2.5, 3),
                "level": f"SR {round(support,5)}"
            }

            # FAIL BREAKOUT ↓
        elif abs(support - price) <= atr * 0.45:
            result = {
                "signal": "Fail Breakout (BUY)",
                "SL": round(price - atr * 1.5, 3),
                "TP": round(support + atr * 2, 3),
                "level": f"SR {round(support,5)}"
            }
        try:
            risk = abs(price - float(result["SL"]))
            reward = abs(float(result["TP"]) - price)

            rr = reward / risk
        except ZeroDivisionError:
            rr = 0
        except TypeError:
            sys.exit("Please try again in a few minutes.")


        # --- Save results ---
        self.data["Breakout_Signal"] = result["signal"]
        self.data["SL"] = result["SL"]
        self.data["TP"] = result["TP"]
        self.data["Risk/Reward"] = round(rr, 1)
        self.data["Break_Level"] = result["level"]

    def day_before_ema(self):
            params = {
                "type": "1day",
                "symbol": f"{self.symbol}-{self.convertT}",
                "limit": "20",
            }
            try:
                response = requests.get(self.url,params=params, timeout=10).json()
                data = response["data"]
                df_daily = pd.DataFrame(data)
                df_daily = df_daily.iloc[:, :6]
                df_daily.columns = ["time", "open", "high", "low", "close", "volume"]

                df_daily[df_daily.columns] = df_daily[df_daily.columns].astype(float)


                df_daily['ema_20'] = df_daily['close'].ewm(span=20, adjust=False).mean()
                yesterday = df_daily['ema_20'].iloc[1]
                now = df_daily['ema_20'].iloc[-2]



                slope = now - yesterday

                difference = (self.data['EMA_20'] - self.data['EMA_50']) / self.data['EMA_50']

                if slope > 0 and 0.0015 < difference:
                    return "Bullish"
                elif slope < 0 and -0.0015 > difference:
                    return "Bearish"
                else:
                    return "Sideways"
            except (ValueError,KeyError):
                return None

    def csv_save(self):
        file_exists = os.path.isfile("market_data.csv")
        with open("market_data.csv", "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.data.keys())

            if not file_exists:
                writer.writeheader()

            writer.writerow(self.data)


if __name__ == "__main__":
    try:
        coins = str(input("please enter a coin: ")).strip().upper()
        convert = str(input("please enter a convert: ")).strip() or "USD"
        intervaltime = input("please enter a time frame: ").strip() or "1h"

        if coins == "":
            raise ValueError("please is enter a valid coin")

    except ValueError:
        sys.exit("please is enter a valid coin")

    analysis = Crypto(symbol=coins,convert_fee=convert,interval=intervaltime)
    print(analysis.main())




