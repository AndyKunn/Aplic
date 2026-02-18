import kivy
import os
import json
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle, RoundedRectangle

# ═══════════════════════════════════════════════════════════
#  PALĪGFUNKCIJAS — работа с файлами вместо БД
# ═══════════════════════════════════════════════════════════

DATA_DIR = "user_data"

def ensure_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def get_user_file(username):
    return os.path.join(DATA_DIR, f"{username}.json")

def load_user_data(username):
    path = get_user_file(username)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_user_data(username, data):
    ensure_dir()
    with open(get_user_file(username), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_new_user(username, email, password):
    data = {
        "username": username,
        "email": email,
        "password": password,
        "punkti": 0,
        "izaicinajumi": [],
        "rezultati": [],
        "sasniegumi": []
    }
    save_user_data(username, data)
    return data

def add_achievement(data, title, description, punkti):
    data["sasniegumi"].append({
        "title": title,
        "description": description,
        "punkti": punkti,
        "datums": datetime.now().strftime("%d.%m.%Y %H:%M")
    })
    data["punkti"] += punkti

# ═══════════════════════════════════════════════════════════
#  STILS — общие цвета и хелперы для виджетов
# ═══════════════════════════════════════════════════════════

BG_COLOR      = (0.07, 0.07, 0.13, 1)   # тёмно-синий фон
CARD_COLOR    = (0.12, 0.12, 0.22, 1)   # карточки
ACCENT        = (0.2, 0.6, 1.0, 1)      # синий акцент
ACCENT2       = (0.1, 0.85, 0.6, 1)     # зелёный акцент
DANGER        = (1.0, 0.35, 0.35, 1)    # красный
TEXT_PRIMARY  = (1, 1, 1, 1)
TEXT_SECONDARY= (0.65, 0.65, 0.8, 1)


def make_button(text, bg=ACCENT, text_color=(1,1,1,1), font_size=16, height=48):
    btn = Button(
        text=text,
        font_size=font_size,
        size_hint=(1, None),
        height=height,
        background_normal="",
        background_color=bg,
        color=text_color,
        bold=True
    )
    return btn


def make_label(text, font_size=16, color=TEXT_PRIMARY, bold=False,
               height=30, halign="left", size_hint_y=None):
    lbl = Label(
        text=text,
        font_size=font_size,
        color=color,
        bold=bold,
        size_hint=(1, None),
        height=height,
        halign=halign,
        text_size=(None, None)
    )
    lbl.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
    return lbl


def make_input(hint="", password=False, height=44):
    return TextInput(
        hint_text=hint,
        multiline=False,
        font_size=16,
        size_hint=(1, None),
        height=height,
        password=password,
        background_color=(0.18, 0.18, 0.3, 1),
        foreground_color=(1, 1, 1, 1),
        hint_text_color=(0.5, 0.5, 0.7, 1),
        cursor_color=(0.2, 0.6, 1, 1),
        padding=[12, 10]
    )


def make_scrollable_box(spacing=10, padding=20):
    scroll = ScrollView(size_hint=(1, 1))
    box = BoxLayout(
        orientation="vertical",
        size_hint_y=None,
        spacing=spacing,
        padding=padding
    )
    box.bind(minimum_height=box.setter("height"))
    scroll.add_widget(box)
    return scroll, box


def show_popup(title, message, ok_text="Labi"):
    content = BoxLayout(orientation="vertical", padding=20, spacing=10)
    content.add_widget(Label(text=message, color=TEXT_PRIMARY, font_size=15))
    btn = make_button(ok_text, height=44)
    content.add_widget(btn)
    popup = Popup(
        title=title,
        content=content,
        size_hint=(0.85, None),
        height=220,
        background="",
        background_color=CARD_COLOR,
        title_color=ACCENT,
        title_size=18
    )
    btn.bind(on_press=popup.dismiss)
    popup.open()
    return popup


def set_bg(widget, color):
    with widget.canvas.before:
        Color(*color)
        rect = Rectangle(size=widget.size, pos=widget.pos)
    widget.bind(size=lambda w, v: setattr(rect, "size", v))
    widget.bind(pos=lambda w, v: setattr(rect, "pos", v))


# ═══════════════════════════════════════════════════════════
#  NAVIGĀCIJAS JOSLA — нижняя навигация
# ═══════════════════════════════════════════════════════════

class NavBar(BoxLayout):
    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (1, None)
        self.height = 60
        self.sm = screen_manager
        set_bg(self, (0.08, 0.08, 0.18, 1))

        tabs = [
            ("challenges", "Izaicinājumi", "challenges"),
            ("results", "Rezultāti",    "results"),
            ("points", "Punkti",       "points"),
            ("profile", "Profils",      "profile"),
        ]
        for icon, label, screen in tabs:
            btn = Button(
                text=f"{icon}\n{label}",
                font_size=11,
                background_normal="",
                background_color=(0, 0, 0, 0),
                color=TEXT_SECONDARY,
                halign="center"
            )
            btn.screen_name = screen
            btn.bind(on_press=self.switch)
            self.add_widget(btn)

    def switch(self, btn):
        self.sm.current = btn.screen_name
        for child in self.children:
            child.color = TEXT_SECONDARY
        btn.color = ACCENT


# ═══════════════════════════════════════════════════════════
#  1. REĢISTRĀCIJA — экран регистрации
# ═══════════════════════════════════════════════════════════

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")
        set_bg(root, BG_COLOR)

        # Заголовок
        header = BoxLayout(size_hint=(1, None), height=80, padding=[20, 15])
        set_bg(header, (0.05, 0.05, 0.12, 1))
        title = Label(
            text="[b]🏃 Sporta Aplikācija[/b]",
            markup=True, font_size=22,
            color=ACCENT, size_hint=(1,1)
        )
        header.add_widget(title)
        root.add_widget(header)

        scroll, box = make_scrollable_box(spacing=12, padding=[30, 20])

        box.add_widget(make_label("Reģistrācija", font_size=20, bold=True,
                                  color=TEXT_PRIMARY, height=35, halign="center"))
        box.add_widget(make_label("Izveidojiet savu kontu", font_size=14,
                                  color=TEXT_SECONDARY, height=25, halign="center"))
        box.add_widget(Label(size_hint=(1, None), height=10))

        box.add_widget(make_label("Vārds:", color=TEXT_SECONDARY, height=24))
        self.name_input = make_input("Ievadiet vārdu")
        box.add_widget(self.name_input)

        box.add_widget(make_label("E-pasts:", color=TEXT_SECONDARY, height=24))
        self.email_input = make_input("Ievadiet e-pastu")
        box.add_widget(self.email_input)

        box.add_widget(make_label("Parole:", color=TEXT_SECONDARY, height=24))
        self.password_input = make_input("Ievadiet paroli", password=True)
        box.add_widget(self.password_input)

        box.add_widget(make_label("Apstiprināt paroli:", color=TEXT_SECONDARY, height=24))
        self.confirm_input = make_input("Atkārtojiet paroli", password=True)
        box.add_widget(self.confirm_input)

        box.add_widget(Label(size_hint=(1, None), height=10))

        reg_btn = make_button("Reģistrēties", height=52, font_size=17)
        reg_btn.bind(on_press=self.register)
        box.add_widget(reg_btn)

        login_btn = make_button("Jau ir konts? Ieiet", bg=CARD_COLOR, height=44)
        login_btn.bind(on_press=lambda x: setattr(self.manager, "current", "login"))
        box.add_widget(login_btn)

        root.add_widget(scroll)
        self.add_widget(root)

    def register(self, _):
        name     = self.name_input.text.strip()
        email    = self.email_input.text.strip()
        password = self.password_input.text.strip()
        confirm  = self.confirm_input.text.strip()

        if not all([name, email, password, confirm]):
            show_popup("Kļūda", "Lūdzu aizpildiet visus laukus!")
            return
        if password != confirm:
            show_popup("Kļūda", "Paroles nesakrīt!")
            return
        if load_user_data(name):
            show_popup("Kļūda", "Šāds lietotājs jau eksistē!")
            return

        data = create_new_user(name, email, password)
        add_achievement(data, "Laipni lūgts!", "Reģistrējies aplikācijā", 50)
        save_user_data(name, data)

        App.get_running_app().current_user = name
        show_popup("Veiksmīgi!", f"Sveiks, {name}!\nTu saņēmi 50 punktus par reģistrāciju! ")
        for inp in [self.name_input, self.email_input, self.password_input, self.confirm_input]:
            inp.text = ""
        self.manager.current = "challenges"
        App.get_running_app().navbar.switch(App.get_running_app().navbar.children[-1])


# ═══════════════════════════════════════════════════════════
#  2. IEIET — экран входа
# ═══════════════════════════════════════════════════════════

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")
        set_bg(root, BG_COLOR)

        header = BoxLayout(size_hint=(1, None), height=80, padding=[20, 15])
        set_bg(header, (0.05, 0.05, 0.12, 1))
        header.add_widget(Label(
            text="[b]🏃 Sporta Aplikācija[/b]",
            markup=True, font_size=22, color=ACCENT
        ))
        root.add_widget(header)

        scroll, box = make_scrollable_box(spacing=12, padding=[30, 40])

        box.add_widget(make_label("Ienākšana", font_size=20, bold=True,
                                  color=TEXT_PRIMARY, height=35, halign="center"))
        box.add_widget(Label(size_hint=(1, None), height=20))

        box.add_widget(make_label("Vārds:", color=TEXT_SECONDARY, height=24))
        self.name_input = make_input("Ievadiet vārdu")
        box.add_widget(self.name_input)

        box.add_widget(make_label("Parole:", color=TEXT_SECONDARY, height=24))
        self.password_input = make_input("Ievadiet paroli", password=True)
        box.add_widget(self.password_input)

        box.add_widget(Label(size_hint=(1, None), height=10))

        login_btn = make_button("Ieiet", height=52, font_size=17)
        login_btn.bind(on_press=self.login)
        box.add_widget(login_btn)

        reg_btn = make_button("Nav konta? Reģistrēties", bg=CARD_COLOR, height=44)
        reg_btn.bind(on_press=lambda x: setattr(self.manager, "current", "register"))
        box.add_widget(reg_btn)

        root.add_widget(scroll)
        self.add_widget(root)

    def login(self, _):
        name     = self.name_input.text.strip()
        password = self.password_input.text.strip()

        if not name or not password:
            show_popup("Kļūda", "Aizpildiet visus laukus!")
            return

        data = load_user_data(name)
        if not data or data.get("password") != password:
            show_popup("Kļūda", "Nepareizs vārds vai parole!")
            return

        App.get_running_app().current_user = name
        self.name_input.text = ""
        self.password_input.text = ""
        self.manager.current = "challenges"
        App.get_running_app().navbar.switch(App.get_running_app().navbar.children[-1])


# ═══════════════════════════════════════════════════════════
#  3. IZAICINĀJUMI — экран вызовов
# ═══════════════════════════════════════════════════════════

SPORTS = ["Skriešana", "Peldēšana", "Riteņbraukšana", "Basketbols",
          "Futbols", "Volejbols", "Vingrošana", "Cits"]

class ChallengesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        set_bg(root, BG_COLOR)

        # Header
        header = BoxLayout(size_hint=(1, None), height=65, padding=[20, 10])
        set_bg(header, (0.05, 0.05, 0.12, 1))
        header.add_widget(Label(
            text="[b]Izaicinājumi[/b]",
            markup=True, font_size=20, color=ACCENT
        ))
        root.add_widget(header)

        scroll, self.list_box = make_scrollable_box(spacing=10, padding=[15, 15])

        # Кнопка создания
        create_btn = make_button("+ Izveidot izaicinājumu", bg=ACCENT2,
                                 text_color=(0,0,0,1), height=52, font_size=16)
        create_btn.bind(on_press=self.open_create_popup)
        self.list_box.add_widget(create_btn)

        self.list_box.add_widget(make_label("Mani izaicinājumi:", bold=True,
                                            color=TEXT_SECONDARY, height=28))
        self.challenge_container = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=8
        )
        self.challenge_container.bind(minimum_height=self.challenge_container.setter("height"))
        self.list_box.add_widget(self.challenge_container)

        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        self.refresh_challenges()

    def refresh_challenges(self):
        self.challenge_container.clear_widgets()
        app = App.get_running_app()
        if not app.current_user:
            return
        data = load_user_data(app.current_user)
        if not data or not data.get("izaicinajumi"):
            self.challenge_container.add_widget(
                make_label("Nav izaicinājumu. Izveidojiet savu pirmo!",
                           color=TEXT_SECONDARY, height=40, halign="center")
            )
            return

        for ch in reversed(data["izaicinajumi"]):
            card = self._make_challenge_card(ch)
            self.challenge_container.add_widget(card)

    def _make_challenge_card(self, ch):
        card = BoxLayout(orientation="vertical", size_hint=(1, None),
                         height=100, padding=[15, 10], spacing=4)
        set_bg(card, CARD_COLOR)

        top = BoxLayout(size_hint=(1, None), height=28)
        top.add_widget(Label(
            text=f"[b]{ch['title']}[/b]",
            markup=True, font_size=16, color=ACCENT,
            size_hint=(0.7, 1), halign="left"
        ))
        top.add_widget(Label(
            text=ch["sport"],
            font_size=13, color=ACCENT2,
            size_hint=(0.3, 1), halign="right"
        ))
        card.add_widget(top)

        desc = ch.get("description", "")
        if desc:
            card.add_widget(make_label(desc, font_size=13,
                                       color=TEXT_SECONDARY, height=22))

        bottom = Label(
            text=f"Mērķis: {ch.get('target', '')} {ch.get('unit', '')}  |  Termiņš: {ch.get('deadline', 'Nav')}",
            font_size=12, color=TEXT_SECONDARY,
            size_hint=(1, None), height=22, halign="left"
        )
        bottom.bind(size=lambda w, v: setattr(w, "text_size", (v[0], None)))
        card.add_widget(bottom)

        return card

    def open_create_popup(self, _):
        content = BoxLayout(orientation="vertical", spacing=10, padding=20)

        title_inp = make_input("Nosaukums, piem. 'Skrien 5km'")
        sport_spinner = Spinner(
            text="Izvēlies sportu",
            values=SPORTS,
            size_hint=(1, None), height=44,
            background_normal="",
            background_color=(0.18, 0.18, 0.3, 1),
            color=(1,1,1,1)
        )
        desc_inp = make_input("Apraksts (neobligāts)")
        target_inp = make_input("Mērķa vērtība, piem. 5")
        unit_inp = make_input("Vienība, piem. km, min, reizes")
        deadline_inp = make_input("Termiņš, piem. 31.12.2025")

        for label, widget in [
            ("Nosaukums:", title_inp),
            ("Sports:", sport_spinner),
            ("Apraksts:", desc_inp),
            ("Mērķis:", target_inp),
            ("Vienība:", unit_inp),
            ("Termiņš:", deadline_inp),
        ]:
            content.add_widget(make_label(label, color=TEXT_SECONDARY, height=22))
            content.add_widget(widget)

        popup = Popup(
            title="Jauns izaicinājums",
            content=content,
            size_hint=(0.92, None), height=620,
            background="", background_color=BG_COLOR,
            title_color=ACCENT, title_size=18
        )

        btn_row = BoxLayout(size_hint=(1, None), height=48, spacing=10)
        cancel_btn = make_button("Atcelt", bg=DANGER, height=48)
        save_btn   = make_button("Saglabāt ✓", bg=ACCENT2,
                                  text_color=(0,0,0,1), height=48)
        cancel_btn.bind(on_press=popup.dismiss)

        def save(_):
            if not title_inp.text.strip():
                show_popup("Kļūda", "Ievadiet nosaukumu!")
                return
            if sport_spinner.text == "Izvēlies sportu":
                show_popup("Kļūda", "Izvēlieties sportu!")
                return

            app = App.get_running_app()
            data = load_user_data(app.current_user)
            data["izaicinajumi"].append({
                "title":       title_inp.text.strip(),
                "sport":       sport_spinner.text,
                "description": desc_inp.text.strip(),
                "target":      target_inp.text.strip(),
                "unit":        unit_inp.text.strip(),
                "deadline":    deadline_inp.text.strip(),
                "datums":      datetime.now().strftime("%d.%m.%Y")
            })
            add_achievement(data, "Izaicinājums izveidots!",
                            f"Izveidots: {title_inp.text.strip()}", 20)
            save_user_data(app.current_user, data)
            popup.dismiss()
            self.refresh_challenges()
            show_popup("Veiksmīgi!", "Izaicinājums izveidots! +20 punkti 🏆")

        save_btn.bind(on_press=save)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(save_btn)
        content.add_widget(btn_row)

        popup.open()


