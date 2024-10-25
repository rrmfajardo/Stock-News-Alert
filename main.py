import requests
import private
from twilio.rest import Client

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
alpha_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "outputsize": "compact",
    "apikey": private.ALPHA_API
}

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
news_param = {
    "apiKey": private.NEWS_API,
    "q": COMPANY_NAME,
    "pageSize": 3
}

r = requests.get(STOCK_ENDPOINT, alpha_params)
r.raise_for_status()
data = r.json()
closing_prices = [value["4. close"] for (key, value) in data["Time Series (Daily)"].items()]

yesterday_price = float(closing_prices[0]) # yesterday's price
before_ystd_price = float(closing_prices[1]) # day before yesterday's price

price_difference = abs(yesterday_price - before_ystd_price)
price_diff_percentage = (price_difference/before_ystd_price)*100 # |YSTD - BEFORE YSTD| / BEFORE YSTD * 100
sign = "▼"
if yesterday_price > before_ystd_price:
    sign = "▲"

if price_diff_percentage > 0.1:
    res = requests.get(NEWS_ENDPOINT, news_param)
    res.raise_for_status()
    news_data = res.json()["articles"][:3]
    news = [{"title": x["title"], "description": x["description"]} for x in news_data]

    client = Client(private.ACC_SID, private.AUTH_TOKEN)
    message = client.messages.create(
        body=f"{STOCK_NAME}: {sign} {round(price_diff_percentage, 2)}%\nHeadline: {news[0]["title"]}\nBrief: {news[0]["description"]}",
        from_=private.FROM_NO,
        to=private.TO_NO
    )
