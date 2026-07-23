from flights.models import Airport

airports = [
    ("DEL", "Indira Gandhi International Airport", "Delhi"),
    ("BOM", "Chhatrapati Shivaji Maharaj International Airport", "Mumbai"),
    ("BLR", "Kempegowda International Airport", "Bengaluru"),
    ("HYD", "Rajiv Gandhi International Airport", "Hyderabad"),
    ("MAA", "Chennai International Airport", "Chennai"),
    ("CCU", "Netaji Subhas Chandra Bose International Airport", "Kolkata"),
    ("AMD", "Sardar Vallabhbhai Patel International Airport", "Ahmedabad"),
    ("PNQ", "Pune Airport", "Pune"),
    ("GOI", "Dabolim Airport", "Goa"),
    ("GOX", "Manohar International Airport", "Goa"),
    ("COK", "Cochin International Airport", "Kochi"),
    ("TRV", "Trivandrum International Airport", "Thiruvananthapuram"),
    ("IXC", "Chandigarh International Airport", "Chandigarh"),
    ("LKO", "Chaudhary Charan Singh International Airport", "Lucknow"),
    ("PAT", "Jay Prakash Narayan Airport", "Patna"),
    ("GAU", "Lokpriya Gopinath Bordoloi Airport", "Guwahati"),
    ("IDR", "Devi Ahilya Bai Holkar Airport", "Indore"),
    ("JAI", "Jaipur International Airport", "Jaipur"),
    ("NAG", "Dr. Babasaheb Ambedkar Airport", "Nagpur"),
    ("BHO", "Raja Bhoj Airport", "Bhopal"),
    ("IXR", "Birsa Munda Airport", "Ranchi"),
    ("VNS", "Lal Bahadur Shastri Airport", "Varanasi"),
    ("SXR", "Srinagar Airport", "Srinagar"),
    ("IXJ", "Jammu Airport", "Jammu"),
    ("IXL", "Kushok Bakula Rimpochee Airport", "Leh"),
    ("BBI", "Biju Patnaik International Airport", "Bhubaneswar"),
    ("IXB", "Bagdogra Airport", "Siliguri"),
    ("IMF", "Imphal Airport", "Imphal"),
    ("IXA", "Agartala Airport", "Agartala"),
    ("IXZ", "Veer Savarkar Airport", "Port Blair"),
    ("CJB", "Coimbatore International Airport", "Coimbatore"),
    ("IXM", "Madurai Airport", "Madurai"),
    ("IXE", "Mangalore International Airport", "Mangalore"),
]

for code, name, city in airports:
    Airport.objects.get_or_create(
        code=code, defaults={"name": name, "city": city, "country": "India"}
    )

print("Indian airports added successfully")
print("Total airports:", Airport.objects.count())
