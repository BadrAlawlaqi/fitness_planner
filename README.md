# 🏋️‍♂️ AI Personal Fitness & Meal Planner

An AI-powered web application built with **Flask**, **SQLite**, and **Google Gemini API** (`gemini-3.8-flash`). The application creates personalized daily meal plans and workout routines tailored to individual user goals, body metrics, and available pantry ingredients.

---

## ✨ Features

- 🎯 **Tailored Fitness Plans:** Generates workout routines based on user age, weight, height, and specific health goals.
- 🥗 **Smart Meal Planning:** Uses available kitchen ingredients to minimize food waste while meeting target daily calories.
- ⚡ **Fast & Modern AI:** Powered by the latest `google-genai` SDK and `gemini-3.8-flash` model.
- 🗄️ **Database Persistence:** Stores user profiles and generated plans cleanly using SQLite.
- 🎨 **Responsive UI:** Clean, intuitive UI built with HTML5, CSS3, and JavaScript.

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask, SQLite3
- **AI Integration:** Google GenAI SDK (`google-genai`), `gemini-3.8-flash`
- **Environment Management:** `python-dotenv`
- **WSGI Server (Deployment):** `gunicorn`
- **Frontend:** HTML5, CSS3, JavaScript

---

## 📂 Project Structure

```text
fitness_planner/
├── app.py              # Main Flask application logic & Gemini API integration
├── database.db         # SQLite database file
├── requirements.txt    # Project dependencies
├── .env                # Environment configuration (API Keys)
├── .gitignore          # Git exclusion rules
├── static/
│   ├── css/
│   │   └── style.css   # Main stylesheet
│   └── js/
│       └── main.js     # Frontend script
└── templates/
    ├── index.html      # User input form
    └── dashboard.html  # Generated fitness & meal plan view
