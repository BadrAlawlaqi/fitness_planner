import os
import json
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from google import genai

# 1. تحميل متغيرات البيئة من ملف .env
load_dotenv()

app = Flask(__name__)
DB_NAME = "database.db"

# 2. تهيئة عميل Gemini API
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def init_db():
    """Database initialization"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            height REAL,
            weight REAL,
            goal TEXT,
            available_ingredients TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            calories INTEGER,
            meal_plan TEXT,
            workout_plan TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

# إنشاء الجداول عند التشغيل
init_db()


def generate_plan_with_gemini(user_data):
    """Prompt engineering and API request to Gemini"""
    prompt = f"""
    You are a professional fitness coach and nutritionist.
    Create a personalized daily fitness and meal plan based on the following user data:
    - Name: {user_data['name']}
    - Age: {user_data['age']}
    - Gender: {user_data['gender']}
    - Height: {user_data['height']} cm
    - Weight: {user_data['weight']} kg
    - Goal: {user_data['goal']}
    - Available Kitchen Ingredients: {user_data['available_ingredients']}

    IMPORTANT: You MUST return ONLY a valid JSON object without any Markdown formatting or extra text outside the JSON block. Use the following key structure:
    {{
      "calories": 2200,
      "meal_plan": "Detailed daily meal breakdown (Breakfast, Lunch, Dinner, Snacks) using the available ingredients",
      "workout_plan": "Detailed daily workout routine tailored to their goal"
    }}
    """
    
    # إرسال الطلب لـ Gemini API
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt
    )
    
    # تنظيف الاستجابة لضمان تحويلها لـ JSON بنجاح
    text_response = response.text.strip()
    if text_response.startswith("```json"):
        text_response = text_response[7:-3].strip()
    elif text_response.startswith("```"):
        text_response = text_response[3:-3].strip()
        
    return json.loads(text_response)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    if request.method == 'POST':
        user_data = {
            'name': request.form.get('name'),
            'age': request.form.get('age'),
            'gender': request.form.get('gender'),
            'height': request.form.get('height'),
            'weight': request.form.get('weight'),
            'goal': request.form.get('goal'),
            'available_ingredients': request.form.get('available_ingredients')
        }
        
        try:
            # 1. حفظ بيانات المستخدم في قاعدة البيانات
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, age, gender, height, weight, goal, available_ingredients)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_data['name'], user_data['age'], user_data['gender'], 
                  user_data['height'], user_data['weight'], user_data['goal'], 
                  user_data['available_ingredients']))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # 2. توليد الخطة عبر Gemini API
            ai_result = generate_plan_with_gemini(user_data)
            
            # 3. حفظ الخطة المولدة في قاعدة البيانات
            cursor.execute('''
                INSERT INTO plans (user_id, calories, meal_plan, workout_plan)
                VALUES (?, ?, ?, ?)
            ''', (user_id, ai_result['calories'], ai_result['meal_plan'], ai_result['workout_plan']))
            
            plan_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return redirect(url_for('dashboard', plan_id=plan_id))

        except Exception as e:
            print(f"\n❌ Error during generation: {e}\n")
            return f"An error occurred while generating the plan: {str(e)}", 500


@app.route('/dashboard/<int:plan_id>')
def dashboard(plan_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT users.name, users.age, users.gender, users.height, users.weight, users.goal,
               plans.calories, plans.meal_plan, plans.workout_plan
        FROM plans
        JOIN users ON plans.user_id = users.id
        WHERE plans.id = ?
    ''', (plan_id,))
    
    plan_data = cursor.fetchone()
    conn.close()
    
    if plan_data:
        data = {
            'name': plan_data[0],
            'age': plan_data[1],
            'gender': plan_data[2],
            'height': plan_data[3],
            'weight': plan_data[4],
            'goal': plan_data[5],
            'calories': plan_data[6],
            'meal_plan': plan_data[7],
            'workout_plan': plan_data[8]
        }
        return render_template('dashboard.html', plan=data)
    else:
        return "Plan not found", 404


if __name__ == '__main__':
    app.run(debug=True)