# ═══════════════════════════════════════════════════════════
#  4. REZULTĀTI — экран результатов
# ═══════════════════════════════════════════════════════════

class ResultsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        set_bg(root, BG_COLOR)

        header = BoxLayout(size_hint=(1, None), height=65, padding=[20, 10])
        set_bg(header, (0.05, 0.05, 0.12, 1))
        header.add_widget(Label(
            text="[b] Rezultātu ievade[/b]",
            markup=True, font_size=20, color=ACCENT
        ))
        root.add_widget(header)

        scroll, self.list_box = make_scrollable_box(spacing=10, padding=[15, 15])

        # Кнопки
        btn_row = BoxLayout(size_hint=(1, None), height=52, spacing=10)
        add_btn  = make_button("+ Ievadīt rezultātu", bg=ACCENT, height=52)
        sync_btn = make_button("⟳ Sinhronizēt", bg=CARD_COLOR, height=52)
        add_btn.bind(on_press=self.open_add_popup)
        sync_btn.bind(on_press=self.sync)
        btn_row.add_widget(add_btn)
        btn_row.add_widget(sync_btn)
        self.list_box.add_widget(btn_row)

        self.list_box.add_widget(make_label("Rezultātu vēsture:", bold=True,
                                            color=TEXT_SECONDARY, height=28))
        self.results_container = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=8
        )
        self.results_container.bind(minimum_height=self.results_container.setter("height"))
        self.list_box.add_widget(self.results_container)

        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        self.refresh_results()

    def refresh_results(self):
        self.results_container.clear_widgets()
        app = App.get_running_app()
        if not app.current_user:
            return
        data = load_user_data(app.current_user)
        if not data or not data.get("rezultati"):
            self.results_container.add_widget(
                make_label("Nav rezultātu. Pievienojiet pirmo!",
                           color=TEXT_SECONDARY, height=40, halign="center")
            )
            return

        for r in reversed(data["rezultati"]):
            card = self._make_result_card(r)
            self.results_container.add_widget(card)

    def _make_result_card(self, r):
        card = BoxLayout(orientation="horizontal", size_hint=(1, None),
                         height=72, padding=[15, 8], spacing=10)
        set_bg(card, CARD_COLOR)

        left = BoxLayout(orientation="vertical", size_hint=(0.75, 1))
        left.add_widget(Label(
            text=f"[b]{r['sport']}[/b]",
            markup=True, font_size=15, color=TEXT_PRIMARY,
            size_hint=(1, None), height=24, halign="left"
        ))
        note = r.get("note", "")
        left.add_widget(Label(
            text=note if note else r.get("datums", ""),
            font_size=12, color=TEXT_SECONDARY,
            size_hint=(1, None), height=20, halign="left"
        ))
        card.add_widget(left)

        right = Label(
            text=f"[b]{r['value']} {r.get('unit','')}[/b]",
            markup=True, font_size=18, color=ACCENT2,
            size_hint=(0.25, 1), halign="right"
        )
        card.add_widget(right)
        return card

    def open_add_popup(self, _):
        content = BoxLayout(orientation="vertical", spacing=10, padding=20)

        sport_spinner = Spinner(
            text="Izvēlies sportu", values=SPORTS,
            size_hint=(1, None), height=44,
            background_normal="", background_color=(0.18, 0.18, 0.3, 1),
            color=(1,1,1,1)
        )
        value_inp = make_input("Rezultāts, piem. 5.2")
        unit_inp  = make_input("Vienība, piem. km, min, gab")
        note_inp  = make_input("Piezīme (neobligāti)")

        for label, widget in [
            ("Sports:",    sport_spinner),
            ("Rezultāts:", value_inp),
            ("Vienība:",   unit_inp),
            ("Piezīme:",   note_inp),
        ]:
            content.add_widget(make_label(label, color=TEXT_SECONDARY, height=22))
            content.add_widget(widget)

        popup = Popup(
            title="Pievienot rezultātu",
            content=content,
            size_hint=(0.9, None), height=440,
            background="", background_color=BG_COLOR,
            title_color=ACCENT, title_size=18
        )

        btn_row = BoxLayout(size_hint=(1, None), height=48, spacing=10)
        cancel_btn = make_button("Atcelt", bg=DANGER, height=48)
        save_btn   = make_button("Saglabāt ✓", bg=ACCENT2,
                                  text_color=(0,0,0,1), height=48)
        cancel_btn.bind(on_press=popup.dismiss)

        def save(_):
            if sport_spinner.text == "Izvēlies sportu":
                show_popup("Kļūda", "Izvēlieties sportu!")
                return
            if not value_inp.text.strip():
                show_popup("Kļūda", "Ievadiet rezultātu!")
                return
            try:
                float(value_inp.text.strip())
            except ValueError:
                show_popup("Kļūda", "Rezultātam jābūt skaitlim!")
                return

            app = App.get_running_app()
            data = load_user_data(app.current_user)
            data["rezultati"].append({
                "sport":  sport_spinner.text,
                "value":  value_inp.text.strip(),
                "unit":   unit_inp.text.strip(),
                "note":   note_inp.text.strip(),
                "datums": datetime.now().strftime("%d.%m.%Y %H:%M")
            })
            add_achievement(data, "Rezultāts reģistrēts!",
                            f"{sport_spinner.text}: {value_inp.text} {unit_inp.text}", 10)
            save_user_data(app.current_user, data)
            popup.dismiss()
            self.refresh_results()
            show_popup("Veiksmīgi!", "Rezultāts saglabāts! +10 punkti")

        save_btn.bind(on_press=save)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(save_btn)
        content.add_widget(btn_row)
        popup.open()

    def sync(self, _):
        show_popup("Sinhronizācija", "Sinhronizācija ar ierīci\nNav pieejama šajā versijā.")


