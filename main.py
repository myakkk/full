import flet as ft
import random
import database as db
import webbrowser
import time
import pandas as pd
import os
import threading 

# --- ТҮСТЕР ПАЛИТРАСЫ ---
THEME_COLOR = ft.Colors.INDIGO
LIGHT_BG = "#F3F4F6"
LIGHT_CARD = "#FFFFFF"
LIGHT_TEXT = "#1F2937"
DARK_BG = "#111827"
DARK_CARD = "#1F2937"
DARK_TEXT = "#F9FAFB"
SECONDARY_TEXT = "#6B7280"

# --- МОТИВАЦИЯЛЫҚ СӨЗДЕР ---
QUOTES = [
    "«Оқу инемен құдық қазғандай.»",
    "«Білімді мыңды жығар, білекті бірді жығар.»",
    "«Еңбек етсең ерінбей, тояды қарның тіленбей.» – Абай",
    "«Армансыз адам – қанатсыз құспен тең.»",
    "«Бүгінгі еңбек – ертеңгі жеміс.»"
]

# --- АНЫҚТАМАЛЫҚ ДЕРЕКТЕР ---
HISTORY_DATES = [
    {"date": "Б.з.б. 1 мыңжылдық", "event": "Сақтардың өмір сүрген уақыты"},
    {"date": "552 жыл", "event": "Түрік қағанатының құрылуы"},
    {"date": "751 жыл", "event": "Атлах (Талас) шайқасы"},
    {"date": "1465 жыл", "event": "Қазақ хандығының құрылуы"},
    {"date": "1723-1727 жылдар", "event": "«Ақтабан шұбырынды...»"},
    {"date": "1991 жыл 16 желтоқсан", "event": "Қазақстанның Тәуелсіздігі"},
]

MATH_FORMULAS = [
    {"name": "Пифагор теоремасы", "formula": "a² + b² = c²"},
    {"name": "Шеңбердің ауданы", "formula": "S = πr²"},
    {"name": "Тіктөртбұрыш ауданы", "formula": "S = a × b"},
    {"name": "Арифметикалық прогрессия", "formula": "an = a1 + (n-1)d"},
]

