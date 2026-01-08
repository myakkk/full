import json
from datetime import datetime
from supabase import create_client, Client
import random
import os
import certifi 

# --- SSL ҚАТЕСІН ТҮЗЕТУ ---
os.environ['SSL_CERT_FILE'] = certifi.where()

# --- БАПТАУЛАР ---
SUPABASE_URL = "https://kgdhjkuaufsinbyaltin.supabase.co"
SUPABASE_KEY = "sb_publishable_ocFzfPWfI6pGgFJvV8Fchw_13v5T7sM"

# Клиентті іске қосу
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Supabase қосылу қатесі: {e}")

# Сұрақтарды импорттау (егер файл бар болса)
try:
    from questions import ALL_DATA, READING_DATA
except ImportError:
    ALL_DATA = {}
    READING_DATA = []

def init_db():
    """Базаны тексереді және сұрақтар жоқ болса, жүктейді."""
    try:
        response = supabase.table('questions').select("id", count="exact").execute()
        count = response.count
        
        if count == 0:
            print("База бос, сұрақтар жүктелуде...")
            bulk_data = []

            # 1. Қалыпты сұрақтар (Тарих, Мат.сауаттылық)
            mapping = {"history": "Қазақстан тарихы", "math": "Математикалық сауаттылық"}
            for key, qs in ALL_DATA.items():
                if key == "reading": continue
                subject_name = mapping.get(key, key)
                for q in qs:
                    bulk_data.append({
                        "subject": subject_name,
                        "question": q['q'],
                        "options": json.dumps(q['opts']),
                        "answer": q['a'],
                        "explanation": q.get('explanation', ''),
                        "context": None
                    })

            # 2. Оқу сауаттылығы (Мәтіндік сұрақтар)
            for item in READING_DATA:
                text_passage = item["text"]
                for q in item["questions"]:
                    bulk_data.append({
                        "subject": "Оқу сауаттылығы",
                        "question": q['q'],
                        "options": json.dumps(q['opts']),
                        "answer": q['a'],
                        "explanation": "",
                        "context": text_passage
                    })
            
            # Базаға салу (100-ден бөліп)
            chunk_size = 100
            for i in range(0, len(bulk_data), chunk_size):
                supabase.table('questions').insert(bulk_data[i:i+chunk_size]).execute()
            print("Сұрақтар сәтті жүктелді!")
            
    except Exception as e:
        print(f"init_db қатесі: {e}")

# --- ҚОЛДАНУШЫЛАР ---
def login_user(username, password):
    try:
        response = supabase.table('users').select("*").eq('username', username).eq('password', password).execute()
        if response.data:
            return response.data[0]
    except: pass
    return None

def register_user(username, full_name, password):
    try:
        check = supabase.table('users').select("id").eq('username', username).execute()
        if check.data:
            return False
        
        supabase.table('users').insert({
            "username": username,
            "full_name": full_name,
            "password": password,
            "role": "student" 
        }).execute()
        return True
    except: return False

# --- database.py соңына қосыңыз ---

def change_password(user_id, new_password):
    """Оқушының өз паролін өзгертуі"""
    try:
        supabase.table('users').update({"password": new_password}).eq('id', user_id).execute()
        return True
    except Exception as e:
        print(f"Password change error: {e}")
        return False

# --- ТЕСТ ЖӘНЕ НӘТИЖЕЛЕР ---
def save_result(user_id, subject, score, total):
    try:
        supabase.table('results').insert({
            "user_id": user_id,
            "subject": subject,
            "score": score,
            "total": total,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "is_active": True 
        }).execute()
    except Exception as e: print(f"Қате: {e}")

def get_questions_by_subject(subject, limit=20):
    try:
        response = supabase.table('questions').select("*").eq('subject', subject).execute()
        data = response.data
        if not data: return []
        
        if subject == "Оқу сауаттылығы":
            data.sort(key=lambda x: x.get('context', '') or '')
            selected = data[:limit]
        else:
            random.shuffle(data)
            selected = data[:limit]
        
        return [{
            "id": r["id"],
            "q": r["question"],
            "opts": json.loads(r["options"]),
            "a": r["answer"],
            "expl": r["explanation"],
            "context": r.get("context")
        } for r in selected]
    except Exception as e:
        print(f"Сұрақ алу қатесі: {e}")
        return []

def get_my_results(user_id):
    try:
        response = supabase.table('results').select("*").eq('user_id', user_id).order('id', desc=True).execute()
        return response.data
    except: return []

