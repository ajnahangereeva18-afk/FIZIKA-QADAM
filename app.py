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
# 5. ИНТЕРАКТИВТІ 3D ФИЗИКАЛЫҚ МОДЕЛЬДЕР
# =====================================================

def style_3d_figure(fig, title):
    fig.update_layout(
        title={
            "text": title,
            "x": 0.03,
            "font": {"size": 17, "color": "#17365D"}
        },
        height=390,
        margin=dict(l=0, r=0, t=48, b=0),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor="#F7FBFF",
            aspectmode="cube",
            camera=dict(
                eye=dict(x=1.55, y=1.55, z=1.25)
            )
        ),
        showlegend=False
    )
    return fig


def atom_figure():
    t = np.linspace(0, 2*np.pi, 240)
    fig = go.Figure()

    for plane in range(3):
        if plane == 0:
            x = 1.35*np.cos(t)
            y = 1.35*np.sin(t)
            z = 0*t
        elif plane == 1:
            x = 1.35*np.cos(t)
            y = 0*t
            z = 1.35*np.sin(t)
        else:
            x = 0*t
            y = 1.35*np.cos(t)
            z = 1.35*np.sin(t)

        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode="lines",
            line=dict(color="#55A6E8", width=5)
        ))

    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode="markers",
        marker=dict(
            size=22,
            color="#FF9F43",
            line=dict(color="#D96B27", width=2)
        )
    ))

    fig.add_trace(go.Scatter3d(
        x=[1.35, -0.75, 0],
        y=[0, 0.95, -1.35],
        z=[0.25, 0.75, 0.0],
        mode="markers",
        marker=dict(
            size=9,
            color=["#1769AA", "#7B61FF", "#19A7A0"],
            line=dict(color="white", width=1)
        )
    ))

    return style_3d_figure(fig, "АТОМ ҚҰРЫЛЫСЫ • 3D модель")


def magnetic_figure():
    fig = go.Figure()
    t = np.linspace(0, 2*np.pi, 220)

    for radius in [0.55, 0.85, 1.15, 1.45]:
        x = radius*np.cos(t)
        y = 0.72*radius*np.sin(t)
        z = 0.42*np.sin(2*t) * (1.5-radius/2)

        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode="lines",
            line=dict(color="#287BC1", width=5)
        ))

    fig.add_trace(go.Scatter3d(
        x=[-1.6, 1.6],
        y=[0, 0],
        z=[0, 0],
        mode="markers+text",
        text=["N", "S"],
        textposition="top center",
        marker=dict(size=13, color=["#E65C5C", "#287BC1"])
    ))

    return style_3d_figure(
        fig, "МАГНИТ ӨРІСІ • күш сызықтарының көрінісі"
    )


def pendulum_figure(angle_degrees):
    angle = np.deg2rad(angle_degrees)
    length = 1.8

    bob_x = length*np.sin(angle)
    bob_z = -length*np.cos(angle)

    fig = go.Figure()

    arc = np.linspace(
        -np.deg2rad(55),
        np.deg2rad(55),
        100
    )

    fig.add_trace(go.Scatter3d(
        x=length*np.sin(arc),
        y=0*arc,
        z=-length*np.cos(arc),
        mode="lines",
        line=dict(color="#9AB8D6", width=4, dash="dot")
    ))

    fig.add_trace(go.Scatter3d(
        x=[0, bob_x],
        y=[0, 0],
        z=[0, bob_z],
        mode="lines",
        line=dict(color="#1769AA", width=7)
    ))

    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode="markers",
        marker=dict(size=8, color="#17365D")
    ))

    fig.add_trace(go.Scatter3d(
        x=[bob_x],
        y=[0],
        z=[bob_z],
        mode="markers",
        marker=dict(
            size=19,
            color="#FF9F43",
            line=dict(color="#D96B27", width=2)
        )
    ))

    return style_3d_figure(
        fig,
        f"МАТЕМАТИКАЛЫҚ МАЯТНИК • бұрыш {angle_degrees}°"
    )


