import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_ai_itinerary(destination, days, budget, interests):
    prompt = f"""
    Create a {days}-day travel itinerary.

    Destination: {destination}
    Budget: ₹{budget}
    Interests: {interests}

    Include:
    - Day-wise itinerary
    - Morning, Afternoon and Evening activities
    - Food recommendations
    - Local transport tips
    - Estimated daily budget
    - Best places to visit

    Keep the response structured using Markdown.
    """

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception:
        return None