# --- РЕЙТИНГ ЖҮЙЕСІ ---
def get_leaderboard_general():
    try:
        users_res = supabase.table('users').select("id, full_name").eq('role', 'student').execute()
        users = users_res.data
        
        results_res = supabase.table('results').select("user_id, subject, score").eq('is_active', True).execute()
        results = results_res.data

        leaderboard = []
        for u in users:
            uid = u['id']
            user_results = [r for r in results if r['user_id'] == uid]
            total_score = sum(r['score'] for r in user_results)
            
            hist = sum(r['score'] for r in user_results if r['subject'] == "Қазақстан тарихы")
            math = sum(r['score'] for r in user_results if r['subject'] == "Математикалық сауаттылық")
            read = sum(r['score'] for r in user_results if r['subject'] == "Оқу сауаттылығы")
            
            if total_score > 0:
                leaderboard.append({
                    "full_name": u['full_name'],
                    "history": hist,
                    "math": math,
                    "reading": read,
                    "total_score": total_score
                })
        
        leaderboard.sort(key=lambda x: x['total_score'], reverse=True)
        return leaderboard
    except Exception as e: 
        print(f"Leaderboard Error: {e}")
        return []

def get_user_stats(user_id):
    try:
        res_count = supabase.table('results').select("id", count="exact").eq('user_id', user_id).execute()
        total_tests = res_count.count
        
        res_scores = supabase.table('results').select("score, total").eq('user_id', user_id).execute()
        if not res_scores.data: return 0, 0
            
        percentages = [(r['score'] / r['total'] * 100) for r in res_scores.data if r['total'] > 0]
        avg_score = sum(percentages) / len(percentages) if percentages else 0
        return total_tests, avg_score
    except: return 0, 0

# --- МҰҒАЛІМ ФУНКЦИЯЛАРЫ ---
def get_all_questions_for_teacher():
    try:
        response = supabase.table('questions').select("id, subject, question").order('id', desc=True).execute()
        return response.data
    except: return []

def delete_question(question_id):
    try:
        supabase.table('questions').delete().eq('id', question_id).execute()
        return True
    except Exception as e:
        print(f"Өшіру қатесі: {e}")
        return False

def add_question(subject, question, opts, answer, explanation=""):
    try:
        supabase.table('questions').insert({
            "subject": subject,
            "question": question,
            "options": json.dumps(opts),
            "answer": answer,
            "explanation": explanation,
            "context": None 
        }).execute()
        return True
    except: return False

def clear_leaderboard():
    try:
        supabase.table('results').update({"is_active": False}).gt('id', -1).execute()
        return True
    except: return False

# --- КІЛТ СӨЗ ЖӘНЕ ПАРОЛЬДІ ҚАЛПЫНА КЕЛТІРУ ---
def get_current_secret():
    try:
        response = supabase.table('settings').select("secret_key").eq('id', 1).execute()
        if response.data:
            return response.data[0]['secret_key']
    except: pass
    return "mektep2026"

def update_secret_key(new_key):
    try:
        supabase.table('settings').update({"secret_key": new_key}).eq('id', 1).execute()
        return True
    except: return False

def reset_password_with_key(username, new_password, input_key):
    ACTUAL_SECRET = get_current_secret()
    if input_key != ACTUAL_SECRET:
        return False, "Құпия кілт сөз қате!"

    try:
        user_check = supabase.table('users').select("id").eq('username', username).execute()
        if not user_check.data:
            return False, "Мұндай логин табылмады!"

        supabase.table('users').update({"password": new_password}).eq('username', username).execute()
        return True, "Құпия сөз сәтті өзгертілді!"
    except:
        return False, "Байланыс қатесі!"

# --- ӘКІМШІ (ADMIN) ФУНКЦИЯЛАРЫ - SUPABASE НҰСҚАСЫ ---
def get_all_users():
    """Барлық тіркелген оқушыларды алу (Supabase)"""
    try:
        # id бойынша сұрыптаймыз
        response = supabase.table('users').select("id, full_name, username, password, role").order('id', desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Users алу қатесі: {e}")
        return []

# --- database.py ішіне қосыңыз немесе түзетіңіз ---

# --- database.py ішіндегі ескі функцияны осыған ауыстырыңыз ---

def update_user_info(user_id, new_username, new_password, new_fullname, new_role):
    """Қолданушының деректерін ЖӘНЕ ЛАУАЗЫМЫН өзгерту"""
    try:
        data = {
            "username": new_username,
            "password": new_password,
            "full_name": new_fullname,
            "role": new_role  # <--- Жаңа қосылған жері осы
        }
        supabase.table('users').update(data).eq('id', user_id).execute()
        return True
    except Exception as e:
        print(f"Update қатесі: {e}")
        return False

def delete_user(user_id):
    """Қолданушыны өшіру (Supabase)"""
    try:
        supabase.table('users').delete().eq('id', user_id).execute()
        return True
    except Exception as e:
        print(f"Delete user қатесі: {e}")
        return False