def prism_figure():
    fig = go.Figure()

    x = [0, 1.4, 0.7, 0, 1.4, 0.7]
    y = [-0.7, -0.7, 0.7, -0.7, -0.7, 0.7]
    z = [-0.6, -0.6, -0.6, 0.6, 0.6, 0.6]

    fig.add_trace(go.Mesh3d(
        x=x, y=y, z=z,
        i=[0, 0, 0, 3, 3, 1, 1, 2],
        j=[1, 2, 3, 4, 5, 4, 2, 5],
        k=[2, 3, 1, 5, 4, 2, 5, 4],
        color="#77B8E8",
        opacity=0.48,
        flatshading=True
    ))

    fig.add_trace(go.Scatter3d(
        x=[-1.3, 0.05],
        y=[0, 0],
        z=[0, 0],
        mode="lines",
        line=dict(color="#F2B705", width=8)
    ))

    colors = [
        "#E53935", "#FB8C00", "#FDD835",
        "#43A047", "#1E88E5", "#5E35B1"
    ]

    for i, color in enumerate(colors):
        yy = -0.48 + i*0.19

        fig.add_trace(go.Scatter3d(
            x=[1.1, 2.0],
            y=[0.05, yy],
            z=[0.0, 0.12*(i-2.5)],
            mode="lines",
            line=dict(color=color, width=6)
        ))

    return style_3d_figure(
        fig, "ЖАРЫҚТЫҢ ДИСПЕРСИЯСЫ • призма"
    )


def show_physics_world():
    st.markdown(
        '<div class="physics-heading">'
        'ЗЕРТТЕУ АЛАҢЫ • INTERACTIVE 3D'
        '</div>',
        unsafe_allow_html=True
    )

    st.subheader("Физикалық құбылыстар әлемі")
    st.caption(
        "3D модельдерді тышқанмен айналдырып, "
        "жақындатып немесе алыстатып көріңіз."
    )

    atom_tab, magnetic_tab, pendulum_tab, prism_tab = st.tabs([
        "⚛️ Атом",
        "🧲 Магнит өрісі",
        "🕰️ Маятник",
        "🌈 Жарық призмасы"
    ])

    with atom_tab:
        st.plotly_chart(
            atom_figure(),
            use_container_width=True,
            config={"displayModeBar": True}
        )
        st.caption(
            "Бұл — атом құрылымын түсіндіруге арналған шартты модель; "
            "орбиталар нақты траектория емес."
        )

    with magnetic_tab:
        st.plotly_chart(
            magnetic_figure(),
            use_container_width=True,
            config={"displayModeBar": True}
        )
        st.caption(
            "Магнит өрісінің кеңістіктегі көрінісі шартты түрде берілген."
        )

    with pendulum_tab:
        angle = st.slider(
            "Маятниктің ауытқу бұрышы",
            min_value=-55,
            max_value=55,
            value=25,
            step=5,
            key="pendulum_angle"
        )

        st.plotly_chart(
            pendulum_figure(angle),
            use_container_width=True,
            config={"displayModeBar": True}
        )
        st.caption(
            "Бұрышты өзгертіп, маятниктің орнын бақылаңыз."
        )

    with prism_tab:
        st.plotly_chart(
            prism_figure(),
            use_container_width=True,
            config={"displayModeBar": True}
        )
        st.caption(
            "Ақ жарықтың түрлі түстерге жіктелуі — "
            "дисперсия құбылысының көрнекі моделі."
        )
        # ============================================================
# 6. QADAM AI — GEMINI ЖАСАНДЫ ИНТЕЛЛЕКТІ
# ============================================================

QADAM_INSTRUCTIONS = """
Сен — QADAM AI атты физика пәнінің көмекшісісің.

Міндетің:
- Оқушыларға физиканы қарапайым әрі түсінікті тілмен түсіндіру.
- Есептерді кезең-кезеңімен шығару.
- Формулалардың мағынасын түсіндіру.
- Күнделікті өмірден мысалдар келтіру.
- Оқушының сыныбы мен білім деңгейін ескеру.
- Оқушыға дайын жауапты ғана бермей, шешу жолын да көрсету.
- Қазақ тілінде жауап беру.

Жауаптарың нақты, түсінікті және оқушының жас ерекшелігіне сай болсын.
"""


