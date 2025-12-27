from textblob import TextBlob

def summarize_text(text):
    blob = TextBlob(text)
    sentences = blob.sentences
    summary = " ".join(str(s) for s in sentences[:5])
    sentiment = blob.sentiment.polarity

    return {
        'summary_text': summary,
        'sentiment_score': round(sentiment, 3),
        'overall_assessment': (
            'Positive' if sentiment > 0.05 else
            'Negative' if sentiment < -0.05 else
            'Neutral'
        )
    }