def main(page: ft.Page):
    db.init_db()
    page.title = "№63 Қ.Сатбаев ҰБТ"
    page.window_icon = "icon.ico"

    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "№63 Қ.Сатбаев ҰБТ"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=THEME_COLOR)
    page.bgcolor = LIGHT_BG
    page.window_width = 400
    page.window_height = 800
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    state = {
        "user": None,
        "current_subject": None,
        "questions": [],
        "current_index": 0,
        "score": 0,
        "answers_log": []
    }

    # --- UI Helpers ---
    def get_bg_color(): return DARK_BG if page.theme_mode == ft.ThemeMode.DARK else LIGHT_BG
    def get_card_color(): return DARK_CARD if page.theme_mode == ft.ThemeMode.DARK else LIGHT_CARD
    def get_text_color(): return DARK_TEXT if page.theme_mode == ft.ThemeMode.DARK else LIGHT_TEXT

    def create_card(content, padding=20):
        return ft.Container(
            content=content,
            padding=padding,
            bgcolor=get_card_color(),
            border_radius=20,
            shadow=ft.BoxShadow(blur_radius=15, spread_radius=1, color=ft.Colors.with_opacity(0.1, "black"), offset=ft.Offset(0, 4)),
            animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        )

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.bgcolor = get_bg_color()
        e.control.icon = ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE
        if state["user"]:
            if state["user"].get("role") == "admin": show_admin_menu()
            elif state["user"].get("role") == "teacher": show_teacher_menu()
            else: show_student_menu()
        else: show_login_screen()
        page.update()

    # --- 1. LOGIN & REGISTER ---
    def show_login_screen():
        page.clean(); page.bgcolor = get_bg_color()
        username = ft.TextField(label="Логин", width=280, border_radius=12, prefix_icon=ft.Icons.PERSON_OUTLINE)
        password = ft.TextField(label="Құпия сөз", width=280, password=True, can_reveal_password=True, border_radius=12, prefix_icon=ft.Icons.LOCK_OUTLINE)
        error_text = ft.Text("", color="red", size=12)

        def login_click(e):
            user = db.login_user(username.value, password.value)
            if user:
                state["user"] = user
                role = user.get("role", "student")
                if role == "admin": show_admin_menu()
                elif role == "teacher": show_teacher_menu()
                else: show_student_menu()
            else:
                error_text.value = "Қате логин немесе құпия сөз!"; page.update()

        content = ft.Column([
            ft.Icon(ft.Icons.SCHOOL_ROUNDED, size=60, color=THEME_COLOR),
            ft.Text("Қош келдіңіз!", size=26, weight="bold", color=get_text_color()),
            ft.Text("№63 Қ.Сатбаев ҰБТ-ға дайындық", color=SECONDARY_TEXT, text_align="center", size=12),
            ft.Divider(height=20, color="transparent"),
            username, password, error_text,
            ft.Container(height=10),
            ft.FilledButton("КІРУ", width=280, height=50, on_click=login_click),
            ft.Row([
                ft.TextButton("Тіркелу", on_click=lambda e: show_register_screen()),
                ft.TextButton("Құпия сөзді ұмыттым?", on_click=lambda e: show_forgot_password_screen())
            ], alignment="center")
        ], horizontal_alignment="center", spacing=10)
        page.add(ft.Container(content=create_card(content, padding=40), alignment=ft.Alignment(0, 0), expand=True))

    def show_register_screen():
        page.clean(); page.bgcolor = get_bg_color()
        full_name = ft.TextField(label="Аты-жөніңіз", width=280, border_radius=12)
        username = ft.TextField(label="Логин", width=280, border_radius=12)
        password = ft.TextField(label="Құпия сөз", width=280, password=True, border_radius=12)
        error_text = ft.Text("", color="red", size=12)

        def register_click(e):
            if not all([username.value, full_name.value, password.value]): error_text.value = "Барлық өрісті толтырыңыз!"; page.update(); return
            if db.register_user(username.value, full_name.value, password.value):
                user = db.login_user(username.value, password.value)
                state["user"] = user
                show_student_menu()
            else: error_text.value = "Бұл логин бос емес!"; page.update()

        content = ft.Column([
            ft.Text("Тіркелу", size=24, weight="bold", color=get_text_color()),
            full_name, username, password, error_text,
            ft.Container(height=10),
            ft.FilledButton("ТІРКЕЛУ", width=280, height=50, on_click=register_click),
            ft.TextButton("Кері қайту", on_click=lambda e: show_login_screen())
        ], horizontal_alignment="center", spacing=10)
        page.add(ft.Container(content=create_card(content), alignment=ft.Alignment(0, 0), expand=True))

    def show_forgot_password_screen():
        page.clean(); page.bgcolor = get_bg_color()
        username = ft.TextField(label="Логин", width=300, border_radius=12, prefix_icon=ft.Icons.PERSON)
        secret_key = ft.TextField(label="Кілт сөз (Мұғалімнен сұраңыз)", width=300, border_radius=12, prefix_icon=ft.Icons.VPN_KEY, password=True, can_reveal_password=True)
        new_pass = ft.TextField(label="Жаңа құпия сөз", width=300, border_radius=12, prefix_icon=ft.Icons.LOCK_RESET, password=True, can_reveal_password=True)
        
        def reset_click(e):
            if not all([username.value, secret_key.value, new_pass.value]):
                page.snack_bar = ft.SnackBar(ft.Text("Барлық өрістерді толтырыңыз!"), bgcolor="red")
                page.snack_bar.open = True; page.update(); return
            success, message = db.reset_password_with_key(username.value, new_pass.value, secret_key.value)
            page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor="green" if success else "red")
            page.snack_bar.open = True; page.update()
            if success: time.sleep(1); show_login_screen()

        content = ft.Column([
            ft.Icon(ft.Icons.LOCK_PERSON, size=60, color=THEME_COLOR),
            ft.Text("Құпия сөзді өзгерту", size=20, weight="bold", color=get_text_color()),
            ft.Divider(), username, secret_key, new_pass, ft.Container(height=10),
            ft.FilledButton("ӨЗГЕРТУ", width=300, height=50, on_click=reset_click),
            ft.TextButton("Кері қайту", on_click=lambda e: show_login_screen())
        ], horizontal_alignment="center", spacing=15)
        page.add(ft.Container(content=create_card(content, padding=40), alignment=ft.Alignment(0, 0), expand=True))

    # --- 2. STUDENT MENU ---
    def show_student_menu():
        page.clean(); page.bgcolor = get_bg_color()
        random_quote = random.choice(QUOTES)
        header = ft.Row([
            ft.Row([
                ft.CircleAvatar(content=ft.Text(state['user']['full_name'][0], size=20, weight="bold"), bgcolor=THEME_COLOR, radius=20),
                ft.Column([ft.Text(f"Сәлем,", size=12, color=SECONDARY_TEXT), ft.Text(f"{state['user']['full_name']}", size=16, weight="bold", color=get_text_color())], spacing=2)
            ]),
            ft.Row([ft.IconButton(ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE, on_click=toggle_theme), ft.IconButton(ft.Icons.LOGOUT_ROUNDED, on_click=lambda e: show_login_screen(), icon_color="red")])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        def create_btn(text, icon, color, action):
            return ft.Container(content=ft.Row([ft.Container(content=ft.Icon(icon, color="white", size=24), bgcolor=color, padding=10, border_radius=10), ft.Text(text, size=16, weight="w600", color=get_text_color())], spacing=15), padding=15, bgcolor=get_card_color(), border_radius=15, border=ft.Border.all(1, ft.Colors.GREY_800 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.GREY_200), on_click=action, ink=True)

        motivation_card = ft.Container(content=ft.Column([ft.Row([ft.Icon(ft.Icons.LIGHTBULB, color=ft.Colors.YELLOW_600), ft.Text("Күннің сөзі", weight="bold", color=get_text_color())]), ft.Text(random_quote, italic=True, size=14, color=SECONDARY_TEXT, text_align="center")], horizontal_alignment="center"), padding=15, bgcolor=get_card_color(), border_radius=15, border=ft.Border.all(1, ft.Colors.GREY_300 if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.GREY_700))

        menu_items = [
            ft.Container(content=header, padding=ft.Padding(bottom=5)), motivation_card, ft.Divider(height=10, color="transparent"),
            ft.Container(content=ft.Row([ft.Icon(ft.Icons.ACCOUNT_CIRCLE, color=ft.Colors.BLUE_400, size=30), ft.Column([ft.Text("Менің профилім", weight="bold", color=get_text_color()), ft.Text("Статистика және баптаулар", size=12, color=SECONDARY_TEXT)], spacing=2), ft.Icon(ft.Icons.CHEVRON_RIGHT, color=SECONDARY_TEXT)], alignment="spaceBetween"), padding=15, bgcolor=get_card_color(), border_radius=15, border=ft.Border.all(1, ft.Colors.GREY_800 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.GREY_200), on_click=lambda e: show_profile_screen(), ink=True),
            ft.Divider(height=10, color="transparent"), ft.Text("Тест тапсыру", size=18, weight="bold", color=get_text_color()),
            create_btn("Қазақстан тарихы", ft.Icons.HISTORY_EDU, ft.Colors.BLUE_500, lambda e: start_test_prep("Қазақстан тарихы")),
            create_btn("Мат. сауаттылық", ft.Icons.CALCULATE_OUTLINED, ft.Colors.ORANGE_500, lambda e: start_test_prep("Математикалық сауаттылық")),
            create_btn("Оқу сауаттылығы", ft.Icons.MENU_BOOK_ROUNDED, ft.Colors.GREEN_500, lambda e: start_test_prep("Оқу сауаттылығы")),
            ft.Divider(height=5, color="transparent"), create_btn("Карточкалар (Жаттау)", ft.Icons.STYLE, ft.Colors.PINK_400, lambda e: show_flashcards_screen()),
            ft.Container(height=5), create_btn("Анықтамалық", ft.Icons.MENU_BOOK, ft.Colors.TEAL_400, lambda e: show_reference_screen()),
            ft.Container(height=5), create_btn("Пайдалы ресурстар", ft.Icons.LINK, ft.Colors.CYAN_500, lambda e: show_resources_screen()),
            ft.Container(height=5), create_btn("Ойындар", ft.Icons.SPORTS_ESPORTS, ft.Colors.INDIGO, lambda e: show_games_menu()),
            ft.Container(height=5), create_btn("Нәтижелер тарихы", ft.Icons.BAR_CHART_ROUNDED, ft.Colors.PURPLE_500, lambda e: show_my_results()), ft.Container(height=20)
        ]
        page.add(ft.Column(controls=menu_items, spacing=10, scroll=ft.ScrollMode.AUTO, expand=True))

    def show_games_menu():
        page.clean(); page.bgcolor = get_bg_color()
        def show_soon(e): page.snack_bar = ft.SnackBar(content=ft.Text("Бұл ойын жақында қосылады!")); page.snack_bar.open = True; page.update()
        def game_card(title, desc, icon, color, action):
            return ft.Container(content=ft.Row([ft.Container(content=ft.Icon(icon, color="white", size=30), bgcolor=color, padding=15, border_radius=15), ft.Column([ft.Text(title, size=18, weight="bold", color=get_text_color()), ft.Text(desc, size=12, color=SECONDARY_TEXT)], spacing=2, expand=True), ft.Icon(ft.Icons.PLAY_CIRCLE_FILLED, color=color, size=30)], alignment="spaceBetween"), padding=15, bgcolor=get_card_color(), border_radius=20, border=ft.Border.all(1, ft.Colors.GREY_300), shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, "black")), on_click=action, ink=True)
        games_list = ft.Column([game_card("Сәйкестендіру", "Дата мен оқиғаны сәйкестендір", ft.Icons.DASHBOARD_CUSTOMIZE, ft.Colors.INDIGO, lambda e: show_matching_game()), ft.Container(height=10), game_card("Хронология", "Оқиғаларды ретімен қой", ft.Icons.TIMELINE, ft.Colors.ORANGE, lambda e: show_timeline_game()), ft.Container(height=10), game_card("Миллионер", "Сұрақтарға жауап беріп, ұпай жина", ft.Icons.MONETIZATION_ON, ft.Colors.GREEN, show_soon)])
        page.add(ft.Container(content=ft.Column([ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_student_menu()), ft.Text("Ойындар бөлмесі", size=24, weight="bold", color=get_text_color())]), ft.Text("Біліміңді ойын арқылы шыңда!", color=SECONDARY_TEXT), ft.Container(height=20), games_list]), padding=20))

    # --- 3.1 СӘЙКЕСТЕНДІРУ ОЙЫНЫ ---
    def show_matching_game():
        page.clean(); page.bgcolor = get_bg_color()
        raw_data = [{"id": 1, "text": "1465 жыл", "type": "date"}, {"id": 1, "text": "Қазақ хандығы", "type": "event"}, {"id": 2, "text": "1723 жыл", "type": "date"}, {"id": 2, "text": "Ақтабан шұбырынды", "type": "event"}, {"id": 3, "text": "1991 жыл", "type": "date"}, {"id": 3, "text": "Тәуелсіздік", "type": "event"}, {"id": 4, "text": "751 жыл", "type": "date"},  {"id": 4, "text": "Атлах шайқасы", "type": "event"}, {"id": 5, "text": "1729 жыл", "type": "date"}, {"id": 5, "text": "Аңырақай", "type": "event"}, {"id": 6, "text": "1993 жыл", "type": "date"}, {"id": 6, "text": "Теңге", "type": "event"}]
        game_data = raw_data.copy(); random.shuffle(game_data)
        game_state = {"first": None, "matches": 0, "lives": 5, "locked": False}
        lives_icon = ft.Row([ft.Icon(ft.Icons.FAVORITE, color="red", size=30), ft.Text(f"{game_state['lives']}", size=24, weight="bold", color="red")], alignment="center")
        status_text = ft.Text("Жұптарды тап!", size=18, color=get_text_color(), weight="bold")
        grid = ft.GridView(expand=True, runs_count=3, max_extent=150, child_aspect_ratio=1.3, spacing=10, run_spacing=10)
        def card_click(e):
            btn = e.control
            if game_state["locked"] or btn.disabled or game_state["lives"] <= 0: return
            btn.scale = 0.9; btn.update(); time.sleep(0.1); btn.scale = 1.0; btn.update()
            if game_state["first"] is None:
                game_state["first"] = btn; btn.bgcolor = ft.Colors.BLUE_500; btn.content.color = ft.Colors.WHITE; btn.disabled = True; btn.update()
            else:
                first_btn = game_state["first"]; btn.bgcolor = ft.Colors.BLUE_500; btn.content.color = ft.Colors.WHITE; btn.update()
                if first_btn.data['id'] == btn.data['id']:
                    first_btn.bgcolor = ft.Colors.GREEN_500; btn.bgcolor = ft.Colors.GREEN_500; first_btn.icon = ft.Icons.CHECK_CIRCLE; btn.icon = ft.Icons.CHECK_CIRCLE; first_btn.disabled = True; btn.disabled = True; first_btn.update(); btn.update(); game_state["matches"] += 1; game_state["first"] = None
                    if game_state["matches"] == len(game_data) // 2: status_text.value = "ЖЕҢІС! 🎉"; status_text.color = ft.Colors.GREEN; status_text.size = 24; page.update()
                else:
                    game_state["locked"] = True; first_btn.bgcolor = ft.Colors.RED_500; btn.bgcolor = ft.Colors.RED_500; first_btn.icon = ft.Icons.CANCEL; btn.icon = ft.Icons.CANCEL; first_btn.update(); btn.update(); game_state["lives"] -= 1; lives_icon.controls[1].value = str(game_state['lives']); lives_icon.update()
                    if game_state["lives"] <= 0: status_text.value = "ОЙЫН АЯҚТАЛДЫ 😢"; status_text.color = ft.Colors.RED; 
                    for c in grid.controls: c.disabled = True
                    page.update(); return
                    bg_col = get_card_color(); txt_col = get_text_color()
                    def reset_cards(b1, b2, def_bg, def_txt):
                        time.sleep(1); b1.bgcolor = def_bg; b2.bgcolor = def_bg; b1.content.color = def_txt; b2.content.color = def_txt; b1.icon = None; b2.icon = None; b1.disabled = False; b2.disabled = False; game_state["first"] = None; game_state["locked"] = False
                        try: grid.update()
                        except: page.update()
                    threading.Thread(target=reset_cards, args=(first_btn, btn, bg_col, txt_col), daemon=True).start()
        for item in game_data:
            grid.controls.append(ft.Container(content=ft.Text(item['text'], size=12, weight="bold", text_align="center", color=get_text_color()), bgcolor=get_card_color(), border_radius=15, alignment=ft.Alignment(0, 0), border=ft.Border.all(1, ft.Colors.GREY_400), shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.1, "black")), on_click=card_click, data=item, ink=True, animate_scale=ft.Animation(300, ft.AnimationCurve.ELASTIC_OUT)))
        page.add(ft.Column([ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_games_menu()), ft.Text("Сәйкестендіру", size=24, weight="bold", color=get_text_color())]), ft.Container(content=ft.Row([lives_icon, status_text], alignment="spaceBetween"), padding=ft.Padding(left=20, right=20, top=0, bottom=0)), ft.Divider(), ft.Container(content=grid, expand=True, padding=10)], expand=True))

    # --- 3.2 ХРОНОЛОГИЯ ОЙЫНЫ ---
    def show_timeline_game():
        page.clean(); page.bgcolor = get_bg_color()
        timeline_data = [{"year": 552, "text": "Түрік қағанатының құрылуы"}, {"year": 751, "text": "Атлах шайқасы"}, {"year": 1218, "text": "Отырар апаты"}, {"year": 1465, "text": "Қазақ хандығының құрылуы"}, {"year": 1723, "text": "Ақтабан шұбырынды"}, {"year": 1729, "text": "Аңырақай шайқасы"}, {"year": 1841, "text": "Кенесары хан сайланды"}, {"year": 1917, "text": "Алаш партиясы"}, {"year": 1991, "text": "Тәуелсіздік алу"}, {"year": 1993, "text": "Ұлттық валюта"}, {"year": 1995, "text": "Ата заң"}]
        current_items = random.sample(timeline_data, 5); random.shuffle(current_items); game_state = {"items": current_items, "checked": False}
        header = ft.Container(content=ft.Column([ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_games_menu(), icon_color=THEME_COLOR), ft.Text("Хронология", size=22, weight="bold", color=get_text_color())]), ft.Text("Оқиғаларды ертеден -> кешке қарай ретте", size=14, color=SECONDARY_TEXT, italic=True, text_align="center")]), padding=ft.Padding(left=10, right=10, top=10, bottom=5))
        items_list = ft.ListView(expand=True, spacing=10, padding=20)
        def render_items():
            items_list.controls.clear()
            for i, item in enumerate(game_state["items"]):
                card_color = get_card_color(); icon = None
                if game_state["checked"]:
                    correct_order = sorted(game_state["items"], key=lambda x: x['year'])
                    if item['year'] == correct_order[i]['year']: card_color = ft.Colors.GREEN_100 if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.GREEN_900; icon = ft.Icon(ft.Icons.CHECK_CIRCLE, color="green")
                    else: card_color = ft.Colors.RED_100 if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.RED_900; icon = ft.Icon(ft.Icons.ERROR, color="red")
                btn_up = ft.IconButton(ft.Icons.KEYBOARD_ARROW_UP, on_click=lambda e, idx=i: move_item(idx, -1), disabled= (i == 0) or game_state["checked"], icon_color=THEME_COLOR)
                btn_down = ft.IconButton(ft.Icons.KEYBOARD_ARROW_DOWN, on_click=lambda e, idx=i: move_item(idx, 1), disabled= (i == len(game_state["items"]) - 1) or game_state["checked"], icon_color=THEME_COLOR)
                card = ft.Container(content=ft.Row([ft.Text(f"{i + 1}.", weight="bold", size=18, color=THEME_COLOR), ft.Container(content=ft.Column([ft.Text(item['text'], weight="bold", size=16, color=get_text_color(), no_wrap=False), ft.Text(f"{item['year']} жыл" if game_state["checked"] else "---- жыл", size=12, color=SECONDARY_TEXT)], spacing=2), expand=True, padding=ft.Padding(left=10, right=0, top=0, bottom=0)), ft.Column([icon if icon else ft.Container(), ft.Row([btn_up, btn_down], spacing=0)], alignment="center", spacing=0)], alignment="spaceBetween"), padding=15, bgcolor=card_color, border_radius=15, border=ft.Border.all(1, ft.Colors.GREY_300), shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.05, "black")), animate_scale=ft.Animation(300, "easeOut")); items_list.controls.append(card)
            page.update()
        def move_item(index, direction): new_index = index + direction; game_state["items"][index], game_state["items"][new_index] = game_state["items"][new_index], game_state["items"][index]; render_items()
        action_area = ft.Container(padding=20, bgcolor=get_bg_color()) 
        def check_order(e):
            game_state["checked"] = True; correct_list = sorted(game_state["items"], key=lambda x: x['year']); is_win = (game_state["items"] == correct_list)
            page.snack_bar = ft.SnackBar(ft.Text("КЕРЕМЕТ! БАРЛЫҒЫ ДҰРЫС! 🎉" if is_win else "Қателер бар!"), bgcolor="green" if is_win else "red"); page.snack_bar.open = True
            action_area.content = ft.FilledButton("Келесі деңгей", icon=ft.Icons.REFRESH, on_click=lambda e: show_timeline_game(), width=float("inf"), height=50); action_area.update(); render_items()
        check_btn = ft.FilledButton("ТЕКСЕРУ", icon=ft.Icons.CHECK, on_click=check_order, width=float("inf"), height=50, style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN)); action_area.content = check_btn; render_items()
        page.add(ft.Column([header, items_list, ft.Divider(height=1), action_area], expand=True, spacing=0))

    # --- 4. FLASHCARDS, 5. TEST, 6. RESULTS - ҚАЛПЫНДА ---
    def show_flashcards_screen():
        page.clean(); page.bgcolor = get_bg_color()
        current_mode = {"data": HISTORY_DATES, "index": 0, "is_flipped": False}
        card_content = ft.Text(value="", size=24, weight="bold", text_align="center", color=get_text_color())
        card_container = ft.Container(content=card_content, width=320, height=200, bgcolor=get_card_color(), border_radius=20, alignment=ft.Alignment(0, 0), shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.with_opacity(0.1, "black")), animate=ft.Animation(duration=300, curve=ft.AnimationCurve.EASE_OUT), on_click=lambda e: flip_card(e))
        title_text = ft.Text("", size=20, weight="bold", color=get_text_color()); counter_text = ft.Text("", color=SECONDARY_TEXT)
        def update_card():
            item = current_mode["data"][current_mode["index"]]
            text = (item['event'] if not current_mode["is_flipped"] else item['date']) if current_mode["data"] == HISTORY_DATES else (item['name'] if not current_mode["is_flipped"] else item['formula'])
            title_text.value = "Тарих: Даталарды жаттау" if current_mode["data"] == HISTORY_DATES else "Математика: Формулалар"
            card_content.value = text; card_container.bgcolor = get_card_color() if not current_mode["is_flipped"] else (ft.Colors.INDIGO_50 if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.GREY_800)
            counter_text.value = f"{current_mode['index'] + 1} / {len(current_mode['data'])}"; page.update()
        def flip_card(e): current_mode["is_flipped"] = not current_mode["is_flipped"]; update_card()
        def next_card(e):
            if current_mode["index"] < len(current_mode["data"]) - 1: current_mode["index"] += 1; current_mode["is_flipped"] = False; update_card()
        def prev_card(e):
            if current_mode["index"] > 0: current_mode["index"] -= 1; current_mode["is_flipped"] = False; update_card()
        def switch_mode(mode_name): current_mode["data"] = HISTORY_DATES if mode_name == "history" else MATH_FORMULAS; current_mode["index"] = 0; current_mode["is_flipped"] = False; update_card()
        controls = ft.Row([ft.IconButton(ft.Icons.ARROW_BACK_IOS, on_click=prev_card), ft.Container(content=ft.Text("Карточканы бас", italic=True, size=12, color=SECONDARY_TEXT), padding=10), ft.IconButton(ft.Icons.ARROW_FORWARD_IOS, on_click=next_card)], alignment="center")
        mode_switcher = ft.Row([ft.FilledButton("Тарих", on_click=lambda e: switch_mode("history"), style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_400)), ft.FilledButton("Математика", on_click=lambda e: switch_mode("math"), style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE_400))], alignment="center")
        update_card(); page.add(ft.Column([ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_student_menu()), title_text]), ft.Divider(color="transparent"), mode_switcher, ft.Container(height=20), card_container, ft.Container(height=20), controls, counter_text], horizontal_alignment="center", spacing=10))

    def start_test_prep(subj): state["current_subject"] = subj; show_settings_menu()

    def show_settings_menu():
        page.clean(); page.bgcolor = get_bg_color()
        dd_count = ft.Dropdown(label="Сұрақ саны", options=[ft.dropdown.Option("5"), ft.dropdown.Option("10"), ft.dropdown.Option("20")], value="5", width=280, border_radius=12)
        def start(e):
            state["questions"] = db.get_questions_by_subject(state["current_subject"], limit=int(dd_count.value))
            if not state["questions"]: page.snack_bar = ft.SnackBar(ft.Text("Сұрақ жоқ!")); page.snack_bar.open=True; page.update(); return
            state["score"] = 0; state["current_index"] = 0; state["answers_log"] = []
            load_question_screen()
        content = ft.Column([ft.Icon(ft.Icons.QUIZ_ROUNDED, size=50, color=THEME_COLOR), ft.Text("Тест баптаулары", size=22, weight="bold", color=get_text_color()), ft.Text(f"{state['current_subject']}", color=SECONDARY_TEXT), ft.Divider(), dd_count, ft.Container(height=20), ft.FilledButton("БАСТАУ", on_click=start, width=280, height=50)], horizontal_alignment="center")
        page.add(ft.Column([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_student_menu()), create_card(content, padding=30)]))

    def load_question_screen():
        if state["current_index"] >= len(state["questions"]): show_result_screen(); return
        page.clean(); page.bgcolor = get_bg_color()
        idx = state["current_index"]; total = len(state["questions"])
        data = state["questions"][idx]; opts = data["opts"].copy(); random.shuffle(opts)
        def open_calculator(e):
            calc_result = ft.Text(value="", size=30, weight="bold", text_align="right", color=ft.Colors.WHITE)
            def btn_click(e):
                val = e.control.data
                if val == "C": calc_result.value = ""
                elif val == "=":
                    try: calc_result.value = str(eval(calc_result.value.replace("×", "*").replace("÷", "/")))
                    except: calc_result.value = "Қате"
                else: calc_result.value += val
                calc_result.update()
            def calc_btn(text, color=ft.Colors.GREY_800, text_color=ft.Colors.WHITE, width=60): return ft.Container(content=ft.Text(text, size=20, color=text_color, weight="bold"), width=width, height=60, bgcolor=color, border_radius=30, alignment=ft.Alignment(0, 0), on_click=btn_click, data=text, ink=True)
            def close_calc(e): page.overlay.clear(); page.update()
            calc_inner = ft.Container(content=ft.Column([ft.Row([ft.IconButton(ft.Icons.CLOSE, icon_color="white", on_click=close_calc)], alignment="end"), ft.Container(content=calc_result, padding=10, bgcolor=ft.Colors.BLACK, border_radius=10, alignment=ft.Alignment(1, 0), height=70), ft.Row([calc_btn("C", ft.Colors.RED_400), calc_btn("(", ft.Colors.GREY_700), calc_btn(")", ft.Colors.GREY_700), calc_btn("÷", ft.Colors.ORANGE, text_color=ft.Colors.WHITE)], alignment="center"), ft.Row([calc_btn("7"), calc_btn("8"), calc_btn("9"), calc_btn("×", ft.Colors.ORANGE)], alignment="center"), ft.Row([calc_btn("4"), calc_btn("5"), calc_btn("6"), calc_btn("-", ft.Colors.ORANGE)], alignment="center"), ft.Row([calc_btn("1"), calc_btn("2"), calc_btn("3"), calc_btn("+", ft.Colors.ORANGE)], alignment="center"), ft.Row([calc_btn("0", width=130), calc_btn("."), calc_btn("=", ft.Colors.GREEN)], alignment="center")], spacing=10), padding=20, bgcolor=ft.Colors.BLACK87, border_radius=20, width=320, shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.BLACK))
            page.overlay.append(ft.Stack([ft.Container(bgcolor=ft.Colors.with_opacity(0.5, "black"), expand=True, on_click=close_calc), ft.Container(content=calc_inner, alignment=ft.Alignment(0, 0))], expand=True)); page.update()
        progress_circles = []
        for i in range(total):
            color = ft.Colors.GREY_300 
            if i < len(state["answers_log"]): color = ft.Colors.GREEN if state["answers_log"][i]["is_correct"] else ft.Colors.RED
            elif i == idx: color = THEME_COLOR 
            progress_circles.append(ft.Container(width=10, height=10, border_radius=5, bgcolor=color))
        btn_next = ft.FilledButton("Келесі", icon=ft.Icons.ARROW_FORWARD, width=320, height=50, on_click=lambda e: next_q(), visible=False)
        options_container = ft.Column(spacing=10)
        def check_answer(e):
            clicked = e.control; selected = clicked.data; correct = data["a"]; is_correct = (selected == correct)
            state["answers_log"].append({"question": data["q"], "your_answer": selected, "correct_answer": correct, "explanation": data["expl"], "is_correct": is_correct})
            for c in options_container.controls:
                c.on_click = None 
                if c.data == correct: c.bgcolor = ft.Colors.GREEN_100; c.border = ft.Border.all(2, ft.Colors.GREEN); c.content.controls[1].color = ft.Colors.BLACK
                elif c.data == selected: c.bgcolor = ft.Colors.RED_100; c.border = ft.Border.all(2, ft.Colors.RED); c.content.controls[1].color = ft.Colors.BLACK
                c.update()
            if is_correct: state["score"] += 1
            btn_next.visible = True; btn_next.update()
        for opt in opts: options_container.controls.append(ft.Container(content=ft.Row([ft.Icon(ft.Icons.CIRCLE_OUTLINED, size=16, color=THEME_COLOR), ft.Text(opt, size=16, expand=True, color=get_text_color())], alignment="start"), padding=15, bgcolor=get_card_color(), width=320, border_radius=12, border=ft.Border.all(2, ft.Colors.GREY_600 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.GREY_200), on_click=check_answer, data=opt, ink=True))
        context_block = ft.Container()
        if data.get("context"): context_block = ft.Container(content=ft.Column([ft.Text("Мәтінді мұқият оқып шығыңыз:", size=12, color=SECONDARY_TEXT, italic=True), ft.Container(content=ft.Column([ft.Markdown(data["context"], selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB)], scroll=ft.ScrollMode.ALWAYS), height=250, padding=10, bgcolor=ft.Colors.WHITE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.GREY_800, border_radius=10, border=ft.Border.all(1, ft.Colors.GREY_300))]), padding=15, bgcolor=ft.Colors.BLUE_50 if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.GREY_900, border_radius=15, border=ft.Border.all(1, ft.Colors.BLUE_200), margin=ft.Margin(0, 0, 0, 10))
        top_row_controls = [ft.Text(f"Сұрақ {idx + 1}/{total}", weight="bold", color=get_text_color()), ft.IconButton(ft.Icons.CALCULATE, icon_color=THEME_COLOR, tooltip="Калькулятор", on_click=open_calculator)]
        page.add(ft.Column([ft.Row(top_row_controls, alignment="spaceBetween", width=320), ft.Row(progress_circles, alignment=ft.MainAxisAlignment.CENTER, spacing=5), ft.Container(height=10), context_block, ft.Container(content=ft.Text(data["q"], size=18, weight="bold", text_align="center", color=get_text_color()), padding=20, bgcolor=get_card_color(), width=320, border_radius=15, shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.05, "black"))), ft.Container(height=10), options_container, ft.Container(height=10), btn_next, ft.Container(height=20)], scroll=ft.ScrollMode.AUTO, horizontal_alignment="center", expand=True))

    def next_q(): state["current_index"] += 1; load_question_screen()

    def show_result_screen():
        page.clean(); page.bgcolor = get_bg_color()
        db.save_result(state["user"]["id"], state["current_subject"], state["score"], len(state["questions"]))
        score = state["score"]; total = len(state["questions"]); percent = int((score/total) * 100) if total > 0 else 0
        color = ft.Colors.GREEN if percent >= 80 else (ft.Colors.ORANGE if percent >= 50 else ft.Colors.RED)
        content = ft.Column([ft.Icon(ft.Icons.EMOJI_EVENTS_ROUNDED, size=80, color=color), ft.Text("Нәтиже", size=28, weight="bold", color=color), ft.Text(f"{score} / {total}", size=40, weight="bold", color=get_text_color()), ft.ProgressBar(value=percent/100, color=color, bgcolor=ft.Colors.GREY_200, height=10), ft.Text(f"{percent}%", weight="bold", color=get_text_color()), ft.Container(height=20), ft.FilledButton("Қатемен жұмыс", icon=ft.Icons.ASSIGNMENT_LATE, width=250, on_click=lambda e: show_mistakes_screen(), style=ft.ButtonStyle(bgcolor=ft.Colors.RED_400)), ft.FilledButton("Мәзірге оралу", width=250, on_click=lambda e: show_student_menu())], horizontal_alignment="center", spacing=10)
        page.add(ft.Container(content=create_card(content, padding=40), alignment=ft.Alignment(0, 0), expand=True))

    def show_mistakes_screen():
        page.clean(); page.bgcolor = get_bg_color()
        lv = ft.ListView(expand=True, spacing=15, padding=10)
        for item in state["answers_log"]:
            is_cor = item['is_correct']; icon = ft.Icons.CHECK_CIRCLE if is_cor else ft.Icons.CANCEL; color = ft.Colors.GREEN if is_cor else ft.Colors.RED
            expl_content = ft.Column([ft.Divider(), ft.Text(f"Дұрыс жауап: {item['correct_answer']}", color=ft.Colors.GREEN, weight="bold"), ft.Text(f"Түсіндірме: {item['explanation']}", italic=True, size=12, color=get_text_color())]) if not is_cor else ft.Container()
            card = ft.Container(content=ft.Column([ft.Row([ft.Icon(icon, color=color), ft.Text("Дұрыс" if is_cor else "Қате", color=color, weight="bold")]), ft.Text(item['question'], weight="bold", size=16, color=get_text_color()), ft.Text(f"Сіздің жауап: {item['your_answer']}", color=color), expl_content]), padding=15, bgcolor=get_card_color(), border_radius=12, border=ft.Border.all(1, color), shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.with_opacity(0.1, "black")))
            lv.controls.append(card)
        page.add(ft.Column([ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_student_menu()), ft.Text("Қатемен жұмыс", size=20, weight="bold", color=get_text_color())]), lv], expand=True))

    def show_reference_screen():
        page.clean(); page.bgcolor = get_bg_color()
        content_column = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        def load_history(e=None):
            btn_history.style = ft.ButtonStyle(bgcolor=THEME_COLOR, color="white"); btn_math.style = ft.ButtonStyle(bgcolor=ft.Colors.TRANSPARENT, color=get_text_color()); content_column.controls.clear()
            for item in HISTORY_DATES: content_column.controls.append(ft.Container(content=ft.Column([ft.Text(item['date'], weight="bold", color=THEME_COLOR, size=16), ft.Text(item['event'], color=get_text_color())]), padding=10, bgcolor=get_card_color(), border_radius=10, border=ft.Border.all(1, ft.Colors.GREY_300)))
            page.update()
        def load_math(e=None):
            btn_math.style = ft.ButtonStyle(bgcolor=ft.Colors.ORANGE, color="white"); btn_history.style = ft.ButtonStyle(bgcolor=ft.Colors.TRANSPARENT, color=get_text_color()); content_column.controls.clear()
            for item in MATH_FORMULAS: content_column.controls.append(ft.Container(content=ft.Row([ft.Text(item['name'], expand=True, color=get_text_color()), ft.Container(content=ft.Text(item['formula'], weight="bold", color="white"), bgcolor=ft.Colors.ORANGE_400, padding=5, border_radius=5)], alignment="spaceBetween"), padding=10, bgcolor=get_card_color(), border_radius=10, border=ft.Border.all(1, ft.Colors.GREY_300)))
            page.update()
        btn_history = ft.FilledButton("Тарих", on_click=load_history, expand=True); btn_math = ft.FilledButton("Мат", on_click=load_math, expand=True)
        load_history(); page.add(ft.Column([ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_student_menu()), ft.Text("Анықтамалық", size=20, weight="bold", color=get_text_color())]), ft.Row([btn_history, btn_math], spacing=10), content_column], expand=True))

    def show_resources_screen():
        page.clean(); page.bgcolor = get_bg_color()
        def resource_card(title, desc, url, icon, color): return ft.Container(content=ft.Row([ft.Container(content=ft.Icon(icon, color="white"), bgcolor=color, padding=10, border_radius=10), ft.Column([ft.Text(title, weight="bold", color=get_text_color()), ft.Text(desc, size=12, color=SECONDARY_TEXT)], expand=True), ft.IconButton(ft.Icons.OPEN_IN_NEW, on_click=lambda e: webbrowser.open(url))], alignment="spaceBetween"), padding=15, bgcolor=get_card_color(), border_radius=12, border=ft.Border.all(1, ft.Colors.GREY_300))
        page.add(ft.Column([ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_student_menu()), ft.Text("Ресурстар", size=20, weight="bold", color=get_text_color())]), ft.ListView([resource_card("ҰТО", "Ресми сайт", "https://testcenter.kz/", ft.Icons.PUBLIC, ft.Colors.BLUE), resource_card("Daryn", "Видеосабақтар", "https://daryn.online/", ft.Icons.PLAY_CIRCLE, ft.Colors.ORANGE)], spacing=10, expand=True)], expand=True))

    def show_my_results():
        page.clean(); page.bgcolor = get_bg_color()
        results = db.get_my_results(state['user']['id'])
        total_tests = len(results)
        if total_tests > 0: avg_percent = int(sum([(r['score'] / r['total'] * 100) for r in results if r['total'] > 0]) / total_tests)
        else: avg_percent = 0
        stat_color = ft.Colors.GREEN if avg_percent >= 80 else (ft.Colors.ORANGE if avg_percent >= 50 else ft.Colors.RED)
        stats_card = ft.Container(content=ft.Column([ft.Text("Жалпы статистика", size=18, weight="bold", color=get_text_color()), ft.Divider(), ft.Row([ft.Text("Орташа нәтиже:", size=16, color=SECONDARY_TEXT), ft.Text(f"{avg_percent}%", size=24, weight="bold", color=stat_color)], alignment="spaceBetween"), ft.ProgressBar(value=avg_percent/100, color=stat_color, bgcolor=ft.Colors.GREY_200, height=15, border_radius=10), ft.Container(height=10), ft.Row([ft.Icon(ft.Icons.ASSIGNMENT, color=THEME_COLOR), ft.Text(f"Тапсырылған тест саны: {total_tests}", size=16, color=get_text_color())]), ft.Text("Жақсы нәтиже! Дайындықты тоқтатпаңыз.", size=12, color=SECONDARY_TEXT, italic=True)]), padding=20, bgcolor=get_card_color(), border_radius=20, shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, "black")))
        lv = ft.ListView(expand=True, spacing=10, padding=10)
        if not results: lv.controls.append(ft.Text("Нәтиже жоқ", italic=True, color=get_text_color())); stats_card.visible = False 
        else:
            for r in results:
                percent = int((r['score'] / r['total']) * 100) if r['total'] > 0 else 0
                badge_color = ft.Colors.GREEN if percent >= 80 else (ft.Colors.ORANGE if percent >= 50 else ft.Colors.RED)
                lv.controls.append(ft.Container(content=ft.Row([ft.Column([ft.Text(f"{r['subject']}", weight="bold", color=get_text_color()), ft.Text(f"{r['date']}", size=12, color=SECONDARY_TEXT)]), ft.Container(content=ft.Text(f"{r['score']} / {r['total']}", color="white", size=14, weight="bold"), bgcolor=badge_color, padding=ft.Padding(left=12, top=6, right=12, bottom=6), border_radius=8)], alignment="spaceBetween"), padding=15, bgcolor=get_card_color(), border_radius=12, border=ft.Border.all(1, ft.Colors.GREY_600 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.GREY_300), shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.with_opacity(0.05, "black"))))
        page.add(ft.Column([ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_student_menu()), ft.Text("Нәтижелер тарихы", size=20, weight="bold", color=get_text_color())]), stats_card, ft.Text("Соңғы тапсырылған тесттер:", size=14, color=SECONDARY_TEXT, weight="bold"), lv], expand=True))

    # --- 6. ПРОФИЛЬ БЕТІ (ЖАҢА ТЕРЕЗЕ АРҚЫЛЫ ӨЗГЕРТУ) ---
    def show_profile_screen():
        page.clean()
        page.bgcolor = get_bg_color()
        
        # Статистиканы аламыз
        total_tests, avg_score = db.get_user_stats(state['user']['id'])
        
        # --- 1. ҚҰПИЯ СӨЗДІ ӨЗГЕРТУ ТЕРЕЗЕСІ (OVERLAY) ---
        new_pass_input = ft.TextField(
            label="Жаңа құпия сөз", 
            password=True, 
            can_reveal_password=True, 
            border_radius=12,
            width=280
        )
        
        def close_change_modal(e=None):
            change_pass_container.visible = False
            page.update()

        def save_new_password(e):
            new_pass = new_pass_input.value
            if not new_pass:
                page.snack_bar = ft.SnackBar(ft.Text("Құпия сөз бос болмауы керек!"), bgcolor="red")
                page.snack_bar.open = True; page.update(); return

            if db.change_password(state['user']['id'], new_pass):
                state['user']['password'] = new_pass # State жаңарту
                
                # Негізгі экрандағы жазуды жаңарту
                current_pass_text.value = new_pass
                
                page.snack_bar = ft.SnackBar(ft.Text("Құпия сөз өзгертілді! ✅"), bgcolor="green")
                close_change_modal()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Қате орын алды!"), bgcolor="red")
            
            page.snack_bar.open = True; page.update()

        # Модальды терезе контейнері
        change_pass_card = ft.Container(
            content=ft.Column([
                ft.Text("Құпия сөзді өзгерту", size=20, weight="bold", color=get_text_color()),
                ft.Text("Жаңа құпия сөзді енгізіңіз", size=12, color=SECONDARY_TEXT),
                ft.Divider(height=20, color="transparent"),
                new_pass_input,
                ft.Container(height=10),
                ft.Row([
                    ft.OutlinedButton("Болдырмау", on_click=close_change_modal),
                    ft.FilledButton("Сақтау", on_click=save_new_password)
                ], alignment="center")
            ], horizontal_alignment="center"),
            padding=30, bgcolor=get_card_color(), border_radius=20,
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.3, "black")),
            alignment=ft.Alignment(0, 0)
        )

        change_pass_container = ft.Container(
            content=change_pass_card,
            visible=False, # Басында жабық
            expand=True,
            alignment=ft.Alignment(0, 0),
            bgcolor=ft.Colors.with_opacity(0.4, "black"),
            on_click=lambda e: None
        )

        def open_change_modal(e):
            new_pass_input.value = "" # Тазалау
            change_pass_container.visible = True
            page.update()

        # --- 2. НЕГІЗГІ ЭКРАН ЭЛЕМЕНТТЕРІ ---
        
        # Аватар
        header_section = ft.Column([
            ft.Container(
                content=ft.Text(state['user']['full_name'][0], size=40, weight="bold", color="white"),
                width=100, height=100, bgcolor=THEME_COLOR, border_radius=50,
                alignment=ft.Alignment(0, 0), shadow=ft.BoxShadow(blur_radius=10, color=THEME_COLOR)
            ),
            ft.Text(state['user']['full_name'], size=22, weight="bold", color=get_text_color(), text_align="center"),
            ft.Container(content=ft.Text("Оқушы", color="white", size=12), bgcolor=ft.Colors.GREEN, padding=5, border_radius=5)
        ], horizontal_alignment="center", spacing=5)

        # Статистика
        def stat_box(title, value, color, icon):
            return ft.Container(
                content=ft.Column([
                    ft.Icon(icon, color=color, size=30),
                    ft.Text(str(value), size=24, weight="bold", color=get_text_color()),
                    ft.Text(title, size=12, color=SECONDARY_TEXT)
                ], horizontal_alignment="center", spacing=2),
                padding=15, bgcolor=get_card_color(), border_radius=15, width=160,
                border=ft.Border.all(1, ft.Colors.GREY_300),
                shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.05, "black"))
            )

        stats_row = ft.Row([
            stat_box("Тесттер", total_tests, ft.Colors.BLUE, ft.Icons.QUIZ),
            stat_box("Орташа %", int(avg_score), ft.Colors.ORANGE, ft.Icons.PERCENT)
        ], alignment="center")

        # --- ҚАУІПСІЗДІК БЛОГЫ (СІЗ СҰРАҒАН ЖЕР) ---
        
        # Парольді көрсететін өріс (тек оқу үшін)
        current_pass_text = ft.TextField(
            value=state['user']['password'],
            label="Құпия сөз",
            read_only=True, # Өзгертуге болмайды (тек көруге)
            password=True, 
            can_reveal_password=True, # Көруге болады
            border="none", # Жиегі жоқ, әдемі көрінеді
            text_style=ft.TextStyle(size=18, weight="bold", color=THEME_COLOR),
            width=200
        )

        security_card = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.LOCK, color=SECONDARY_TEXT), ft.Text("Қауіпсіздік деректері", weight="bold", color=SECONDARY_TEXT)]),
                ft.Divider(),
                
                # Логин
                ft.Row([
                    ft.Text("Логин:", width=100, color=get_text_color()),
                    ft.Text(f"@{state['user']['username']}", weight="bold", size=16, color=get_text_color())
                ], alignment="start"),
                
                # Құпия сөз (сіз сұрағандай екі нүктеден соң)
                ft.Row([
                    ft.Text("Құпия сөз:", width=100, color=get_text_color()), # Екі нүкте
                    current_pass_text # Пароль (жұлдызшамен)
                ], alignment="start", vertical_alignment="center"),
                
                ft.Container(height=10),
                
                # Батырма (Жаңа терезе ашады)
                ft.OutlinedButton(
                    "Құпия сөзді өзгерту", 
                    icon=ft.Icons.EDIT, 
                    width=300, 
                    on_click=open_change_modal
                )
            ]),
            padding=20, bgcolor=get_card_color(), border_radius=15,
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.1, "black"))
        )

        # Негізгі экран жинақтау
        main_column = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_student_menu()),
                    ft.Text("Менің профилім", size=20, weight="bold", color=get_text_color())
                ]),
                ft.Container(height=10),
                ft.Column([
                    header_section,
                    ft.Container(height=20),
                    stats_row,
                    ft.Container(height=20),
                    security_card
                ], horizontal_alignment="center", spacing=10)
            ], scroll=ft.ScrollMode.AUTO),
            padding=20,
            expand=True
        )

        page.add(ft.Stack([
            main_column,
            change_pass_container # Overlay (үстінде тұрады)
        ], expand=True))
    # --- СҰРАҚ ҚОСУ ФУНКЦИЯСЫ (ОСЫ ЖЕТІСПЕЙ ТҰР) ---
    def show_add_question_screen():
        page.clean()
        page.bgcolor = get_bg_color()
        
        # Енгізу өрістері
        subject_dd = ft.Dropdown(
            label="Пән", 
            options=[
                ft.dropdown.Option("Қазақстан тарихы"), 
                ft.dropdown.Option("Математикалық сауаттылық")
            ], 
            width=350, 
            border_radius=10
        )
        
        q_text = ft.TextField(label="Сұрақ", multiline=True, width=350, border_radius=10)
        
        # Жауаптар
        opt1 = ft.TextField(label="Дұрыс жауап", width=350, border_radius=10, prefix_icon=ft.Icons.CHECK, color="green")
        opt2 = ft.TextField(label="Қате жауап 1", width=350, border_radius=10, prefix_icon=ft.Icons.CLOSE, color="red")
        opt3 = ft.TextField(label="Қате жауап 2", width=350, border_radius=10, prefix_icon=ft.Icons.CLOSE, color="red")
        opt4 = ft.TextField(label="Қате жауап 3", width=350, border_radius=10, prefix_icon=ft.Icons.CLOSE, color="red")
        
        # Сақтау функциясы
        def save_q(e):
            # Тексеру: барлығы толтырылды ма?
            if not all([subject_dd.value, q_text.value, opt1.value, opt2.value, opt3.value, opt4.value]):
                page.snack_bar = ft.SnackBar(ft.Text("Барлық өрістерді толтырыңыз!"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return

            # Жауаптарды тізімге жинау
            options = [opt1.value, opt2.value, opt3.value, opt4.value]
            
            # Базаға сақтау
            if db.add_question(subject_dd.value, q_text.value, options, opt1.value):
                page.snack_bar = ft.SnackBar(ft.Text("Сұрақ сәтті сақталды! ✅"), bgcolor="green")
                # Өрістерді тазалау
                q_text.value = ""
                opt1.value = ""
                opt2.value = ""
                opt3.value = ""
                opt4.value = ""
                page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Қате орын алды!"), bgcolor="red")
            
            page.snack_bar.open = True
            page.update()

        # Интерфейс
        content = ft.Column([
            ft.Text("Жаңа сұрақ қосу", size=20, weight="bold", color=get_text_color()),
            subject_dd,
            q_text,
            ft.Divider(),
            ft.Text("Жауап нұсқалары:", size=14, color=SECONDARY_TEXT),
            opt1,
            opt2,
            opt3,
            opt4,
            ft.Container(height=10),
            ft.FilledButton("САҚТАУ", on_click=save_q, width=350, height=50, icon=ft.Icons.SAVE)
        ], horizontal_alignment="center", spacing=10)

        page.add(ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_teacher_menu()),
                ft.Text("Артқа", size=16, weight="bold", color=get_text_color())
            ]),
            ft.Container(
                content=content,
                padding=20,
                bgcolor=get_card_color(),
                border_radius=20,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, "black"))
            )
        ], scroll=ft.ScrollMode.AUTO, expand=True))
    
    # --- 7. TEACHER MENU (КІЛТ СӨЗ ТЕРЕЗЕСІ КҮШЕЙТІЛГЕН) ---
    def show_teacher_menu():
        page.clean()
        page.bgcolor = get_bg_color()
        
        # --- КІЛТ СӨЗДІ ӨЗГЕРТУ ТЕРЕЗЕСІ (ДИЗАЙН) ---
        
        # Жаңа кілт сөзді енгізу өрісі
        new_secret_input = ft.TextField(
            label="Жаңа кілт сөзді жазыңыз", 
            prefix_icon=ft.Icons.VPN_KEY, 
            border_radius=12,
            width=300
        )
        
        # Қазіргі кілт сөзді көрсететін мәтін
        current_key_text = ft.Text(
            value="...", 
            size=20, 
            weight="bold", 
            color=THEME_COLOR,
            font_family="monospace" # Код сияқты көріну үшін
        )

        # Модальды терезенің ішкі мазмұны (Карточка)
        secret_card = ft.Container(
            padding=30,
            bgcolor=get_card_color(),
            border_radius=25,
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.2, "black"), offset=ft.Offset(0, 5)),
            border=ft.Border.all(1, ft.Colors.GREY_300),
            animate_scale=ft.Animation(300, ft.AnimationCurve.ELASTIC_OUT),
            scale=0.9, # Басында кішірейіп тұрады
            content=ft.Column([
                # Тақырып және Икона
                ft.Icon(ft.Icons.SECURITY_ROUNDED, size=50, color=THEME_COLOR),
                ft.Text("Құпия кілт сөз", size=22, weight="bold", color=get_text_color()),
                ft.Text("Оқушылар тіркелгенде осы сөзді сұрайды", size=12, color=SECONDARY_TEXT, text_align="center"),
                
                ft.Divider(height=20, color="transparent"),
                
                # Қазіргі кілт сөз блогы
                ft.Container(
                    content=ft.Column([
                        ft.Text("Қазіргі кілт сөз:", size=10, color=SECONDARY_TEXT),
                        current_key_text
                    ], horizontal_alignment="center", spacing=2),
                    padding=10,
                    bgcolor=ft.Colors.BLUE_50 if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.GREY_800,
                    border_radius=10,
                    width=300
                ),
                
                ft.Divider(height=10, color="transparent"),
                
                # Енгізу өрісі
                new_secret_input,
                
                ft.Divider(height=20, color="transparent"),
                
                # Батырмалар
                ft.Row([
                    ft.OutlinedButton("Жабу", on_click=lambda e: close_secret_modal(), height=45),
                    ft.FilledButton("САҚТАУ", on_click=lambda e: save_secret_key(), height=45, icon=ft.Icons.SAVE)
                ], alignment="center", spacing=20)
            ], horizontal_alignment="center", spacing=5)
        )

        # Overlay (Бүкіл экранды жабатын қабат)
        secret_modal = ft.Container(
            content=secret_card,
            visible=False,
            expand=True,
            alignment=ft.Alignment(0, 0),
            bgcolor=ft.Colors.with_opacity(0.4, "black"),
            on_click=lambda e: None # Сыртын басқанда жабылмау үшін
        )

        # --- ФУНКЦИЯЛАР ---

        def open_secret_modal(e):
            # Базадан қазіргі кілт сөзді аламыз
            current_val = db.get_current_secret()
            current_key_text.value = current_val
            new_secret_input.value = "" # Өрісті тазалаймыз
            
            secret_modal.visible = True
            secret_card.scale = 1.0 # Анимация: үлкейеді
            page.update()

        def close_secret_modal(e=None):
            secret_card.scale = 0.9 # Анимация: кішірейеді
            secret_card.update()
            time.sleep(0.1)
            secret_modal.visible = False
            page.update()

        def save_secret_key():
            if not new_secret_input.value:
                page.snack_bar = ft.SnackBar(ft.Text("Бос қалдыруға болмайды!"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return
            
            if db.update_secret_key(new_secret_input.value):
                page.snack_bar = ft.SnackBar(ft.Text(f"Кілт сөз жаңартылды! ✅"), bgcolor="green")
                close_secret_modal()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Қате орын алды!"), bgcolor="red")
            
            page.snack_bar.open = True
            page.update()

        # --- НЕГІЗГІ МӘЗІР ИНТЕРФЕЙСІ ---
        
        def menu_btn(title, icon, color, action):
            return ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=40, color="white"),
                    ft.Text(title, color="white", weight="bold", size=14, text_align="center")
                ], alignment="center", horizontal_alignment="center"),
                width=150, height=150,
                bgcolor=color,
                border_radius=25,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.2, "black")),
                on_click=action,
                ink=True,
                animate_scale=ft.Animation(100, "easeOut") # Басқанда кішірейю анимациясы
            )

        top_bar = ft.Row([
            ft.Row([
                ft.Icon(ft.Icons.SCHOOL, color=THEME_COLOR, size=30),
                ft.Text("ҰСТАЗ ПАНЕЛІ", size=20, weight="bold", color=THEME_COLOR)
            ]),
            ft.Row([
                ft.IconButton(ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE, on_click=toggle_theme),
                ft.IconButton(ft.Icons.LOGOUT, on_click=lambda e: show_login_screen(), icon_color="red")
            ])
        ], alignment="spaceBetween")

        # Негізгі контейнер
        main_content = ft.Container(
            content=ft.Column([
                top_bar,
                ft.Divider(),
                ft.Container(height=20), # Бос орын
                ft.Row([
                    menu_btn("Сұрақ қосу", ft.Icons.ADD_TASK, ft.Colors.INDIGO_400, lambda e: show_add_question_screen()),
                    menu_btn("Рейтинг", ft.Icons.LEADERBOARD, ft.Colors.TEAL_400, lambda e: show_leaderboard_screen())
                ], alignment="center", spacing=20),
                ft.Container(height=10),
                ft.Row([
                    menu_btn("Өшіру", ft.Icons.DELETE_FOREVER, ft.Colors.RED_400, lambda e: show_delete_questions_screen()),
                    menu_btn("Кілт сөз", ft.Icons.VPN_KEY, ft.Colors.ORANGE_400, lambda e: open_secret_modal(e))
                ], alignment="center", spacing=20)
            ], horizontal_alignment="center"),
            padding=20
        )

        page.add(ft.Stack([
            main_content,
            secret_modal # Overlay ең соңында тұрады
        ], expand=True))
    def show_leaderboard_screen():
        page.clean(); page.bgcolor = get_bg_color()
        leaders = db.get_leaderboard_general()
        lv = ft.ListView(expand=True, spacing=10, padding=15)
        def export_to_excel(e):
            if not leaders: page.snack_bar = ft.SnackBar(ft.Text("Деректер жоқ, жүктеу мүмкін емес!"), bgcolor="red"); page.snack_bar.open = True; page.update(); return
            try:
                df = pd.DataFrame(leaders); headers = {"full_name": "Оқушының аты-жөні", "history": "Қазақстан тарихы", "math": "Математикалық сауаттылық", "reading": "Оқу сауаттылығы", "total_score": "Жалпы ұпай"}; df.rename(columns=headers, inplace=True); filename = "Rating_Result.xlsx"; df.to_excel(filename, index=False)
                page.snack_bar = ft.SnackBar(ft.Text(f"Файл '{filename}' сәтті жүктелді! ✅"), bgcolor="green"); page.snack_bar.open = True; page.update(); os.startfile(filename)
            except Exception as ex: page.snack_bar = ft.SnackBar(ft.Text(f"Қате: {str(ex)}"), bgcolor="red"); page.snack_bar.open = True; page.update()
        top_bar = ft.Row([ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_teacher_menu() if state['user']['role'] == 'teacher' else show_student_menu()), ft.Text("Үздік оқушылар", size=24, weight="bold", color=get_text_color())]), ft.FilledButton("Excel", icon=ft.Icons.DOWNLOAD, style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE), on_click=export_to_excel, visible=(state['user']['role'] in ['teacher', 'admin']))], alignment="spaceBetween")
        if not leaders: lv.controls.append(ft.Container(content=ft.Text("Әзірге нәтижелер жоқ", italic=True, color=SECONDARY_TEXT), alignment=ft.Alignment(0, 0), padding=20))
        else:
            for i, row in enumerate(leaders):
                rank = i + 1; rank_color = "#FFD700" if rank == 1 else ("#C0C0C0" if rank == 2 else ("#CD7F32" if rank == 3 else ft.Colors.BLUE_GREY_200)); rank_content = ft.Icon(ft.Icons.WORKSPACE_PREMIUM if rank == 1 else (ft.Icons.LOOKS_TWO if rank == 2 else ft.Icons.LOOKS_3), color="white", size=20) if rank <= 3 else ft.Text(str(rank), color="white", weight="bold", size=16)
                def score_badge(icon, val, color): return ft.Container(content=ft.Row([ft.Icon(icon, size=14, color="white"), ft.Text(str(int(val)), size=12, color="white", weight="bold")], spacing=3, alignment="center"), bgcolor=color, padding=5, border_radius=8, width=65, height=25)
                card_content = ft.Row([ft.Container(content=rank_content, bgcolor=rank_color, width=40, height=40, border_radius=20, alignment=ft.Alignment(0, 0), shadow=ft.BoxShadow(blur_radius=5, color=rank_color)), ft.Column([ft.Text(row['full_name'], weight="bold", size=16, color=get_text_color()), ft.Row([score_badge(ft.Icons.HISTORY_EDU, row['history'], ft.Colors.BLUE_400), score_badge(ft.Icons.CALCULATE, row['math'], ft.Colors.ORANGE_400), score_badge(ft.Icons.MENU_BOOK, row['reading'], ft.Colors.GREEN_400)])], expand=True, spacing=5), ft.Column([ft.Text("Жалпы", size=10, color=SECONDARY_TEXT), ft.Text(f"{int(row['total_score'])}", weight="bold", size=20, color=THEME_COLOR)], horizontal_alignment="center")], alignment="spaceBetween")
                lv.controls.append(ft.Container(content=card_content, padding=15, bgcolor=get_card_color(), border_radius=15, border=ft.Border.all(2, rank_color if rank <= 3 else ft.Colors.TRANSPARENT), shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.05, "black")), animate_scale=ft.Animation(300, "easeOut")))
        page.add(ft.Column([top_bar, ft.Container(content=ft.Row([ft.Text("Тар: Тарих", size=12, color=SECONDARY_TEXT), ft.Text("Мат: Математика", size=12, color=SECONDARY_TEXT), ft.Text("Оқу: Оқу сауат.", size=12, color=SECONDARY_TEXT)], alignment="center", spacing=20), padding=5), lv], expand=True))

    def show_delete_questions_screen():
        page.clean()
        page.bgcolor = get_bg_color()
        
        # Барлық сұрақтарды аламыз
        all_questions = db.get_all_questions_for_teacher()
        
        # Сұрақтар тізімі (ListView)
        lv = ft.ListView(expand=True, spacing=10, padding=10)
        
        current_delete_id = {"id": None}

        # Модальды терезе (өшіруді растау)
        def close_modal(e): 
            modal_bg.visible = False
            page.update()

        def confirm_action(e):
            if db.delete_question(current_delete_id["id"]):
                page.snack_bar = ft.SnackBar(ft.Text("Өшірілді"), bgcolor="green")
                # Тізімді жаңарту
                nonlocal all_questions
                all_questions = [q for q in all_questions if q['id'] != current_delete_id["id"]]
                filter_questions(None)
            
            page.snack_bar.open = True
            close_modal(e)
        
        modal_bg = ft.Container(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Өшіруді растаңыз", weight="bold"),
                    ft.Row([
                        ft.TextButton("Жоқ", on_click=close_modal),
                        ft.FilledButton("Иә", on_click=confirm_action)
                    ])
                ], horizontal_alignment="center"),
                padding=30, bgcolor=get_card_color(), border_radius=20
            ),
            visible=False, expand=True, alignment=ft.Alignment(0, 0), bgcolor="#80000000"
        )

        def open_modal(e, q_id): 
            current_delete_id["id"] = q_id
            modal_bg.visible = True
            page.update()

        # Сүзгілеу және тізімді шығару функциясы
        def filter_questions(e):
            search_text = search_box.value.lower() if search_box.value else ""
            lv.controls.clear()
            
            filtered = [q for q in all_questions if search_text in q['question'].lower()]
            
            for q in filtered:
                lv.controls.append(
                    ft.Container(
                        content=ft.Row([
                            # 1. Мәтін бөлігі (expand=True қосылды - осы иконаны оңға итереді)
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(q['subject'], size=12, color=SECONDARY_TEXT),
                                    ft.Text(q['question'], size=14, color=get_text_color(), weight="bold", no_wrap=False)
                                ], spacing=2),
                                expand=True  # <--- ЕҢ МАҢЫЗДЫ ЖЕРІ ОСЫ
                            ),
                            
                            # 2. Өшіру иконасы
                            ft.IconButton(
                                ft.Icons.DELETE, 
                                icon_color="red", 
                                on_click=lambda e, qid=q['id']: open_modal(e, qid)
                            )
                        ], alignment="spaceBetween"), # Екі шетке жайғастыру
                        
                        padding=15,
                        bgcolor=get_card_color(),
                        border_radius=12,
                        border=ft.Border.all(1, ft.Colors.GREY_300)
                    )
                )
            try: lv.update()
            except: pass

        search_box = ft.TextField(
            label="Іздеу...", 
            prefix_icon=ft.Icons.SEARCH, 
            border_radius=10, 
            on_change=filter_questions
        )
        
        # Басында барлық сұрақты шығару
        filter_questions(None)

        page.add(ft.Stack([
            ft.Column([
                ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_teacher_menu()), 
                    ft.Text("Сұрақтар", size=20, weight="bold", color=get_text_color())
                ]),
                search_box,
                lv
            ], expand=True),
            modal_bg
        ], expand=True))
    # --- 8. ADMIN MENU (БАРЛЫҚ МӘСЕЛЕЛЕР ШЕШІЛГЕН) ---
    def show_admin_menu():
        page.clean()
        page.bgcolor = get_bg_color()
        
        # --- 1. ЭЛЕМЕНТТЕР ---
        users_list_view = ft.ListView(expand=True, spacing=10, padding=10)
        
        # ID сақтау үшін
        edit_id_ref = {"id": None} 
        
        # Өрістер (Ескі Flet-ке лайықталған: helper_text жоқ)
        txt_name = ft.TextField(label="Аты-жөні", prefix_icon=ft.Icons.PERSON_ROUNDED, border_radius=12, width=300)
        txt_login = ft.TextField(label="Логин", prefix_icon=ft.Icons.ALTERNATE_EMAIL_ROUNDED, border_radius=12, width=300)
        txt_pass = ft.TextField(label="Құпия сөз", prefix_icon=ft.Icons.VPN_KEY_ROUNDED, password=True, can_reveal_password=True, border_radius=12, width=300)
        
        # Dropdown (Ескі Flet-ке лайықталған: prefix_icon жоқ)
        dd_role = ft.Dropdown(
            label="Лауазымы",
            options=[
                ft.dropdown.Option("student", "Оқушы (Student)"),
                ft.dropdown.Option("teacher", "Мұғалім (Teacher)"),
                ft.dropdown.Option("admin", "Әкімші (Admin)"),
            ],
            border_radius=12,
            width=250 
        )

        # --- КАРТОЧКА (Стиль) ---
        edit_card = ft.Container(
            padding=30,
            bgcolor=get_card_color(), 
            border_radius=25,
            shadow=ft.BoxShadow(
                blur_radius=20, 
                color=ft.Colors.with_opacity(0.2, "black"), 
                offset=ft.Offset(0, 5)
            ),
            border=ft.Border.all(1, ft.Colors.GREY_300),
            # Анимацияны осыған береміз
            animate_scale=ft.Animation(300, ft.AnimationCurve.ELASTIC_OUT),
            scale=0.9, # Басында кішкентай болып тұрады
        )

        # --- OVERLAY (Бүкіл экранды жабатын қабат) ---
        # Мәселе осында болған. Енді біз осыны басқарамыз.
        edit_overlay = ft.Container(
            content=edit_card,
            visible=False, # БАСЫНДА ЖАСЫРЫН! Сондықтан батырмалар басылады.
            expand=True,
            alignment=ft.Alignment(0, 0), # Ортаға туралау
            bgcolor=ft.Colors.with_opacity(0.4, "black"), # Артқы фонды күңгірттеу
            on_click=lambda e: None # Форманың сыртын басқанда ештеңе болмауы үшін
        )

        # --- 2. ФУНКЦИЯЛАР ---

        def show_list_view(e=None):
            # Жабу анимациясы
            edit_card.scale = 0.9
            edit_card.update()
            time.sleep(0.1)
            
            edit_overlay.visible = False # Қабатты жасырамыз -> Астындағы батырмалар істейді
            page.update()
            load_users()

        def open_edit_mode(user):
            edit_id_ref["id"] = user['id']
            txt_name.value = user['full_name']
            txt_login.value = user['username']
            txt_pass.value = user['password']
            dd_role.value = user['role'] 
            
            edit_overlay.visible = True # Қабатты көрсетеміз
            edit_card.scale = 1.0 # Карточканы үлкейтеміз
            page.update()

        def save_changes(e):
            btn_save.disabled = True
            btn_save.text = "Сақталуда..."
            page.update()
            time.sleep(0.5)

            if db.update_user_info(edit_id_ref["id"], txt_login.value, txt_pass.value, txt_name.value, dd_role.value):
                page.snack_bar = ft.SnackBar(ft.Text("Деректер сәтті жаңартылды! 🎉"), bgcolor="green")
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Қате орын алды!"), bgcolor="red")
            
            btn_save.disabled = False
            btn_save.text = "САҚТАУ"
            page.snack_bar.open = True
            show_list_view()

        def delete_user_click(user_id):
            def confirm_delete(e):
                if db.delete_user(user_id):
                     page.snack_bar = ft.SnackBar(ft.Text("Өшірілді! 🗑️"), bgcolor="green")
                     load_users()
                else:
                     page.snack_bar = ft.SnackBar(ft.Text("Қате!"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

            page.snack_bar = ft.SnackBar(
                content=ft.Text("Бұл қолданушыны өшіруге сенімдісіз бе?"),
                action="Иә, өшір",
                action_color="red",
                on_action=confirm_delete,
                bgcolor=get_card_color(),
                duration=5000,
            )
            page.snack_bar.open = True
            page.update()

        # Интерфейс
        edit_header = ft.Row([
             ft.Icon(ft.Icons.EDIT_NOTE_ROUNDED, size=40, color=THEME_COLOR),
             ft.Column([
                 ft.Text("Деректерді өзгерту", size=22, weight="bold", color=get_text_color()),
                 ft.Text("Оқушының мәліметтерін жаңартыңыз", size=14, color=SECONDARY_TEXT)
             ], spacing=2)
        ], alignment="center")

        btn_save = ft.FilledButton("САҚТАУ", icon=ft.Icons.SAVE_ROUNDED, on_click=save_changes, height=50, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)), expand=True)
        btn_cancel = ft.OutlinedButton("Болдырмау", icon=ft.Icons.CLOSE_ROUNDED, on_click=show_list_view, height=50, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)))

        edit_card.content = ft.Column([
            edit_header,
            ft.Divider(height=20, color="transparent"),
            txt_name, txt_login, txt_pass, 
            ft.Row([ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS_ROUNDED, color=SECONDARY_TEXT), dd_role], alignment="center"),
            ft.Divider(height=20, color="transparent"),
            ft.Row([btn_cancel, btn_save], spacing=15, alignment="center")
        ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        def load_users(search_text=""):
            users_list_view.controls.clear()
            try: all_users = db.get_all_users()
            except: all_users = []
            
            if not all_users: 
                users_list_view.controls.append(ft.Container(content=ft.Text("Оқушылар жоқ", italic=True), alignment=ft.Alignment(0, 0), padding=20))
                page.update(); return

            filtered = [u for u in all_users if search_text.lower() in u['full_name'].lower() or search_text.lower() in u['username'].lower()]
            
            for u in filtered:
                if u['role'] == 'admin': role_color = ft.Colors.BLUE; role_text = "Әкімші"; icon = ft.Icons.ADMIN_PANEL_SETTINGS
                elif u['role'] == 'teacher': role_color = ft.Colors.ORANGE; role_text = "Мұғалім"; icon = ft.Icons.SCHOOL
                else: role_color = ft.Colors.GREEN; role_text = "Оқушы"; icon = ft.Icons.PERSON

                item = ft.Container(
                    content=ft.Row([
                        ft.Row([
                            ft.Container(content=ft.Icon(icon, color="white", size=24), bgcolor=role_color, padding=10, border_radius=12),
                            ft.Column([
                                ft.Text(u['full_name'], weight="bold", size=16, color=get_text_color()),
                                ft.Row([ft.Icon(ft.Icons.CIRCLE, size=8, color=role_color), ft.Text(f"@{u['username']} | {role_text}", size=12, color=SECONDARY_TEXT)], spacing=5, alignment="center"),
                                ft.Text(f"Пароль: {u['password']}", size=10, color="grey")
                            ], spacing=4)
                        ]),
                        ft.Row([
                            ft.IconButton(ft.Icons.EDIT, icon_color="blue", tooltip="Өзгерту", on_click=lambda e, x=u: open_edit_mode(x)),
                            ft.IconButton(ft.Icons.DELETE, icon_color="red", tooltip="Өшіру", on_click=lambda e, x=u['id']: delete_user_click(x))
                        ])
                    ], alignment="spaceBetween"),
                    padding=15, bgcolor=get_card_color(), border_radius=15,
                    border=ft.Border.all(1, ft.Colors.GREY_200 if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.GREY_800),
                    shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.05, "black")), animate_scale=ft.Animation(300, "easeOut")
                )
                users_list_view.controls.append(item)
            page.update()

        search_field = ft.TextField(label="Оқушыны іздеу...", prefix_icon=ft.Icons.SEARCH, border_radius=12, on_change=lambda e: load_users(e.control.value))
        
        def clear_leaderboard_click(e):
            db.clear_leaderboard()
            page.snack_bar = ft.SnackBar(ft.Text("Рейтинг тазартылды!"), bgcolor="green"); page.snack_bar.open = True; page.update()

        header = ft.Row([ft.Row([ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=30, color=THEME_COLOR), ft.Text("Әкімші тақтасы", size=24, weight="bold", color=THEME_COLOR)]), ft.IconButton(ft.Icons.LOGOUT_ROUNDED, icon_color="red", tooltip="Шығу", on_click=lambda e: show_login_screen())], alignment="spaceBetween")

        main_column = ft.Container(
            content=ft.Column([
                ft.Container(content=header, padding=10),
                ft.Container(content=ft.Row([ft.FilledButton("Рейтингті нөлдеу", icon=ft.Icons.CLEANING_SERVICES, on_click=clear_leaderboard_click, style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE, shape=ft.RoundedRectangleBorder(radius=10))), ft.IconButton(ft.Icons.DARK_MODE, on_click=toggle_theme, tooltip="Тақырыпты өзгерту")], alignment="spaceBetween"), padding=5),
                ft.Container(content=search_field, padding=10),
                ft.Text("  Тіркелген қолданушылар:", weight="bold", color=SECONDARY_TEXT),
                users_list_view
            ], expand=True),
            expand=True,
            padding=20
        )

        # МАҢЫЗДЫ ЖЕРІ: edit_overlay (Visible=False) қазір батырмаларға кедергі жасамайды!
        page.add(ft.Stack([
            main_column, 
            edit_overlay 
        ], expand=True))
        
        load_users()

    show_login_screen()

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