# ═══════════════════════════════════════════════════════════
#  5. PUNKTI UN SASNIEGUMI — очки и достижения
# ═══════════════════════════════════════════════════════════

class PointsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        set_bg(root, BG_COLOR)

        header = BoxLayout(size_hint=(1, None), height=65, padding=[20, 10])
        set_bg(header, (0.05, 0.05, 0.12, 1))
        header.add_widget(Label(
            text="[b] Punkti un sasniegumi[/b]",
            markup=True, font_size=20, color=ACCENT
        ))
        root.add_widget(header)

        scroll, self.box = make_scrollable_box(spacing=10, padding=[15, 15])

        # Блок с общим количеством очков
        self.points_card = BoxLayout(size_hint=(1, None), height=110,
                                     padding=[20, 15], spacing=5,
                                     orientation="vertical")
        set_bg(self.points_card, (0.1, 0.18, 0.35, 1))
        self.points_label = Label(
            text="0",
            font_size=48, bold=True, color=ACCENT,
            size_hint=(1, None), height=55
        )
        self.points_card.add_widget(self.points_label)
        self.points_card.add_widget(
            make_label("kopā punkti", font_size=14, color=TEXT_SECONDARY,
                       height=22, halign="center")
        )
        self.box.add_widget(self.points_card)

        # Уровень
        self.level_label = make_label("", font_size=15, color=ACCENT2,
                                      height=30, halign="center")
        self.box.add_widget(self.level_label)

        self.box.add_widget(make_label("Sasniegumu vēsture:", bold=True,
                                       color=TEXT_SECONDARY, height=28))

        self.ach_container = BoxLayout(orientation="vertical",
                                       size_hint_y=None, spacing=6)
        self.ach_container.bind(minimum_height=self.ach_container.setter("height"))
        self.box.add_widget(self.ach_container)

        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        self.refresh()

    def refresh(self):
        self.ach_container.clear_widgets()
        app = App.get_running_app()
        if not app.current_user:
            return
        data = load_user_data(app.current_user)
        if not data:
            return

        total = data.get("punkti", 0)
        self.points_label.text = str(total)

        # Уровень
        level = "Iesācējs " if total < 100 else \
                "Sportists " if total < 300 else \
                "Meistars " if total < 600 else "Čempions "
        self.level_label.text = f"Līmenis: {level}"

        achievements = data.get("sasniegumi", [])
        if not achievements:
            self.ach_container.add_widget(
                make_label("Nav sasniegumu vēl.", color=TEXT_SECONDARY,
                           height=40, halign="center")
            )
            return

        for ach in reversed(achievements):
            card = BoxLayout(orientation="horizontal", size_hint=(1, None),
                             height=70, padding=[15, 8], spacing=12)
            set_bg(card, CARD_COLOR)

            icon_label = Label(text="P", font_size=28,
                               size_hint=(None, 1), width=40)
            card.add_widget(icon_label)

            info = BoxLayout(orientation="vertical", size_hint=(0.7, 1))
            info.add_widget(Label(
                text=f"[b]{ach['title']}[/b]",
                markup=True, font_size=14, color=TEXT_PRIMARY,
                size_hint=(1, None), height=24, halign="left"
            ))
            info.add_widget(Label(
                text=ach.get("description", ""),
                font_size=11, color=TEXT_SECONDARY,
                size_hint=(1, None), height=18, halign="left"
            ))
            card.add_widget(info)

            pts = Label(
                text=f"[b]+{ach['punkti']}[/b]",
                markup=True, font_size=16, color=ACCENT2,
                size_hint=(0.22, 1), halign="right"
            )
            card.add_widget(pts)
            self.ach_container.add_widget(card)


