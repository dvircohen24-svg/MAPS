import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# הגדרת מפתח ה-API של Stay22 ממשתני הסביבה (ניתן לשנות בשרת בהתאם)
STAY22_APP_ID = os.environ.get('STAY22_APP_ID', 'your_test_app_id_here')


@app.route('/')
def home():
    """
    נתיב זה מגיש את דף הנחיתה של האפליקציה (קובץ ה-HTML).
    תומך בריבוי יעדים דרך פרמטר dests המופרד בפסיקים.
    לדוגמה: /?dests=rome,tuscany&group=couple
    """
    # קבלת היעדים מה-URL. אם אין, נשתמש בברירת מחדל של קאו יאי וקאו סוק
    dests_param = request.args.get('dests', 'khaoyai,khaosok')

    # פיצול המחרוזת למערך של יעדים (מנקה רווחים מיותרים)
    destinations = [d.strip() for d in dests_param.split(',') if d.strip()]

    group_type = request.args.get('group', 'family')
    travel_style = request.args.get('style', 'general')

    # העברת הנתונים למנוע התבניות של Flask
    return render_template('index.html',
                           destinations=destinations,
                           group_type=group_type,
                           travel_style=travel_style)


@app.route('/api/hotels')
def get_hotels():
    """
    נתיב זה מקבל בקשות מתוך מפת ה-Leaflet שלנו, 
    שואב את הנתונים בזמן אמת מ-Stay22, ומחזיר JSON ללקוח.
    """
    lat = request.args.get('lat', default=14.5300, type=float)
    lng = request.args.get('lng', default=101.4000, type=float)

    stay22_url = "https://api.stay22.com/v3/search"

    params = {
        'appid': STAY22_APP_ID,
        'lat': lat,
        'lng': lng,
    }

    try:
        response = requests.get(stay22_url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Stay22: {e}")
        return jsonify({
            'error': 'Failed to fetch hotels from Stay22',
            'details': str(e)
        }), 500


if __name__ == '__main__':
    # מפעיל את השרת בסביבת פיתוח
    app.run(debug=True)
