#test
from flask import Flask, render_template, redirect, request, session, url_for

from flask_session import Session
from datetime import timedelta, datetime # הוספתי datetime
import mysql.connector
from contextlib import contextmanager
from utils import *

app = Flask(__name__)

# הגדרות Session מתוקנות לפיתוח
app.config.update(
    SESSION_TYPE="filesystem",
    # SESSION_FILE_DIR="./flask_session_data", # נקודה לפני אומרת "בתיקייה הנוכחית"
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=10),
    SESSION_COOKIE_SECURE=False # חייב להיות False כדי שיעבוד ב-localhost
)

Session(app)

@app.route("/")
def home_page():
    try:
        # קריאה לפונקציה (היא כבר מטפלת בפתיחה וסגירה של ה-DB לבד)
        airports_list = get_all_active_airports()
    except Exception as e:
        # טיפול בשגיאה למקרה שה-DB לא זמין
        print(f"Error loading airports: {e}")
        airports_list = []

    return render_template('home_page.html',
                           origins=airports_list,
                           destinations=airports_list)


@app.route("/user_home_page")
def user_home_page():
    if 'email' not in session:
        return redirect("/login")
        # 1. שליפת רשימת השדות לחיפוש (כמו שעשינו בדף הרגיל)
        airports_list = get_all_active_airports()
        # 2. בדיקה איזה טאב להציג
        active_tab = request.args.get('tab', 'search')
        # 3. שליפת היסטוריית ההזמנות של המשתמש הספציפי
        # נניח שיש לך פונקציה כזו ב-utils שמקבלת את המייל/מזהה של המשתמש
        user_history = []
        if active_tab == 'history':
            user_history = get_user_bookings(session['user_id'])

        return render_template('user_home_page.html',
                               origins=airports_list,
                               destinations=airports_list,
                               active_tab=active_tab,
                               user_history=user_history,  # שולחים את ההיסטוריה ל-HTML
                               name=session.get('name'))


@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")  # unique value
        password = request.form.get("password")
        if ExistingUser.get(email) == password:
            session['email'] = email
            return redirect("/user_home_page")
        else:
            return render_template("login.html", message='Incorrect Login Details.')
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # בטעינה ראשונה נתחיל עם שדה טלפון אחד
    num_phones = int(request.form.get('num_phones', 1))
    if request.method == "POST":
        # תרחיש 1: המשתמש לחץ על הוספת טלפון
        if 'add_phone' in request.form:
            num_phones += 1
            return render_template("register.html", num_phones=num_phones)
        # תרחיש 2: המשתמש מנסה להירשם (final_submit)
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        birth_date = request.form.get("birth_date")
        passport = request.form.get("passport")
        password = request.form.get("password")
        # איסוף כל מספרי הטלפון לרשימה אחת
        phones_list = []
        for i in range(num_phones):
            p = request.form.get(f"phone_{i}")
            if p:
                phones_list.append(p)
        # המרת הרשימה למחרוזת אחת (למשל: "050123, 052456") כדי להתאים למבנה הקיים שלך
        all_phones_str = ", ".join(phones_list)
        # בדיקה שכל השדות מולאו (כולל לפחות טלפון אחד)
        if not all([first_name, last_name, email, all_phones_str, birth_date, passport, password]):
            return render_template("register.html", num_phones=num_phones, message="נא למלא את כל השדות")
        # יצירת המשתמש עם מחרוזת הטלפונים
        new_user = ExistingUser.add(ExistingUser(
            first_name, last_name, all_phones_str, email, passport, password, birth_date,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))
        if new_user:
            session['email'] = email
            return redirect("/login")
        else:
            return render_template("register.html", num_phones=num_phones, message="אימייל כבר קיים במערכת")

    return render_template("register.html", num_phones=num_phones)


    return render_template("register.html")
if __name__=="__main__":

    app.run(debug=True)