def ask_qadam_ai(messages, mode="Түсіндіру", grade=9):
    """Gemini арқылы QADAM AI жауабын алу."""

    try:
        from google import genai
        from google.genai import types

        if not messages:
            return "Сұрағыңды енгіз."

        api_key = st.secrets["gemini"]["api_key"].strip()

        if not api_key:
            return "Gemini API кілті табылмады."

        client = genai.Client(api_key=api_key)

        system_instruction = f"""
        {QADAM_INSTRUCTIONS}

        Оқушының сыныбы: {grade}-сынып.
        Жұмыс режимі: {mode}.
        """

        chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7
            ),
            history=[
                {
                    "role": (
                        "model"
                        if item["role"] == "assistant"
                        else "user"
                    ),
                    "parts": [{"text": item["content"]}]
                }
                for item in messages[:-1]
            ]
        )

        response = chat.send_message(messages[-1]["content"])

        return response.text or "Жауап алынбады."

    except KeyError:
        return (
            "Gemini API кілті бапталмаған. "
            "Streamlit Secrets бөлімін тексер."
        )

    except Exception as e:
        error_text = str(e).lower()

        if "quota" in error_text or "429" in error_text:
            return "Сұраныс шегі аяқталды. Кейінірек қайталап көр."

        if "permission" in error_text or "403" in error_text:
            return "API рұқсаты жоқ. API баптауын тексер."

        if "api_key" in error_text or "401" in error_text:
            return "API кілті дұрыс емес."

        return f"QADAM AI қатесі: {e}"


# ============================================================
# 8. БАСТЫ ПАНЕЛЬ
# ============================================================

def show_dashboard():

    user = st.session_state.user

    fullname = html.escape(
        user.get("full_name", "Оқушы")
    )

    st.markdown(
        f"""
        <div class="dashboard-banner">
            <div class="banner-content">
                <h1>Қош келдің, {fullname}!</h1>
                <p>
                    FIZIKA QADAM — физиканы түсінудің
                    жаңа қадамы.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## Физика әлеміне қош келдің!")

    show_physics_world()

    st.markdown("---")

    st.markdown("## Сенің оқу кеңістігің")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Оқу бағыты",
            value="Физика",
            delta="7–11 сынып"
        )

    with col2:
        st.metric(
            label="Оқу мүмкіндігі",
            value="Онлайн",
            delta="Кез келген уақытта"
        )

    with col3:
        st.metric(
            label="Көмекші",
            value="QADAM AI",
            delta="Жасанды интеллект"
        )

    st.markdown("### Білім алу бөлімдері")

    card_col1, card_col2, card_col3 = st.columns(3)

    with card_col1:
        st.markdown(
            """
            <div class="feature-card">
                <h3>📚 Физика курсы</h3>
                <p>
                    Теориялық материалдар,
                    формулалар және мысалдар.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Курсқа өту",
            key="dashboard_course",
            use_container_width=True
        ):
            go_to("Физика курсы")

    with card_col2:
        st.markdown(
            """
            <div class="feature-card">
                <h3>📝 Тапсырмалар</h3>
                <p>
                    Біліміңді тапсырмалар арқылы
                    тексер.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Тапсырмаларға өту",
            key="dashboard_tasks",
            use_container_width=True
        ):
            go_to("Тапсырмалар")

    with card_col3:
        st.markdown(
            """
            <div class="feature-card">
                <h3>🤖 QADAM AI</h3>
                <p>
                    Физика сұрақтарына
                    жасанды интеллекттен жауап ал.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "QADAM AI ашу",
            key="dashboard_ai",
            use_container_width=True
        ):
            st.session_state.qadam_chat_open = True
            st.rerun()

    st.markdown("---")

    if user.get("role") == "teacher":
        st.markdown("### Мұғалім панелі")

        st.info(
            "Мұғалім ретінде жүйеге кірдіңіз. "
            "Оқушылардың оқу барысын бақылауға болады."
        )


