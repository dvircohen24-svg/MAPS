import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# הגדרות מפתחות עבור RapidAPI ממשתני הסביבה (יש לעדכן בהתאם לחשבון שלך)
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY', 'your_rapidapi_key_here')
RAPIDAPI_HOST = os.environ.get('RAPIDAPI_HOST', 'booking-com.p.rapidapi.com')
RAPIDAPI_URL = os.environ.get('RAPIDAPI_URL', 'https://booking-com.p.rapidapi.com/v1/hotels/search')


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
    שואב את הנתונים בזמן אמת מ-RapidAPI, ומחזיר JSON ללקוח.
    """
    # מיקום
    lat = request.args.get('lat', default=14.5300, type=float)
    lng = request.args.get('lng', default=101.4000, type=float)
    dest_id = request.args.get('dest_id')
    
    # תאריכים והרכב
    checkin = request.args.get('checkin')
    checkout = request.args.get('checkout')
    guests = request.args.get('guests', type=int)
    rooms = request.args.get('rooms', type=int)
    currency = request.args.get('currency', default='USD')

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    # פרמטרים בסיסיים
    # חלק מה-APIs משתמשים ב-'filter_by_currency' במקום 'currency'
    params = {
        'currency': currency, 
        'locale': 'en-gb'
    }
    
    # בחירת מיקום
    if dest_id:
        params['dest_id'] = dest_id
        params['dest_type'] = 'city' # תוקן מ-search_type ל-dest_type
    else:
        params['latitude'] = lat
        params['longitude'] = lng

    # תאריכים
    if checkin:
        params['checkin_date'] = checkin
    if checkout:
        params['checkout_date'] = checkout
        
    # הרכב אורחים וחדרים
    if guests:
        params['adults_number'] = guests
        
    # בוקינג כמעט תמיד דורשים חדר 1 כמינימום, לכן נגדיר ברירת מחדל אם חסר
    params['room_number'] = rooms if rooms else 1

    try:
        response = requests.get(RAPIDAPI_URL, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # נרמול נתונים למערך 'results'
        if 'result' in data and 'results' not in data:
            data['results'] = data.pop('result')
            
        return jsonify(data)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from RapidAPI: {e}")
        return jsonify({
            'error': 'Failed to fetch hotels from RapidAPI',
            'details': str(e)
        }), 500


if __name__ == '__main__':
    # מפעיל את השרת בסביבת פיתוח
    app.run(debug=True)
