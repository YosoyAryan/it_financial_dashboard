from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from newspaper import Article
import nltk
from textblob import TextBlob
import requests

# Download necessary NLTK resources
nltk.download('punkt')

def analyze_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0.1:
        return 'Positive'
    elif analysis.sentiment.polarity < -0.1:
        return 'Negative'
    else:
        return 'Neutral'

def get_it_tech_news():
    all_news = []

    # ECONOMIC TIMES TECH via RSS
    rss_feeds = {
        "Economic Times Tech": 'https://economictimes.indiatimes.com/rssfeedstopstories.cms'
    }

    for source, url in rss_feeds.items():
        try:
            print(f"Scraping: {source}")
            response = urlopen(url)
            xml_data = response.read()
            response.close()

            parsed_page = soup(xml_data, 'xml')
            items = parsed_page.find_all('item')

            for item in items[:5]:  # Limit to top 5
                title = item.title.text
                link = item.link.text

                try:
                    article = Article(link)
                    article.download()
                    article.parse()
                    article.nlp()
                    summary = article.summary
                    sentiment = analyze_sentiment(summary)

                    all_news.append({
                        "source": source,
                        "title": title,
                        "link": link,
                        "summary": summary,
                        "sentiment": sentiment
                    })
                except Exception as article_err:
                    all_news.append({
                        "source": source,
                        "title": title,
                        "link": link,
                        "summary": "Error parsing article.",
                        "sentiment": "Neutral"
                    })

        except Exception as e:
            all_news.append({
                "source": source,
                "title": f"Error fetching from {source}",
                "link": "#",
                "summary": str(e),
                "sentiment": "Neutral"
            })

    # MONEYCONTROL TECH NEWS via HTML scraping
    try:
        print("Scraping: Moneycontrol Tech")
        mc_url = "https://www.moneycontrol.com/news/technology/"
        page = urlopen(mc_url)
        html = page.read()
        page.close()

        parsed_mc = soup(html, "html.parser")
        articles = parsed_mc.select(".clearfix .title")[:5]

        for article in articles:
            title = article.get_text(strip=True)
            link = article.find('a')['href']

            try:
                mc_article = Article(link)
                mc_article.download()
                mc_article.parse()
                mc_article.nlp()
                summary = mc_article.summary
                sentiment = analyze_sentiment(summary)

                all_news.append({
                    "source": "Moneycontrol Tech",
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "sentiment": sentiment
                })
            except Exception:
                all_news.append({
                    "source": "Moneycontrol Tech",
                    "title": title,
                    "link": link,
                    "summary": "Error parsing article.",
                    "sentiment": "Neutral"
                })

    except Exception as mc_err:
        all_news.append({
            "source": "Moneycontrol Tech",
            "title": "Error fetching from Moneycontrol",
            "link": "#",
            "summary": str(mc_err),
            "sentiment": "Neutral"
        })

    return all_news

# Optional: Currency exchange utility function
def get_exchange_rate(base, target):
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        response = requests.get(url)
        data = response.json()
        
        if 'rates' in data:
            return data['rates'].get(target)
        return None
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return None