# ============================================================
# 9. ФИЗИКА КУРСЫ
# ============================================================

def show_physics_course():

    st.title("📚 Физика курсы")
    st.caption(
        "Сыныпты таңдап, физика бөлімдерімен таныс."
    )

    grade = st.selectbox(
        "Сыныпты таңда:",
        [7, 8, 9, 10, 11],
        key="course_grade"
    )

    track = None

    if grade in [10, 11]:
        track = st.selectbox(
            "Оқу бағытын таңда:",
            ["ЖМБ", "ҚГБ"],
            key="course_track"
        )

    try:
        query = (
            supabase.table("physics_courses")
            .select("*")
            .eq("grade", grade)
        )

        if track:
            query = query.eq("track", track)

        courses = query.execute().data

        if not courses:
            st.warning(
                "Бұл сыныпқа арналған курс әзірге табылмады."
            )
            return

        course_options = {
            item["title"]: item["id"]
            for item in courses
        }

        selected_course = st.selectbox(
            "Курс бөлімін таңда:",
            list(course_options.keys())
        )

        course_id = course_options[selected_course]

        units = (
            supabase.table("physics_units")
            .select("*")
            .eq("course_id", course_id)
            .order("order_number")
            .execute()
            .data
        )

        if not units:
            st.info("Бұл курста бөлімдер әзірге жоқ.")
            return

        unit_options = {
            item["title"]: item["id"]
            for item in units
        }

        selected_unit = st.selectbox(
            "Бөлімді таңда:",
            list(unit_options.keys())
        )

        unit_id = unit_options[selected_unit]

        lessons = (
            supabase.table("physics_lessons")
            .select("*")
            .eq("unit_id", unit_id)
            .order("order_number")
            .execute()
            .data
        )

        if not lessons:
            st.info("Бұл бөлімде сабақтар әзірге жоқ.")
            return

        lesson_options = {
            item["title"]: item["id"]
            for item in lessons
        }

        selected_lesson = st.selectbox(
            "Сабақты таңда:",
            list(lesson_options.keys())
        )

        lesson_id = lesson_options[selected_lesson]

        lesson = next(
            (
                item for item in lessons
                if item["id"] == lesson_id
            ),
            None
        )

        if lesson:
            st.markdown("---")
            st.subheader(lesson["title"])

            if lesson.get("theory"):
                st.markdown("### 📖 Теория")
                st.markdown(lesson["theory"])

            if lesson.get("formulas"):
                st.markdown("### 📐 Формулалар")
                st.markdown(lesson["formulas"])

            if lesson.get("examples"):
                st.markdown("### 💡 Мысалдар")
                st.markdown(lesson["examples"])

            if lesson.get("image_url"):
                st.image(
                    lesson["image_url"],
                    use_container_width=True
                )

    except Exception as e:
        st.error(
            f"Курс материалдарын жүктеу кезінде қате пайда болды: {e}"
        )
        # ============================================================
# 10. ТАПСЫРМАЛАР ЖИНАҒЫ
# ============================================================