# ═══════════════════════════════════════════════════════════
#  6. PROFILS UN STATISTIKA — профиль и статистика
# ═══════════════════════════════════════════════════════════

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        set_bg(root, BG_COLOR)

        header = BoxLayout(size_hint=(1, None), height=65, padding=[20, 10])
        set_bg(header, (0.05, 0.05, 0.12, 1))
        header.add_widget(Label(
            text="[b] Profils un statistika[/b]",
            markup=True, font_size=20, color=ACCENT
        ))
        root.add_widget(header)

        scroll, self.box = make_scrollable_box(spacing=12, padding=[15, 15])

        # Аватар + имя
        avatar_card = BoxLayout(orientation="vertical", size_hint=(1, None),
                                height=130, padding=15)
        set_bg(avatar_card, (0.1, 0.1, 0.2, 1))

        self.avatar_label = Label(text="P", font_size=44,
                                  size_hint=(1, None), height=55)
        avatar_card.add_widget(self.avatar_label)

        self.username_label = Label(
            text="—", font_size=18, bold=True, color=TEXT_PRIMARY,
            size_hint=(1, None), height=30
        )
        avatar_card.add_widget(self.username_label)
        self.box.add_widget(avatar_card)

        # Статистика
        self.box.add_widget(make_label("Statistika:", bold=True,
                                       color=TEXT_SECONDARY, height=28))
        self.stats_grid = GridLayout(cols=2, size_hint=(1, None),
                                     height=160, spacing=8)
        self.box.add_widget(self.stats_grid)

        # История
        self.box.add_widget(make_label("Pēdējie rezultāti:", bold=True,
                                       color=TEXT_SECONDARY, height=28))
        self.history_container = BoxLayout(orientation="vertical",
                                           size_hint_y=None, spacing=6)
        self.history_container.bind(minimum_height=self.history_container.setter("height"))
        self.box.add_widget(self.history_container)

        # Выход
        logout_btn = make_button("Iziet no konta", bg=DANGER, height=48)
        logout_btn.bind(on_press=self.logout)
        self.box.add_widget(logout_btn)

        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        if not app.current_user:
            return
        data = load_user_data(app.current_user)
        if not data:
            return

        self.username_label.text = data.get("username", "—")

        # Статистика — карточки
        self.stats_grid.clear_widgets()
        stats = [
            ("🏆", "Izaicinājumi", str(len(data.get("izaicinajumi", [])))),
            ("R", "Rezultāti",    str(len(data.get("rezultati", [])))),
            ("P", "Punkti",       str(data.get("punkti", 0))),
            ("🎖️", "Sasniegumi",   str(len(data.get("sasniegumi", [])))),
        ]
        for icon, label, value in stats:
            card = BoxLayout(orientation="vertical", size_hint=(1, None),
                             height=72, padding=[10, 8])
            set_bg(card, CARD_COLOR)
            card.add_widget(Label(
                text=f"[b]{value}[/b]",
                markup=True, font_size=22, color=ACCENT,
                size_hint=(1, None), height=30
            ))
            card.add_widget(Label(
                text=f"{icon} {label}",
                font_size=12, color=TEXT_SECONDARY,
                size_hint=(1, None), height=20
            ))
            self.stats_grid.add_widget(card)

        # История (последние 5)
        self.history_container.clear_widgets()
        results = data.get("rezultati", [])
        if not results:
            self.history_container.add_widget(
                make_label("Nav rezultātu.", color=TEXT_SECONDARY,
                           height=30, halign="center")
            )
        else:
            for r in reversed(results[-5:]):
                row = BoxLayout(size_hint=(1, None), height=40, padding=[12, 5])
                set_bg(row, CARD_COLOR)
                row.add_widget(Label(
                    text=r["sport"], font_size=14, color=TEXT_PRIMARY,
                    size_hint=(0.5, 1), halign="left"
                ))
                row.add_widget(Label(
                    text=f"{r['value']} {r.get('unit','')}",
                    font_size=14, color=ACCENT2,
                    size_hint=(0.3, 1), halign="right"
                ))
                row.add_widget(Label(
                    text=r.get("datums", "")[:10],
                    font_size=11, color=TEXT_SECONDARY,
                    size_hint=(0.2, 1), halign="right"
                ))
                self.history_container.add_widget(row)

    def logout(self, _):
        App.get_running_app().current_user = None
        self.manager.current = "login"


# ═══════════════════════════════════════════════════════════
#  GALVENĀ APLIKĀCIJA
# ═══════════════════════════════════════════════════════════

class SportaAplikacija(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None

    def build(self):
        self.title = "Sporta Aplikācija"
        ensure_dir()

        # ScreenManager
        sm = ScreenManager()
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(ChallengesScreen(name="challenges"))
        sm.add_widget(ResultsScreen(name="results"))
        sm.add_widget(PointsScreen(name="points"))
        sm.add_widget(ProfileScreen(name="profile"))
        sm.current = "register"

        # Навигационная панель
        self.navbar = NavBar(sm)

        root = BoxLayout(orientation="vertical")
        set_bg(root, BG_COLOR)
        root.add_widget(sm)
        root.add_widget(self.navbar)

        return root


if __name__ == "__main__":
    SportaAplikacija().run()