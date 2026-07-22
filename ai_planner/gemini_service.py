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

        # Return AI response if available
        if response and hasattr(response, "text") and response.text:
            return response.text

    except Exception as e:
        print(f"Gemini SSL/API error: {e}")

    # Offline fallback itinerary (always returned if AI fails)
    return f"""
# 🌍 AI Trip Plan for {destination}

**Duration:** {days} days  
**Budget:** ₹{budget}  
**Interests:** {interests}

---

## Day 1 — Arrival & Local Exploration
**Morning:** Arrive in {destination} and check in to your hotel.  
**Afternoon:** Visit nearby attractions and local markets.  
**Evening:** Enjoy a traditional dinner and explore the city center.

**Estimated budget:** ₹{int((budget * 0.6)/max(days,1))}

---

## Day 2 — Major Attractions
**Morning:** Visit the top-rated tourist attractions.  
**Afternoon:** Try local cuisine and cultural experiences.  
**Evening:** Relax at a scenic viewpoint or waterfront area.

**Estimated budget:** ₹{int((budget * 0.6)/max(days,1))}

---

## Day 3 — Leisure & Shopping
**Morning:** Leisure activities or optional sightseeing.  
**Afternoon:** Shopping for souvenirs and local handicrafts.  
**Evening:** Enjoy a farewell dinner.

**Estimated budget:** ₹{int((budget * 0.6)/max(days,1))}

---

## Final Day — Departure
Have a relaxed breakfast, complete hotel checkout, and proceed to the airport or railway station for departure.

### 🚕 Local Transport Tips
- Use app-based taxis for convenience.
- Keep small cash for local transport.
- Start sightseeing early to avoid crowds.

### 🍽 Food Recommendations
- Try authentic local dishes.
- Visit highly rated local restaurants rather than tourist-only spots.

### 🌤 Best Time to Visit
Check the **Travel Intelligence** section above for the recommended season.

---

*This itinerary was generated using the offline fallback planner because the AI service is temporarily unavailable.*
"""