def show_tasks_collection():

    st.title("📝 Физика тапсырмалары")

    st.caption(
        "Тапсырмаларды орындап, өз біліміңді тексер."
    )

    grade = st.selectbox(
        "Сыныпты таңда:",
        [7, 8, 9, 10, 11],
        key="task_grade"
    )

    track = None

    if grade in [10, 11]:
        track = st.selectbox(
            "Оқу бағытын таңда:",
            ["ЖМБ", "ҚГБ"],
            key="task_track"
        )

    try:
        course_query = (
            supabase.table("physics_courses")
            .select("*")
            .eq("grade", grade)
        )

        if track:
            course_query = course_query.eq("track", track)

        courses = course_query.execute().data

        if not courses:
            st.warning("Курс табылмады.")
            return

        course_options = {
            item["title"]: item["id"]
            for item in courses
        }

        selected_course = st.selectbox(
            "Курс:",
            list(course_options.keys()),
            key="task_course"
        )

        course_id = course_options[selected_course]

        units = (
            supabase.table("physics_units")
            .select("*")
            .eq("course_id", course_id)
            .order("order_number")
            .execute()
            .data
        )

        if not units:
            st.info("Бөлімдер табылмады.")
            return

        unit_options = {
            item["title"]: item["id"]
            for item in units
        }

        selected_unit = st.selectbox(
            "Бөлім:",
            list(unit_options.keys()),
            key="task_unit"
        )

        unit_id = unit_options[selected_unit]

        lessons = (
            supabase.table("physics_lessons")
            .select("*")
            .eq("unit_id", unit_id)
            .order("order_number")
            .execute()
            .data
        )

        if not lessons:
            st.info("Сабақтар табылмады.")
            return

        lesson_options = {
            item["title"]: item["id"]
            for item in lessons
        }

        selected_lesson = st.selectbox(
            "Сабақ:",
            list(lesson_options.keys()),
            key="task_lesson"
        )

        lesson_id = lesson_options[selected_lesson]

        tasks = (
            supabase.table("physics_tasks")
            .select("*")
            .eq("lesson_id", lesson_id)
            .execute()
            .data
        )

        if not tasks:
            st.info("Бұл сабаққа тапсырмалар әлі қосылмаған.")
            return

        st.markdown("---")

        search_text = st.text_input(
            "🔍 Тапсырманы іздеу:",
            key="task_search"
        )

        difficulty = st.selectbox(
            "Қиындық деңгейі:",
            ["Барлығы", "Жеңіл", "Орташа", "Күрделі"],
            key="task_difficulty"
        )

        filtered_tasks = tasks

        if search_text:
            filtered_tasks = [
                task for task in filtered_tasks
                if search_text.lower()
                in task.get("question", "").lower()
            ]

        if difficulty != "Барлығы":
            filtered_tasks = [
                task for task in filtered_tasks
                if task.get("difficulty") == difficulty
            ]

        if not filtered_tasks:
            st.warning("Сәйкес тапсырма табылмады.")
            return

        for index, task in enumerate(filtered_tasks):

            with st.container(border=True):

                st.markdown(
                    f"### Тапсырма {index + 1}"
                )

                st.markdown(
                    task.get("question", "")
                )

                if task.get("image_url"):
                    st.image(
                        task["image_url"],
                        use_container_width=True
                    )

                if task.get("options"):
                    options = task["options"]

                    selected_answer = st.radio(
                        "Жауабыңды таңда:",
                        options,
                        key=f"answer_{task['id']}",
                        index=None
                    )

                else:
                    selected_answer = st.text_input(
                        "Жауабың:",
                        key=f"answer_{task['id']}"
                    )

                if st.button(
                    "Жауапты тексеру",
                    key=f"check_{task['id']}"
                ):

                    if not selected_answer:
                        st.warning(
                            "Алдымен жауабыңды енгіз."
                        )

                    else:
                        try:
                            result = supabase.rpc(
                                "check_physics_task_answer",
                                {
                                    "p_task_id": task["id"],
                                    "p_answer": str(selected_answer)
                                }
                            ).execute()

                            answer_result = result.data

                            st.session_state[
                                f"task_result_{task['id']}"
                            ] = answer_result

                            st.rerun()

                        except Exception as e:
                            st.error(
                                f"Жауапты тексеру қатесі: {e}"
                            )

                saved_result = st.session_state.get(
                    f"task_result_{task['id']}"
                )

                if saved_result is not None:

                    if isinstance(saved_result, dict):
                        is_correct = saved_result.get(
                            "is_correct",
                            False
                        )

                        explanation = saved_result.get(
                            "explanation",
                            ""
                        )

                    else:
                        is_correct = bool(saved_result)
                        explanation = ""

                    if is_correct:
                        st.success("Дұрыс жауап! Жарайсың!")
                    else:
                        st.error(
                            "Жауап дұрыс емес. Қайта ойланып көр."
                        )

                    if explanation:
                        st.info(
                            f"Түсіндірме: {explanation}"
                        )

    except Exception as e:
        st.error(
            f"Тапсырмаларды жүктеу қатесі: {e}"
        )


