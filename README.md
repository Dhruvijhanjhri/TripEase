# ✈️ TripEase – AI-Powered Travel Booking Platform

[![Django](https://img.shields.io/badge/Django-4.2-green)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple)](https://getbootstrap.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)](https://www.postgresql.org/)
[![Supabase](https://img.shields.io/badge/Backend%20Database-Supabase-green)](https://supabase.com/)
[![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini-orange)](https://ai.google.dev/)
[![Render](https://img.shields.io/badge/Deployment-Render-black)](https://render.com/)

---

## 🌐 Live Demo

**Live Application:**
https://tripease-y0yf.onrender.com/

**GitHub Repository:**
https://github.com/Dhruvijhanjhri/TripEase

---

## 📌 Overview

TripEase is a full-stack **AI-powered travel booking platform** developed using Django and Python.

The platform provides an integrated travel experience where users can search and book **flights, hotels, and holiday packages**, generate personalized AI travel itineraries, manage bookings, complete simulated payments, and access personalized dashboards.

The application is designed as a real-world travel platform with a production-oriented architecture, PostgreSQL database deployment, authentication, booking workflows, AI integration, and responsive web interfaces.

---

## 🚀 Key Features

### ✈️ Flight Booking

* Search flights by source, destination, date, cabin class, and passengers
* Airport-based flight search
* Direct and connecting flight handling
* AI-assisted fare insights
* Flight availability and seat selection
* Passenger management
* Booking confirmation
* Booking history
* Flight tracking
* QR-based boarding pass generation
* Passenger and booking validation

### 🏨 Hotel Booking

* Search hotels by destination and dates
* Hotel and room availability
* Room selection and booking
* Hotel details and amenities
* Check-in and check-out information
* Weather information for destinations
* Booking history and details
* Hotel review support

### 🎒 Holiday Packages

* Browse holiday packages
* Destination-based package search
* Package details and itineraries
* Traveller management
* Package booking and confirmation
* Booking history

### 🤖 AI Trip Planner

* Google Gemini AI integration
* Personalized travel itinerary generation
* Budget-based trip planning
* Duration-based itinerary planning
* Interest-based recommendations
* Suggested travel style
* Best-season information
* Nearest airport information
* Route suggestions
* Map integration

### 💳 Payment & Booking Workflow

* Integrated simulated payment workflow
* UPI, Card, Net Banking, and Wallet options
* Transaction generation
* Payment status tracking
* Booking confirmation
* Payment history
* Booking references

> **Note:** The payment system is implemented as a simulated application workflow for demonstration and portfolio purposes. It does not process real financial transactions.

### 📊 User Dashboard

* Upcoming trips
* Booking history
* Flight, hotel, and package statistics
* Total booking and spending information
* Payment statistics
* Quick actions
* Personalized booking information

### 🛠️ Admin Dashboard

* Admin-only dashboard
* Booking analytics
* Revenue statistics
* Booking statistics by category
* Recent booking activity
* User statistics
* Top destinations
* Top hotels and packages
* Admin booking detail views
* Revenue and booking analysis

---

## 🧠 Technology Stack

### Backend

* Python
* Django 4.2
* Django ORM
* Django Authentication

### Database

* PostgreSQL
* Supabase PostgreSQL
* SQLite for local development/backups

### AI

* Google Gemini API
* AI-powered travel itinerary generation
* AI-assisted flight fare insights

### Frontend

* HTML5
* CSS3
* Bootstrap 5
* JavaScript
* Responsive UI

### APIs & Integrations

* Weather API
* Maps/location services
* Google Gemini API

### Deployment

* Render
* Gunicorn
* PostgreSQL/Supabase
* WhiteNoise/static file handling

---

## 🗂️ Project Structure

```text
TripEase/
│
├── accounts/              # Authentication and user management
├── bookings/              # Flight booking and passenger management
├── flights/               # Flight search and flight-related functionality
├── hotels/                # Hotel and room booking
├── packages/              # Holiday package management
├── payments/              # Payment workflows
├── dashboard/             # User and admin dashboards
├── ai_planner/            # Gemini-powered travel planner
├── integrations/          # External API integrations
├── reviews/               # Review functionality
│
├── templates/             # HTML templates
├── static/                # CSS, JavaScript and images
├── tripease/              # Django project configuration
├── manage.py
├── requirements.txt
├── render.yaml
└── README.md
```

---

## 🗄️ Database & Deployment

TripEase was initially developed using SQLite for local development and testing.

The application was later migrated to **PostgreSQL using Supabase** for production deployment.

The production deployment is hosted on **Render** and uses the PostgreSQL database for persistent application data.

The application includes multiple relational models covering:

* Users
* Airports
* Flights
* Hotels
* Rooms
* Bookings
* Passengers
* Hotel bookings
* Package bookings
* Payments
* Travel packages

---

## 🔐 Authentication & Access Control

TripEase uses Django authentication for user access management.

The application includes:

* User registration/login
* Authenticated booking workflows
* User-specific booking access
* Staff/admin access
* Admin-only dashboard functionality
* Protected booking details

---

## 📱 Responsive Design

The application is designed to work across:

* Desktop
* Tablet
* Mobile

The navigation, booking workflows, dashboards, search forms, and major travel features are adapted for responsive use.

---

## 🔄 Booking Workflow

```text
Search
   ↓
Select Flight / Hotel / Package
   ↓
Enter Traveller Details
   ↓
Review Booking
   ↓
Simulated Payment
   ↓
Booking Confirmation
   ↓
Manage Booking
   ↓
Boarding Pass / Booking Details
```

---

## 🤖 AI Trip Planning Workflow

```text
Destination + Budget + Duration + Interests
                    ↓
             Gemini AI Service
                    ↓
          Personalized Itinerary
                    ↓
      Travel Recommendations
                    ↓
     Maps / Hotels / Destination Info
```

---

## 🎯 Project Highlights

* Full-stack Django application
* Relational database design
* PostgreSQL production deployment
* AI integration using Google Gemini
* Multiple end-to-end booking workflows
* Flight seat selection
* QR boarding pass generation
* Admin analytics dashboard
* External API integrations
* Responsive web interface
* Production deployment using Render

---

## 🔮 Future Enhancements

Possible future improvements include:

* Real payment gateway integration
* Real-time flight status integration
* Real hotel review integration
* Advanced recommendation models
* More comprehensive travel analytics
* Additional travel providers and APIs
* Automated email/SMS booking notifications

---

## 📄 Project Status

**Status: Completed V1 / Production Deployed**

TripEase V1 is deployed and available for demonstration through the live application link above.
Future improvements can be developed incrementally without changing the current production workflow.
