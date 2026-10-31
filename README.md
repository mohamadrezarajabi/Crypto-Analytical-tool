   # Crypto Analytical Tool
    #### Video Demo:  <https://youtu.be/xK-Kk2Et5HU?si=CI_FHmZgbLDHMCW3>
    #### Description:
1. Introduction
1.1 Project Overview
The Crypto Analytical Tool is a simple and beginner-friendly Python application designed to help users perform basic technical analysis on cryptocurrency markets. Many newcomers to crypto struggle to interpret market data, analyze price trends, and identify reasonable conditions for considering a trade. This tool retrieves live market data using trusted APIs, calculates relevant technical indicators such as EMA (Exponential Moving Average) and ATR (Average True Range), and provides an overall analysis of the current market condition.

The final output is saved as a CSV file, allowing users to track and review past analysis results over time. This project aims to enhance understanding of market conditions, not to give definitive recommendations for buying or selling.

2. Why I Chose This Project
I chose this project because technical analysis can be confusing for many beginners in the crypto market, and existing tools are often too complex or designed for advanced users. I wanted to build a solution that:

Uses real market data.

Automatically calculates important technical indicators.

Produces outputs that are easy to interpret and analyze.

This project allowed me to practice:

Working with APIs,

Data processing and analysis using Python and pandas,

Logical design of financial calculations,

Writing and structuring unit tests.

The result is a practical tool, not just a demonstration script.

3. Problems This Project Solves
The cryptocurrency market can be confusing for new users because:

Market prices and indicators are scattered across different sources,

Calculating technical indicators manually requires technical knowledge,

Determining when to analyze or trade is not always clear.

This tool performs the following steps automatically:

Fetches market data from trusted sources like CoinMarketCap and KuCoin,

Computes key technical indicators such as EMA and ATR,

Analyzes market structure and potential breakout scenarios,

Saves the results as a CSV file for later analysis.

This approach helps users gain better insight into market behavior and risk without deep technical expertise.

4. Project Structure
4.1 project.py
This file is the main entry point of the application. It manages the entire technical analysis process, including:

Accepting user input (coin symbol, base currency, timeframe),

Initializing the Crypto class,

Running the analysis sequence,

Printing the final result.

Key Functions in project.py:
price_data()
Fetches live price data from the CoinMarketCap API and stores key details in memory for further analysis.

get_indicator()
Retrieves historical price data from the KuCoin API and calculates EMA and ATR, along with market volatility classification.

determine_trend()
Uses price, ATR, and short-term percentage changes to identify support/resistance levels and classify market behavior (e.g., valid or failed breakout), storing suggested stop-loss, take-profit, and risk/reward.

day_before_ema()
Computes daily EMA for the latest two days and determines the broader trend direction (Bullish, Bearish, Sideways).

csv_save()
Writes all calculated data to market_data.csv, creating headers if the file doesn’t exist.

main()
Orchestrates all functions and returns "success" if the full analysis completes without interruption.

4.2 test_project.py
This module includes unit tests written with pytest. The tests help ensure that core parts of the program work correctly without relying on direct API calls every time. The tests use stored data from market_data.csv to verify functionality.

The tests check:

Price retrieval structure (test_price_data),

Indicator calculations (test_get_indicator),

Trend and signal analysis logic (test_determine_trend),

Market direction output (test_day_before_ema),

Successful CSV storage (test_csv_save).

4.3 market_data.csv
This file is the primary output of the project, storing historical analysis results. Each row represents an analysis session, including price data, indicator values, trend signals, and risk metrics.

Columns include:

Coin name and symbol,

Price, volume, and percentage changes,

EMA20, EMA50, ATR,

Swing classification,

Breakout signal and levels,

Stop-loss (SL), Take-profit (TP),

Risk/Reward ratio,

Trend direction.

The file is automatically created or appended when the program runs.

5. Libraries Used
requests – For making HTTP requests to external APIs (CoinMarketCap & KuCoin).

pandas – For data processing, table handling, and calculating indicators.

csv & os – For reading/writing the CSV file and checking file existence.

sys – For graceful program exit if errors occur.

pytest – For writing and running unit tests.

6. Challenges Faced
Implementing get_indicator() was one of the most technically challenging parts. The API returns raw candlestick arrays, and processing open, high, low, and close values required structuring data into a DataFrame using pandas. Initially, a different API was used but caused long delays (~15 seconds) in execution, so I switched to the KuCoin public API for better performance.

Calculating ATR manually (based on the concept of True Range) helped deepen understanding of how price volatility is derived.

In testing, writing test_csv_save was tricky. A direct data comparison approach was unstable, so I ultimately used file modification times to ensure the CSV updated correctly after saving.

The determine_trend() function was onther more challenging parts of this project. At first, I was working with raw numerical price data and directly comparing values, but it felt dry and didn’t produce reliable analysis. With effort and iteration, I developed a more meaningful method that uses historical price elements (previous high/low/close) combined with the ATR (Average True Range) to calculate dynamic support and resistance levels.

Instead of treating price checks as simple thresholds, this function calculates a pivot point from the previous candlestick and adjusts support/resistance zones based on market volatility. It then checks the current price against these calculated levels to determine whether a breakout is occurring and whether it is valid or failed, and accordingly assigns meaningful values for stop-loss (SL), take-profit (TP), and the risk/reward ratio.

7. Difference from Typical Assignments
Most simple crypto assignments only fetch and display price data from one API or perform basic calculations. This project goes further by:

Receiving raw candlestick data and transforming it,

Calculating meaningful technical indicators,

Providing structured trend analysis,

Including thoughtful unit tests,

Storing historic analysis results over time.

This makes the project more useful, scalable, and closer to a real technical analysis tool.

8. How to Run the Project
Step 1: Install Dependencies
pip install requests pandas
Step 2: Run the Program
python project.py
After executing, the program will ask:

Coin symbol – BTC or ETH (required).

Base currency – USD (optional; default is USD).

Timeframe – 1h, 4h, 1d (optional; default is 1h).

The tool will then fetch data, run the analysis, print the results, and save to market_data.csv.

9. How to Run Tests
Ensure market_data.csv exists (created by running the program once), then run:

pytest -q
You should see results like:

5 passed in 1.23s
This indicates all tests passed successfully.

10. Acknowledgments
Thank you to Harvard University and the CS50 course for the guidance and inspiration.