# ============================================================
# 11. ОҚУШЫ ПРОФИЛІ
# ============================================================

def show_profile():

    st.title("👤 Менің профилім")

    user = st.session_state.user

    st.markdown(
        "### Жеке ақпарат"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Аты-жөні**")
        st.write(
            user.get("full_name", "Көрсетілмеген")
        )

        st.markdown("**Электрондық пошта**")
        st.write(
            user.get("email", "Көрсетілмеген")
        )

    with col2:
        st.markdown("**Рөлі**")
        st.write(
            user.get("role", "student")
        )

        st.markdown("**Сыныбы**")
        st.write(
            user.get("grade", "Көрсетілмеген")
        )

    st.markdown("---")

    if user.get("role") == "teacher":

        st.subheader("Мұғалім аккаунты")

        if not user.get("is_approved", False):
            st.warning(
                "Мұғалім аккаунты әкімші тарапынан "
                "әлі расталмаған."
            )

        else:
            st.success(
                "Мұғалім аккаунты расталған."
            )


# ============================================================
# 12. ӘЗІРЛЕНУ ҮСТІНДЕГІ БӨЛІМДЕР
# ============================================================

def show_placeholder(title, description):

    st.title(title)

    st.info(description)

    st.markdown(
        """
        <div class="feature-card">
            <h3>Жақында қолжетімді болады!</h3>
            <p>
                Бұл бөлім қазіргі уақытта әзірлену үстінде.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 13. QADAM AI ҚАЛҚЫМАЛЫ ЧАТ ТЕРЕЗЕСІ
# ============================================================

def show_floating_qadam_chat():

    if st.session_state.get("qadam_chat_open", False):

        st.markdown(
            """
            <div class="qadam-chat-header">
                <h3>🤖 QADAM AI</h3>
                <p>Сенің физика бойынша көмекшің</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "✕ Жабу",
            key="close_qadam_chat"
        ):
            st.session_state.qadam_chat_open = False
            st.rerun()

        user = st.session_state.user

        grade = user.get("grade", 9)

        try:
            grade = int(grade)
        except (TypeError, ValueError):
            grade = 9

        grade = st.selectbox(
            "Сыныбың:",
            [7, 8, 9, 10, 11],
            index=[7, 8, 9, 10, 11].index(grade)
            if grade in [7, 8, 9, 10, 11]
            else 2,
            key="qadam_grade"
        )

        mode = st.selectbox(
            "Көмек түрін таңда:",
            [
                "Түсіндіру",
                "Есеп шығару",
                "Формуланы түсіндіру",
                "Мысал келтіру"
            ],
            key="qadam_mode"
        )

        if "qadam_messages" not in st.session_state:
            st.session_state.qadam_messages = []

        st.markdown("---")

        for message in st.session_state.qadam_messages:

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input(
            "Физика бойынша сұрағыңды жаз..."
        )

        if prompt:

            st.session_state.qadam_messages.append(
                {
                    "role": "user",
                    "content": prompt
                }
            )

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):

                with st.spinner(
                    "QADAM AI ойланып жатыр..."
                ):

                    answer = ask_qadam_ai(
                        st.session_state.qadam_messages,
                        mode=mode,
                        grade=grade
                    )

                    st.markdown(answer)

            st.session_state.qadam_messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

            st.rerun()

        if st.button(
            "🗑 Чатты тазалау",
            key="clear_qadam_chat"
        ):
            st.session_state.qadam_messages = []
            st.rerun()

    else:

        if st.button(
            "🤖 QADAM AI",
            key="open_qadam_chat"
        ):
            st.session_state.qadam_chat_open = True
            st.rerun()
            # ============================================================
# 14. НЕГІЗГІ БЕТТЕР ЖӘНЕ SIDEBAR
# ============================================================

