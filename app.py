import html
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from supabase import create_client

# =====================================================
# 1. БЕТ БАПТАУЛАРЫ
# =====================================================
st.set_page_config(
    page_title="FIZIKA QADAM",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. SUPABASE БАЙЛАНЫСЫ
# =====================================================
if "supabase_client" not in st.session_state:
    try:
        supabase_url = st.secrets["supabase"]["url"]
        supabase_key = st.secrets["supabase"]["publishable_key"]

        st.session_state.supabase_client = create_client(
            supabase_url, supabase_key
        )

    except Exception as e:
        st.error(
            "Supabase байланысы орнамады. "
            "Streamlit Secrets баптауын тексеріңіз."
        )
        st.caption(f"Қате түрі: {type(e).__name__}")
        st.stop()

supabase = st.session_state.supabase_client

if "user" not in st.session_state:
    st.session_state.user = None

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Басты бет"

if "qadam_chat_open" not in st.session_state:
    st.session_state.qadam_chat_open = False

if "qadam_messages" not in st.session_state:
    st.session_state.qadam_messages = [
        {
            "role": "assistant",
            "content": (
                "Сәлем! Мен QADAM AI көмекшісімін. "
                "Физикадан сұрағыңды жаз — тақырыпты "
                "түсіндіремін немесе есепті қадамдап шығарамын."
            )
        }
    ]

# =====================================================
# 3. PREMIUM WHITE ДИЗАЙНЫ
# =====================================================
st.markdown("""
<style>
.stApp {
    background: #F5F8FC;
    color: #172B4D;
}

h1, h2, h3, h4, p, label {
    color: #172B4D;
}

.hero-title {
    font-size: 36px;
    font-weight: 800;
    color: #142B4A;
    letter-spacing: -1px;
}

.hero-subtitle {
    color: #718096;
    font-size: 15px;
}

[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E8EDF4;
}

[data-testid="stSidebar"] > div {
    padding-top: 25px;
}

[data-testid="stSidebar"] .stRadio label {
    padding: 9px 10px;
    border-radius: 10px;
    color: #43536B;
    font-weight: 600;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background: #EDF5FF;
}

.stButton > button,
.stFormSubmitButton > button {
    background: #1769AA;
    color: white;
    border: none;
    border-radius: 10px;
    min-height: 42px;
    font-weight: 600;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #10558E;
    color: white;
}

.stTextInput input,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 9px;
}

.info-card {
    background: white;
    border: 1px solid #E8EDF4;
    border-radius: 15px;
    padding: 20px;
    min-height: 125px;
    box-shadow: 0 3px 12px rgba(25,55,90,.04);
}

.info-card h3 {
    font-size: 17px;
    margin-bottom: 8px;
    color: #172B4D;
}

.info-card p {
    font-size: 13px;
    color: #718096;
    margin-bottom: 0;
}

.main-banner {
    background: linear-gradient(110deg,#FFFFFF,#EAF4FF);
    border: 1px solid #DFEAF7;
    border-radius: 20px;
    padding: 28px;
    margin-bottom: 20px;
}

.banner-label {
    color: #1769AA;
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 1px;
}

.banner-title {
    color: #142B4A;
    font-size: clamp(24px,3vw,34px);
    font-weight: 800;
    margin-top: 9px;
}

.banner-text {
    color: #64748B;
    font-size: 15px;
    margin-top: 7px;
}

div[data-testid="stExpander"] {
    background: white;
    border: 1px solid #E5EBF2;
    border-radius: 12px;
    margin-bottom: 8px;
}

hr {
    border-color: #E6ECF3;
}

.footer {
    color: #94A3B8;
    text-align: center;
    font-size: 12px;
    padding: 20px;
}

.physics-heading {
    color: #1769AA;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1.5px;
}

/* Қалқымалы QADAM AI терезесі */
.st-key-qadam_chat_open {
    position: fixed !important;
    right: 18px !important;
    bottom: 18px !important;
    z-index: 999999 !important;
    width: min(390px, calc(100vw - 28px)) !important;
    background: #FFFFFF !important;
    border: 1px solid #DCE7F2 !important;
    border-radius: 18px !important;
    padding: 12px !important;
    box-shadow: 0 12px 40px rgba(20,43,74,.22) !important;
}

.st-key-qadam_chat_closed {
    position: fixed !important;
    right: 20px !important;
    bottom: 20px !important;
    z-index: 999999 !important;
    width: 76px !important;
    background: transparent !important;
    padding: 0 !important;
}

.st-key-qadam_chat_closed .stButton > button {
    width: 66px !important;
    height: 66px !important;
    min-height: 66px !important;
    border-radius: 50% !important;
    font-size: 25px !important;
    box-shadow: 0 8px 25px rgba(23,105,170,.35) !important;
}

@media (max-width: 600px) {
    .st-key-qadam_chat_open {
        right: 8px !important;
        bottom: 8px !important;
        width: calc(100vw - 16px) !important;
    }
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 4. ҚОСАЛҚЫ ФУНКЦИЯЛАР
# =====================================================
def show_footer():
    st.markdown("""
    <div class="footer">
        ⚛️ FIZIKA QADAM © 2026<br>
        Физиканы түсін. Есепті шеш. Нәтижеге жет!
    </div>
    """, unsafe_allow_html=True)


def show_header():
    st.markdown("""
    <div style="margin-bottom:20px;">
        <div class="hero-title">⚛️ FIZIKA QADAM</div>
        <div class="hero-subtitle">
            Физикалық есептерді шешудің адаптивті цифрлық платформасы
        </div>
    </div>
    """, unsafe_allow_html=True)


def go_to(section):
    st.session_state.selected_page = section
    st.rerun()


def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.user = None
    st.session_state.selected_page = "Басты бет"
    st.session_state.qadam_chat_open = False
    st.session_state.qadam_messages = []

    for key in ["course_grade", "course_track"]:
        st.session_state.pop(key, None)

    st.rerun()
    # =====================================================
# 5. 3D ФИЗИКАЛЫҚ МОДЕЛЬДЕР
# =====================================================

def show_atom_model():
    """Атомның қарапайым 3D моделі."""

    fig = go.Figure()

    # Ядро
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode="markers",
        marker=dict(size=18, color="red"),
        name="Ядро"
    ))

    # Электрон орбиталары
    t = np.linspace(0, 2 * np.pi, 150)

    orbit_data = [
        (3, 0, 0),
        (0, 3, 0),
        (0, 0, 3)
    ]

    for axis in range(3):
        if axis == 0:
            x = 3 * np.cos(t)
            y = 3 * np.sin(t)
            z = np.zeros_like(t)
        elif axis == 1:
            x = 3 * np.cos(t)
            y = np.zeros_like(t)
            z = 3 * np.sin(t)
        else:
            x = np.zeros_like(t)
            y = 3 * np.cos(t)
            z = 3 * np.sin(t)

        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode="lines",
            line=dict(color="#1769AA", width=4),
            showlegend=False
        ))

    # Электрондар
    fig.add_trace(go.Scatter3d(
        x=[3, -3, 0],
        y=[0, 0, 3],
        z=[0, 0, 0],
        mode="markers",
        marker=dict(size=8, color="#00A6FB"),
        name="Электрон"
    ))

    fig.update_layout(
        title="Атом құрылысының моделі",
        height=420,
        margin=dict(l=0, r=0, t=45, b=0),
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            aspectmode="cube"
        )
    )

    st.plotly_chart(fig, use_container_width=True)


def show_magnetic_model():
    """Магнит өрісінің күш сызықтары."""

    fig = go.Figure()

    theta = np.linspace(0, 2 * np.pi, 200)

    for radius in [1, 1.5, 2, 2.5, 3]:
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        z = 0.25 * np.sin(2 * theta)

        fig.add_trace(go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode="lines",
            line=dict(color="#1769AA", width=4),
            showlegend=False
        ))

    fig.add_trace(go.Scatter3d(
        x=[0, 0],
        y=[0, 0],
        z=[0.5, -0.5],
        mode="markers+text",
        marker=dict(size=12, color=["red", "blue"]),
        text=["N", "S"],
        textposition="top center",
        name="Магнит полюстері"
    ))

    fig.update_layout(
        title="Магнит өрісінің моделі",
        height=420,
        margin=dict(l=0, r=0, t=45, b=0),
        scene=dict(aspectmode="cube")
    )

    st.plotly_chart(fig, use_container_width=True)


def show_pendulum_model():
    """Математикалық маятник моделі."""

    angle = st.slider(
        "Маятниктің ауытқу бұрышы",
        min_value=-55,
        max_value=55,
        value=25,
        key="pendulum_angle"
    )

    length = 3
    radians = np.radians(angle)

    x = length * np.sin(radians)
    y = -length * np.cos(radians)

    fig = go.Figure()

    # Тірек
    fig.add_trace(go.Scatter(
        x=[-1, 1],
        y=[0, 0],
        mode="lines",
        line=dict(color="#64748B", width=8),
        showlegend=False
    ))

    # Жіп
    fig.add_trace(go.Scatter(
        x=[0, x],
        y=[0, y],
        mode="lines",
        line=dict(color="#1769AA", width=5),
        showlegend=False
    ))

    # Жүк
    fig.add_trace(go.Scatter(
        x=[x],
        y=[y],
        mode="markers",
        marker=dict(size=25, color="#F59E0B"),
        name="Маятник жүгі"
    ))

    fig.update_layout(
        title="Математикалық маятник",
        height=380,
        xaxis=dict(range=[-4, 4], zeroline=False),
        yaxis=dict(range=[-4, 1], scaleanchor="x"),
        margin=dict(l=10, r=10, t=45, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)
    st.info(f"Маятниктің ауытқу бұрышы: {angle}°")


def show_prism_model():
    """Жарықтың призмада жіктелуі."""

    fig = go.Figure()

    colors = [
        ("Қызыл", "red"),
        ("Қызғылт сары", "orange"),
        ("Сары", "gold"),
        ("Жасыл", "green"),
        ("Көк", "blue"),
        ("Көгілдір", "cyan"),
        ("Күлгін", "purple")
    ]

    # Ақ жарық
    fig.add_trace(go.Scatter(
        x=[-3, 0],
        y=[0, 0],
        mode="lines",
        line=dict(color="gray", width=7),
        name="Ақ жарық"
    ))

    # Призма
    fig.add_trace(go.Scatter(
        x=[0, 1, 0.5, 0],
        y=[1, 1, -1, 1],
        fill="toself",
        fillcolor="rgba(80,160,255,0.25)",
        line=dict(color="#1769AA", width=3),
        name="Призма"
    ))

    # Спектр
    for i, (name, color) in enumerate(colors):
        y = 0.7 - i * 0.22

        fig.add_trace(go.Scatter(
            x=[0.8, 3],
            y=[0.5, y],
            mode="lines",
            line=dict(color=color, width=5),
            name=name
        ))

    fig.update_layout(
        title="Жарықтың дисперсиясы",
        height=400,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=10, r=10, t=45, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)


def show_physics_world():
    st.markdown("### 🌌 Виртуалды физика әлемі")
    st.write(
        "Физикалық құбылыстарды интерактивті модельдер арқылы зертте."
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "⚛️ Атом",
        "🧲 Магнит өрісі",
        "⏱️ Маятник",
        "🌈 Жарық"
    ])

    with tab1:
        show_atom_model()

    with tab2:
        show_magnetic_model()

    with tab3:
        show_pendulum_model()

    with tab4:
        show_prism_model()


# =====================================================
# 6. QADAM AI — GEMINI ЖАСАНДЫ ИНТЕЛЛЕКТІ
# =====================================================

def ask_qadam_ai(messages, mode, grade):
    """
    Gemini арқылы физика сұрақтарына жауап алу.
    API кілті Streamlit Secrets ішінде сақталуы керек.
    """

    try:
        from google import genai

        api_key = st.secrets["gemini"]["api_key"]

        client = genai.Client(api_key=api_key)

        system_instruction = f"""
Сен QADAM AI атты қазақ тілінде сөйлейтін физика пәнінің көмекшісісің.

Сынып: {grade}
Жұмыс режимі: {mode}

Міндеттерің:
1. Оқушыға физиканы түсінікті тілмен түсіндіру.
2. Есептерді кезең-кезеңімен шығару.
3. Формулалардың мағынасын түсіндіру.
4. Өлшем бірліктерін SI жүйесінде көрсету.
5. Қажет болса, күнделікті өмірден мысал келтіру.
6. Оқушының жас ерекшелігіне сай жауап беру.
7. Қауіпсіздік талаптарын сақтау.

Есеп шығарғанда:
- Берілгені;
- ХБЖ;
- Формула;
- Шешуі;
- Жауабы.

Негізгі тіл: қазақ тілі.
"""

        history = []

        for message in messages[-12:]:
            role = (
                "user"
                if message["role"] == "user"
                else "model"
            )

            history.append({
                "role": role,
                "parts": [{"text": message["content"]}]
            })

        if not history or history[-1]["role"] != "user":
            return "Сұрақ табылмады.", True

        chat = client.chats.create(
            model="gemini-2.5-flash",
            config={
                "system_instruction": system_instruction
            },
            history=history[:-1]
        )

        response = chat.send_message(
            history[-1]["parts"][0]["text"]
        )

        answer = response.text

        if not answer:
            return "AI жауап қайтара алмады. Қайталап көр.", True

        return answer, False

    except Exception as e:
        error_type = type(e).__name__
        error_text = str(e)

        if "api_key" in error_text.lower():
            error_text = "API кілтіне қатысты қате."

        return (
            f"QADAM AI қатесі: {error_type}\n\n"
            f"{error_text[:500]}",
            True
        )
        # =====================================================
# 7. БАСТЫ БЕТ
# =====================================================

def show_dashboard():

    show_header()

    st.markdown("""
    <div class="main-banner">
        <div class="banner-label">ҚОШ КЕЛДІҢ!</div>
        <div class="banner-title">Физиканы жаңа қырынан таны!</div>
        <div class="banner-text">
            Теорияны меңгер, тәжірибе жаса, есептерді шеш
            және өз біліміңді дамыт.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🚀 Оқу платформасы")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>📚 Физика курсы</h3>
            <p>7–11 сыныптарға арналған теориялық материалдар мен сабақтар.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Курсты ашу", key="dashboard_course",
                     use_container_width=True):
            go_to("Физика курсы")

    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>📝 Тапсырмалар</h3>
            <p>Физикалық есептерді орындап, біліміңді тексер.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Тапсырмаларды ашу", key="dashboard_tasks",
                     use_container_width=True):
            go_to("Тапсырмалар")

    with col3:
        st.markdown("""
        <div class="info-card">
            <h3>🌌 Виртуалды зертхана</h3>
            <p>Физикалық құбылыстарды интерактивті модельдермен зертте.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Зертхананы ашу", key="dashboard_lab",
                     use_container_width=True):
            go_to("Виртуалды зертхана")

    st.divider()

    show_physics_world()

    st.divider()

    st.markdown("### 🤖 QADAM AI")
    st.write(
        "Физика тақырыбын түсінбедің бе? "
        "Экранның төменгі оң жағындағы робот белгісін басып, "
        "QADAM AI көмекшісіне сұрақ қой."
    )


# =====================================================
# 8. ФИЗИКА КУРСЫ
# =====================================================

def show_physics_course():

    show_header()
    st.markdown("## 📚 Физика курсы")

    grade = st.selectbox(
        "Сыныпты таңда",
        ["7-сынып", "8-сынып", "9-сынып",
         "10-сынып", "11-сынып"],
        key="course_grade"
    )

    track = st.selectbox(
        "Оқу бағытын таңда",
        ["Барлық бөлімдер", "Механика", "Молекулалық физика",
         "Электр және магнетизм", "Оптика"],
        key="course_track"
    )

    grade_number = int(grade.split("-")[0])

    try:
        units_response = (
            supabase.table("physics_units")
            .select("*")
            .eq("grade", grade_number)
            .execute()
        )

        units = units_response.data or []

        if not units:
            st.info(
                "Бұл сыныпқа әзірге бөлімдер енгізілмеген."
            )
            return

        for unit in units:

            unit_title = (
                unit.get("title")
                or unit.get("name")
                or "Бөлім атауы"
            )

            if track != "Барлық бөлімдер":
                if track.lower() not in unit_title.lower():
                    continue

            with st.expander(f"📖 {unit_title}"):

                unit_id = unit.get("id")

                lessons_response = (
                    supabase.table("physics_lessons")
                    .select("*")
                    .eq("unit_id", unit_id)
                    .execute()
                )

                lessons = lessons_response.data or []

                if not lessons:
                    st.caption("Бұл бөлімге сабақтар әлі енгізілмеген.")

                for lesson in lessons:

                    lesson_title = (
                        lesson.get("title")
                        or lesson.get("name")
                        or "Сабақ"
                    )

                    st.markdown(f"### {lesson_title}")

                    content = (
                        lesson.get("content")
                        or lesson.get("description")
                        or ""
                    )

                    if content:
                        st.markdown(content)

                    video_url = lesson.get("video_url")

                    if video_url:
                        st.video(video_url)

                    st.divider()

    except Exception as e:
        st.error("Курсты жүктеу кезінде қате пайда болды.")
        st.caption(f"Қате түрі: {type(e).__name__}")


# =====================================================
# 9. ТАПСЫРМАЛАР ЖИНАҒЫ
# =====================================================

def show_tasks_collection():

    show_header()
    st.markdown("## 📝 Физикалық тапсырмалар")

    grade = st.selectbox(
        "Сыныпты таңда",
        [7, 8, 9, 10, 11],
        index=2,
        key="task_grade"
    )

    try:
        response = (
            supabase.table("physics_tasks")
            .select("*")
            .eq("grade", grade)
            .execute()
        )

        tasks = response.data or []

        if not tasks:
            st.info(
                "Бұл сыныпқа тапсырмалар әлі енгізілмеген."
            )
            return

        for index, task in enumerate(tasks):

            title = task.get("title", f"{index + 1}-тапсырма")
            question = task.get("question", "")
            task_id = task.get("id")

            with st.expander(f"📌 {title}"):

                st.write(question)

                options = task.get("options")

                if options and isinstance(options, list):

                    answer = st.radio(
                        "Жауабыңды таңда",
                        options,
                        key=f"task_answer_{task_id}"
                    )

                else:

                    answer = st.text_input(
                        "Жауабың",
                        key=f"task_answer_{task_id}"
                    )

                if st.button(
                    "Жауапты тексеру",
                    key=f"check_task_{task_id}"
                ):

                    try:
                        result = supabase.rpc(
                            "check_physics_task_answer",
                            {
                                "p_task_id": task_id,
                                "p_answer": str(answer)
                            }
                        ).execute()

                        st.success(
                            "Жауап тексеруге жіберілді."
                        )

                        st.write(result.data)

                    except Exception as e:
                        st.error(
                            "Жауапты тексеру кезінде қате пайда болды."
                        )
                        st.caption(type(e).__name__)

    except Exception as e:
        st.error("Тапсырмаларды жүктеу мүмкін болмады.")
        st.caption(f"Қате түрі: {type(e).__name__}")


# =====================================================
# 10. ОҚУШЫ ПРОФИЛІ
# =====================================================

def show_profile():

    show_header()
    st.markdown("## 👤 Менің профилім")

    user = st.session_state.get("user")

    if not user:
        st.warning("Алдымен жүйеге кіріңіз.")
        return

    email = user.get("email", "Email көрсетілмеген")

    st.markdown(f"""
    <div class="info-card">
        <h3>👤 Оқушы аккаунты</h3>
        <p>{html.escape(str(email))}</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.info(
        "Оқу үлгерімі мен жетістіктер туралы ақпарат "
        "профиль модулі толықтырылған кезде көрсетіледі."
    )


# =====================================================
# 11. ВИРТУАЛДЫ ЗЕРТХАНА
# =====================================================

def show_virtual_lab():

    show_header()
    st.markdown("## 🌌 Виртуалды физика зертханасы")

    show_physics_world()


# =====================================================
# 12. ӘЗІРГЕ ДАЙЫН ЕМЕС БӨЛІМДЕР
# =====================================================

def show_placeholder(title, description):

    show_header()

    st.markdown(f"## {title}")
    st.info(description)
    # =====================================================
# 13. QADAM AI — ҚАЛҚЫМАЛЫ ЧАТ
# =====================================================

def show_floating_qadam_chat():

    if st.session_state.qadam_chat_open:

        with st.container(key="qadam_chat_open"):

            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown("### 🤖 QADAM AI")

            with col2:
                if st.button("✖", key="close_qadam_chat"):
                    st.session_state.qadam_chat_open = False
                    st.rerun()

            st.caption("Физика бойынша жеке AI көмекшісі")

            grade = st.selectbox(
                "Сынып",
                ["7-сынып", "8-сынып", "9-сынып",
                 "10-сынып", "11-сынып"],
                index=2,
                key="qadam_grade"
            )

            mode = st.selectbox(
                "Жұмыс режимі",
                [
                    "Тақырыпты түсіндіру",
                    "Есепті шығару",
                    "Формуланы түсіндіру",
                    "Тестке дайындық"
                ],
                key="qadam_mode"
            )

            st.divider()

            for message in st.session_state.qadam_messages:

                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            with st.form("qadam_chat_form", clear_on_submit=True):

                prompt = st.text_area(
                    "Сұрағыңды жаз...",
                    placeholder="Мысалы: Ньютонның бірінші заңы дегеніміз не?",
                    height=80
                )

                submitted = st.form_submit_button(
                    "Жіберу",
                    use_container_width=True
                )

            if submitted:

                if not prompt.strip():
                    st.warning("Алдымен сұрақ енгіз.")

                else:

                    st.session_state.qadam_messages.append({
                        "role": "user",
                        "content": prompt.strip()
                    })

                    with st.spinner("QADAM AI жауап дайындауда..."):

                        answer, error = ask_qadam_ai(
                            st.session_state.qadam_messages,
                            mode,
                            grade
                        )

                    if error:
                        st.error(answer)

                    else:
                        st.session_state.qadam_messages.append({
                            "role": "assistant",
                            "content": answer
                        })

                    st.rerun()

            if st.button(
                "🗑 Чатты тазалау",
                key="clear_qadam_chat",
                use_container_width=True
            ):

                st.session_state.qadam_messages = [
                    {
                        "role": "assistant",
                        "content": (
                            "Сәлем! Мен QADAM AI көмекшісімін. "
                            "Физикадан сұрағыңды жаза бер!"
                        )
                    }
                ]

                st.rerun()

    else:

        with st.container(key="qadam_chat_closed"):

            if st.button("🤖", key="open_qadam_chat"):
                st.session_state.qadam_chat_open = True
                st.rerun()


# =====================================================
# 14. ЖҮЙЕГЕ КІРУ ЖӘНЕ ТІРКЕЛУ
# =====================================================

def show_auth_page():

    st.markdown("""
    <div style="text-align:center; padding:35px 10px 20px;">
        <div style="font-size:48px;">⚛️</div>
        <div class="hero-title">FIZIKA QADAM</div>
        <div class="hero-subtitle">
            Физиканы түсін. Есепті шеш. Нәтижеге жет!
        </div>
    </div>
    """, unsafe_allow_html=True)

    left, center, right = st.columns([1, 1.5, 1])

    with center:

        tab1, tab2 = st.tabs([
            "🔐 Жүйеге кіру",
            "📝 Тіркелу"
        ])

        with tab1:

            st.markdown("### Қош келдің!")

            login_email = st.text_input(
                "Email",
                key="login_email"
            )

            login_password = st.text_input(
                "Құпиясөз",
                type="password",
                key="login_password"
            )

            if st.button(
                "Жүйеге кіру",
                key="login_button",
                use_container_width=True
            ):

                if not login_email.strip() or not login_password:
                    st.warning("Email мен құпиясөзді енгіз.")

                else:

                    try:
                        result = supabase.auth.sign_in_with_password({
                            "email": login_email.strip(),
                            "password": login_password
                        })

                        if result.user:

                            st.session_state.user = {
                                "id": result.user.id,
                                "email": result.user.email
                            }

                            st.session_state.selected_page = "Басты бет"

                            st.success("Жүйеге сәтті кірдің!")
                            st.rerun()

                        else:
                            st.error("Жүйеге кіру мүмкін болмады.")

                    except Exception:
                        st.error(
                            "Кіру кезінде қате пайда болды. "
                            "Email мен құпиясөзді тексер."
                        )

        with tab2:

            st.markdown("### Жаңа аккаунт ашу")

            register_email = st.text_input(
                "Email",
                key="register_email"
            )

            register_password = st.text_input(
                "Құпиясөз",
                type="password",
                key="register_password"
            )

            confirm_password = st.text_input(
                "Құпиясөзді қайтала",
                type="password",
                key="confirm_password"
            )

            if st.button(
                "Тіркелу",
                key="register_button",
                use_container_width=True
            ):

                if not register_email.strip():
                    st.warning("Email енгіз.")

                elif len(register_password) < 8:
                    st.warning(
                        "Құпиясөз кемінде 8 таңбадан тұруы керек."
                    )

                elif register_password != confirm_password:
                    st.warning("Құпиясөздер сәйкес келмейді.")

                else:

                    try:
                        result = supabase.auth.sign_up({
                            "email": register_email.strip(),
                            "password": register_password
                        })

                        if result.user:

                            st.success(
                                "Тіркелу сәтті орындалды. "
                                "Email-ды растау қажет болуы мүмкін."
                            )

                        else:
                            st.error("Тіркелу орындалмады.")

                    except Exception:
                        st.error(
                            "Тіркелу кезінде қате пайда болды. "
                            "Email мекенжайын тексер."
                        )


# =====================================================
# 15. НЕГІЗГІ МӘЗІР
# =====================================================

def show_sidebar():

    with st.sidebar:

        st.markdown("## ⚛️ FIZIKA QADAM")
        st.caption("Білімге бастар қадам")

        st.divider()

        pages = [
            "Басты бет",
            "Физика курсы",
            "Тапсырмалар",
            "Виртуалды зертхана",
            "Олимпиада",
            "Менің профилім"
        ]

        current_page = st.session_state.selected_page

        if current_page not in pages:
            current_page = "Басты бет"

        selected = st.radio(
            "Навигация",
            pages,
            index=pages.index(current_page),
            key="main_navigation"
        )

        if selected != st.session_state.selected_page:
            st.session_state.selected_page = selected
            st.rerun()

        st.divider()

        user = st.session_state.user

        if user:
            st.caption(
                f"👤 {user.get('email', 'Оқушы')}"
            )

        if st.button(
            "🚪 Жүйеден шығу",
            use_container_width=True
        ):
            logout()


# =====================================================
# 16. БЕТТЕРДІ БАСҚАРУ
# =====================================================

def show_selected_page():

    page = st.session_state.selected_page

    if page == "Басты бет":
        show_dashboard()

    elif page == "Физика курсы":
        show_physics_course()

    elif page == "Тапсырмалар":
        show_tasks_collection()

    elif page == "Виртуалды зертхана":
        show_virtual_lab()

    elif page == "Олимпиада":
        show_placeholder(
            "🏆 Олимпиада",
            "Олимпиадалық тапсырмалар бөлімі әзірленуде."
        )

    elif page == "Менің профилім":
        show_profile()

    else:
        show_dashboard()


# =====================================================
# 17. ҚОСЫМШАНЫ ІСКЕ ҚОСУ
# =====================================================

def main():

    if st.session_state.user is None:

        show_auth_page()

    else:

        show_sidebar()

        show_selected_page()

        show_footer()

        show_floating_qadam_chat()


if __name__ == "__main__":
    main()