if st.session_state.user is not None:

    user = st.session_state.user

    # ---------------- SIDEBAR ----------------

    with st.sidebar:

        st.markdown(
            """
            <div class="sidebar-logo">
                <h2>⚛️ FIZIKA QADAM</h2>
                <p>Білімге бастар қадам</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        st.markdown(
            f"**{user.get('full_name', 'Пайдаланушы')}**"
        )

        st.caption(
            user.get("email", "")
        )

        st.markdown("---")

        menu_items = [
            "Басты бет",
            "Физика курсы",
            "Тапсырмалар",
            "Виртуалды зертхана",
            "Олимпиада",
            "QADAM AI",
            "Менің профилім"
        ]

        if "current_page" not in st.session_state:
            st.session_state.current_page = "Басты бет"

        selected_page = st.radio(
            "Мәзір",
            menu_items,
            index=menu_items.index(
                st.session_state.current_page
            )
            if st.session_state.current_page in menu_items
            else 0,
            key="main_navigation"
        )

        st.session_state.current_page = selected_page

        st.markdown("---")

        if st.button(
            "🚪 Жүйеден шығу",
            use_container_width=True
        ):
            logout()

    # ---------------- БЕТТЕРДІ ШАҚЫРУ ----------------

    if selected_page == "Басты бет":

        show_header()
        show_dashboard()

    elif selected_page == "Физика курсы":

        show_header()
        show_physics_course()

    elif selected_page == "Тапсырмалар":

        show_header()
        show_tasks_collection()

    elif selected_page == "Виртуалды зертхана":

        show_header()

        show_placeholder(
            "🔬 Виртуалды зертхана",
            "Физикалық тәжірибелер мен құбылыстарды "
            "виртуалды ортада зерттеу бөлімі."
        )

    elif selected_page == "Олимпиада":

        show_header()

        show_placeholder(
            "🏆 Олимпиада",
            "Физика олимпиадасына дайындық және "
            "арнайы тапсырмалар бөлімі."
        )

    elif selected_page == "QADAM AI":

        show_header()

        st.title("🤖 QADAM AI")

        st.write(
            "Физика бойынша сұрақтарыңды қойып, "
            "жасанды интеллект көмегін пайдалан."
        )

        if "qadam_messages" not in st.session_state:
            st.session_state.qadam_messages = []

        grade = st.selectbox(
            "Сыныбың:",
            [7, 8, 9, 10, 11],
            index=2,
            key="full_ai_grade"
        )

        mode = st.selectbox(
            "Көмек түрі:",
            [
                "Түсіндіру",
                "Есеп шығару",
                "Формуланы түсіндіру",
                "Мысал келтіру"
            ],
            key="full_ai_mode"
        )

        for message in st.session_state.qadam_messages:

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input(
            "Сұрағыңды жаз..."
        )

        if prompt:

            st.session_state.qadam_messages.append(
                {
                    "role": "user",
                    "content": prompt
                }
            )

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):

                with st.spinner("Жауап дайындалуда..."):

                    answer = ask_qadam_ai(
                        st.session_state.qadam_messages,
                        mode=mode,
                        grade=grade
                    )

                    st.markdown(answer)

            st.session_state.qadam_messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

            st.rerun()

        if st.button(
            "🗑 Чатты тазалау",
            key="full_ai_clear"
        ):
            st.session_state.qadam_messages = []
            st.rerun()

    elif selected_page == "Менің профилім":

        show_header()
        show_profile()

    show_footer()


# ============================================================
# 15. ЖҮЙЕГЕ КІРУ ЖӘНЕ ТІРКЕЛУ
# ============================================================

else:

    show_header()

    st.markdown(
        """
        <div class="login-banner">
            <h1>FIZIKA QADAM</h1>
            <p>
                Физиканы түсін. Зертте. Жаңа қадам жаса!
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    login_tab, register_tab = st.tabs(
        ["🔐 Жүйеге кіру", "📝 Тіркелу"]
    )

    # ---------------- ЖҮЙЕГЕ КІРУ ----------------

    with login_tab:

        st.subheader("Жүйеге қош келдің!")

        with st.form("login_form"):

            email = st.text_input(
                "Электрондық пошта",
                placeholder="example@mail.com"
            )

            password = st.text_input(
                "Құпиясөз",
                type="password"
            )

            login_button = st.form_submit_button(
                "Жүйеге кіру",
                use_container_width=True
            )

        if login_button:

            if not email or not password:

                st.warning(
                    "Электрондық пошта мен құпиясөзді енгіз."
                )

            else:

                try:
                    response = supabase.auth.sign_in_with_password(
                        {
                            "email": email,
                            "password": password
                        }
                    )

                    auth_user = response.user

                    if auth_user:

                        profile_response = (
                            supabase.table("profiles")
                            .select("*")
                            .eq("id", auth_user.id)
                            .execute()
                        )

                        if profile_response.data:

                            profile = profile_response.data[0]

                            st.session_state.user = {
                                **profile,
                                "id": auth_user.id,
                                "email": auth_user.email
                            }

                        else:

                            st.session_state.user = {
                                "id": auth_user.id,
                                "email": auth_user.email,
                                "full_name": (
                                    auth_user.user_metadata.get(
                                        "full_name",
                                        "Пайдаланушы"
                                    )
                                    if auth_user.user_metadata
                                    else "Пайдаланушы"
                                ),
                                "role": "student",
                                "grade": 9
                            }

                        st.session_state.current_page = "Басты бет"

                        st.success(
                            "Жүйеге сәтті кірдің!"
                        )

                        st.rerun()

                except Exception as e:

                    st.error(
                        "Жүйеге кіру мүмкін болмады. "
                        "Электрондық пошта мен құпиясөзді тексер."
                    )

                    st.caption(str(e))

    # ---------------- ТІРКЕЛУ ----------------

    with register_tab:

        st.subheader("Жаңа аккаунт ашу")

        with st.form("register_form"):

            full_name = st.text_input(
                "Аты-жөнің"
            )

            register_email = st.text_input(
                "Электрондық пошта"
            )

            register_password = st.text_input(
                "Құпиясөз",
                type="password"
            )

            confirm_password = st.text_input(
                "Құпиясөзді қайтала",
                type="password"
            )

            role = st.selectbox(
                "Пайдаланушы түрі:",
                ["student", "teacher"],
                format_func=lambda x: (
                    "Оқушы" if x == "student" else "Мұғалім"
                )
            )

            grade = st.selectbox(
                "Сынып:",
                [7, 8, 9, 10, 11]
            )

            register_button = st.form_submit_button(
                "Тіркелу",
                use_container_width=True
            )

        if register_button:

            if not all([
                full_name,
                register_email,
                register_password,
                confirm_password
            ]):

                st.warning(
                    "Барлық қажетті жолдарды толтыр."
                )

            elif register_password != confirm_password:

                st.error(
                    "Құпиясөздер бірдей емес."
                )

            elif len(register_password) < 8:

                st.warning(
                    "Құпиясөз кемінде 8 таңбадан тұруы керек."
                )

            else:

                try:

                    response = supabase.auth.sign_up(
                        {
                            "email": register_email,
                            "password": register_password,
                            "options": {
                                "data": {
                                    "full_name": full_name,
                                    "role": role,
                                    "grade": grade
                                }
                            }
                        }
                    )

                    auth_user = response.user

                    if auth_user:

                        st.success(
                            "Тіркелу сұранысы қабылданды!"
                        )

                        st.info(
                            "Электрондық поштаға растау хаты "
                            "жіберілуі мүмкін. Поштаңды тексер."
                        )

                    else:

                        st.warning(
                            "Тіркелу аяқталмады. Қайта байқап көр."
                        )

                except Exception as e:

                    st.error(
                        f"Тіркелу қатесі: {e}"
                    )

    show_footer()


# ============================================================
# 16. QADAM AI ҚАЛҚЫМАЛЫ ЧАТЫН ІСКЕ ҚОСУ
# ============================================================

if st.session_state.user is not None:
    show_floating_qadam_chat()
