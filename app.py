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
# =====================================================
# 6. QADAM AI — GEMINI ЖАСАНДЫ ИНТЕЛЛЕКТІ
# =====================================================

QADAM_INSTRUCTIONS = """
Сен QADAM AI атты қазақ тілінде сөйлейтін
физика пәнінің жеке көмекшісісің.

НЕГІЗГІ МІНДЕТТЕРІҢ:
1. Физика тақырыптарын түсінікті тілмен түсіндіру.
2. Есептерді кезең-кезеңімен шығару.
3. Формулалардың мағынасын түсіндіру.
4. Өлшем бірліктерін ХБЖ жүйесінде көрсету.
5. Күнделікті өмірден мысалдар келтіру.
6. Оқушының білім деңгейіне сай жауап беру.
7. Оқушыны өздігінен ойлануға және есеп шығаруға үйрету.

ЕСЕП ШЫҒАРУ ТӘРТІБІ:
1. Берілгені
2. ХБЖ
3. Формула
4. Шешуі
5. Жауабы

ЖАУАП БЕРУ ЕРЕЖЕЛЕРІ:
- Негізгі тіл — қазақ тілі.
- Жауап нақты әрі түсінікті болсын.
- Формулаларды дұрыс жаз.
- Қажет болса, мысал келтір.
- Оқушыға дөрекі сөйлеме.
- Белгісіз ақпаратты ойдан шығарма.
- Қауіпті тәжірибелерге нұсқаулық берме.
"""


def ask_qadam_ai(messages, mode, grade):

    try:
        from google import genai
        from google.genai import types

        # 1. Хабарламаларды тексеру
        if not messages:
            return None, "Алдымен сұрақ енгізіңіз."

        # 2. API кілтін алу
        try:
            api_key = st.secrets["gemini"]["api_key"].strip()

        except Exception:
            return None, (
                "Gemini API кілті табылмады. "
                "Streamlit Cloud → Settings → Secrets "
                "бөлімін тексеріңіз."
            )

        if not api_key:
            return None, "Gemini API кілті бос тұр."

        # 3. Gemini клиентін іске қосу
        client = genai.Client(api_key=api_key)

        # 4. Жүйелік нұсқаулық
        instructions = f"""
{QADAM_INSTRUCTIONS}

Оқушының сыныбы: {grade}
Жұмыс режимі: {mode}

Оқушының жас ерекшелігіне сай жауап бер.
Қазақ тілінде түсінікті жауап жаз.
"""

        # 5. Хабарламалар тарихын дайындау
        history = []

        for item in messages[:-1]:

            role = item.get("role", "user")
            content = item.get("content", "")

            if not content:
                continue

            if role == "assistant":
                role = "model"

            elif role != "user":
                continue

            history.append(
                types.Content(
                    role=role,
                    parts=[
                        types.Part(text=str(content))
                    ]
                )
            )

        # 6. Соңғы сұрақты алу
        last_message = messages[-1].get("content", "")

        if not str(last_message).strip():
            return None, "Сұрақ бос тұр."

        # 7. Gemini чатын құру
        chat = client.chats.create(
            model="gemini-2.5-flash",
            history=history,
            config=types.GenerateContentConfig(
                system_instruction=instructions,
                max_output_tokens=750,
                temperature=0.7
            )
        )

        # 8. Жауап алу
        response = chat.send_message(
            message=str(last_message)
        )

        answer = response.text

        if not answer:
            return None, (
                "Gemini бос жауап қайтарды. "
                "Қайталап көріңіз."
            )

        return answer, None

    except Exception as e:

        error_details = str(e)

        # API кілтін қорғау
        if "api_key" in error_details.lower():
            error_details = "API кілтіне қатысты қате."

        elif "quota" in error_details.lower():
            error_details = (
                "Gemini API сұраныстарының лимиті аяқталған болуы мүмкін."
            )

        elif "permission" in error_details.lower():
            error_details = (
                "Gemini API рұқсатына қатысты қате."
            )

        return None, (
            f"Gemini қатесі: {type(e).__name__}\n\n"
            f"{error_details[:500]}"
        )      


# =====================================================
# 8. БАСТЫ БЕТ
# =====================================================

def show_dashboard():

    user = st.session_state.user

    safe_name = html.escape(
        str(user.get("fullname") or "оқушы")
    )

    st.markdown(f"""
    <div class="main-banner">
        <div class="banner-label">
            FIZIKA QADAM • ОҚУ ПЛАТФОРМАСЫ
        </div>
        <div class="banner-title">
            Қош келдіңіз, {safe_name}!
        </div>
        <div class="banner-text">
            Білім алуға, зерттеуге және жаңа жетістіктерге қадам жасаңыз.
        </div>
    </div>
    """, unsafe_allow_html=True)

    show_physics_world()

    st.divider()

    if user["role"] == "student":

        grade = user.get("grade") or "—"

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                '<div class="info-card">'
                '<h3>🎓 Менің сыныбым</h3>'
                '<p>Сіздің оқу деңгейіңіз</p>'
                '</div>',
                unsafe_allow_html=True
            )
            st.metric("Сынып", f"{grade}")

        with col2:
            st.markdown(
                '<div class="info-card">'
                '<h3>⚛️ Жалпы курс</h3>'
                '<p>7–11 сынып бағдарламасы</p>'
                '</div>',
                unsafe_allow_html=True
            )
            st.write("Физика пәні")

        with col3:
            st.markdown(
                '<div class="info-card">'
                '<h3>🧠 Оқу бағыты</h3>'
                '<p>Теория және практикалық есептер</p>'
                '</div>',
                unsafe_allow_html=True
            )
            st.write("Жеке оқу")

        st.divider()

        st.subheader("📚 Оқу мүмкіндіктері")

        cards = [
            (
                "⚛️ Жалпы курс",
                "Теория, формулалар және тақырыптық сабақтар.",
                "Жалпы курс"
            ),
            (
                "🧮 Есептер жинағы",
                "Физикалық есептерді деңгей бойынша орындау.",
                "Есептер жинағы"
            ),
            (
                "🏅 Олимпиада есептері",
                "Күрделілігі жоғары есептермен дайындалу.",
                "Олимпиада есептері"
            ),
            (
                "🧪 Виртуалды зертхана",
                "Физикалық құбылыстарды модельдеу.",
                "Виртуалды зертхана"
            ),
            (
                "🧠 QADAM шешімі",
                "Есепті қадамдарға бөліп талдау.",
                "QADAM шешімі"
            ),
            (
                "🤖 QADAM AI",
                "Физика сұрақтарын AI көмекшісімен талқылау.",
                "QADAM AI"
            )
        ]

        for start in range(0, len(cards), 3):

            cols = st.columns(3)

            for col, card in zip(
                cols,
                cards[start:start + 3]
            ):

                title, description, target = card

                with col:

                    st.markdown(
                        f'<div class="info-card">'
                        f'<h3>{html.escape(title)}</h3>'
                        f'<p>{html.escape(description)}</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                    if st.button(
                        "Ашу",
                        key=f"dashboard_{target}",
                        use_container_width=True
                    ):

                        if target == "QADAM AI":
                            st.session_state.qadam_chat_open = True
                            st.rerun()
                        else:
                            go_to(target)

    elif user["role"] == "teacher":

        st.subheader("👩‍🏫 Мұғалім кабинеті")

        st.markdown(f"""
        <div class="info-card">
            <h3>Мұғалім туралы ақпарат</h3>
            <p>Мектеп: {html.escape(str(user.get('school') or ''))}</p>
            <p>Пәні: {html.escape(str(user.get('subject') or ''))}</p>
        </div>
        """, unsafe_allow_html=True)

        st.info(
            "Оқушыларды басқару, тапсырма беру және оқу нәтижелерін "
            "бақылау бөлімдері кезең-кезеңімен қосылады."
        )


# =====================================================
# 9. ЖАЛПЫ ФИЗИКА КУРСЫ
# =====================================================

def show_physics_course():

    st.title("📚 Жалпы курс")

    st.write(
        "Өзіңіздің сыныбыңызға сәйкес курсты таңдап, "
        "тақырыптарды ретімен меңгеріңіз."
    )

    grade_options = [7, 8, 9, 10, 11]

    try:
        profile_grade = int(
            st.session_state.user.get("grade") or 7
        )
    except (TypeError, ValueError):
        profile_grade = 7

    grade_index = (
        grade_options.index(profile_grade)
        if profile_grade in grade_options
        else 0
    )

    selected_grade = st.selectbox(
        "Сыныпты таңдаңыз",
        grade_options,
        index=grade_index,
        key="course_grade"
    )

    if selected_grade in [10, 11]:

        track_choice = st.selectbox(
            "Оқу бағытын таңдаңыз",
            [
                "Жаратылыстану-математикалық бағыт (ЖМБ)",
                "Қоғамдық-гуманитарлық бағыт (ҚГБ)"
            ],
            key="course_track"
        )

        selected_track = (
            "jmb" if "ЖМБ" in track_choice else "qgb"
        )

    else:

        selected_track = "common"
        st.info("Жалпы білім беретін курс")

    st.divider()

    try:

        course_result = (
            supabase.table("physics_courses")
            .select("id, grade, track, title, description")
            .eq("grade", selected_grade)
            .eq("track", selected_track)
            .eq("is_published", True)
            .limit(1)
            .execute()
        )

        if not course_result.data:
            st.warning(
                "Бұл сыныпқа арналған курс әзірге жарияланбаған."
            )
            return

        course = course_result.data[0]

        st.markdown(f"""
        <div class="main-banner">
            <div class="banner-label">
                {selected_grade}-СЫНЫП • ФИЗИКА
            </div>
            <div class="banner-title">
                {html.escape(str(course.get('title') or 'Физика курсы'))}
            </div>
            <div class="banner-text">
                {html.escape(str(course.get('description') or 'Физика пәнін жүйелі меңгеру'))}
            </div>
        </div>
        """, unsafe_allow_html=True)

        units_result = (
            supabase.table("physics_units")
            .select("id, title, description, sort_order")
            .eq("course_id", course["id"])
            .order("sort_order")
            .execute()
        )

        units = units_result.data or []

        if not units:
            st.info("Бұл курста әзірге бөлімдер жоқ.")
            return

        st.subheader("📂 Курс бөлімдері")
        st.caption(f"Барлық бөлім саны: {len(units)}")

        for number, unit in enumerate(units, start=1):

            with st.expander(
                f"📂 {number}. {unit['title']}"
            ):

                if unit.get("description"):
                    st.write(unit["description"])

                lessons_result = (
                    supabase.table("physics_lessons")
                    .select(
                        "id, title, learning_objective_code, "
                        "learning_objective, theory, formulas, "
                        "examples, sort_order"
                    )
                    .eq("unit_id", unit["id"])
                    .eq("is_published", True)
                    .order("sort_order")
                    .execute()
                )

                lessons = lessons_result.data or []

                if not lessons:
                    st.caption(
                        "Бұл бөлімге сабақтар әлі енгізілмеген."
                    )

                for lesson_number, lesson in enumerate(
                    lessons,
                    start=1
                ):

                    with st.expander(
                        f"📘 {lesson_number}. {lesson['title']}"
                    ):

                        if lesson.get("learning_objective_code"):
                            st.caption(
                                "Оқу мақсаты: "
                                + str(lesson["learning_objective_code"])
                            )

                        if lesson.get("learning_objective"):
                            st.markdown("#### 🎯 Оқу мақсаты")
                            st.write(lesson["learning_objective"])

                        if lesson.get("theory"):
                            st.markdown("#### 📖 Теория")
                            st.write(lesson["theory"])

                        formulas = lesson.get("formulas") or []

                        if formulas:
                            st.markdown("#### 🧮 Формулалар")

                            for formula in formulas:
                                st.info(str(formula))

                        examples = lesson.get("examples") or []

                        if examples:
                            st.markdown("#### 💡 Мысалдар")

                            for example in examples:
                                st.write(example)

    except Exception as e:

        st.error(
            "Физика курсын жүктеу кезінде қате пайда болды."
        )

        st.caption(
            f"Қате түрі: {type(e).__name__}: {str(e)[:250]}"
        )


# =====================================================
# 10. ЕСЕПТЕР ЖИНАҒЫ
# =====================================================

def show_tasks_collection():

    st.title("📚 Есептер жинағы")

    st.caption(
        "Физикалық есептерді тақырып және күрделілік "
        "деңгейі бойынша орында."
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        grade = st.selectbox(
            "🎓 Сыныпты таңда",
            [7, 8, 9, 10, 11],
            key="tasks_grade"
        )

    with col2:

        if grade in [10, 11]:

            direction_name = st.selectbox(
                "Оқу бағыты",
                ["ЖМБ", "ҚГБ"],
                key="tasks_direction"
            )

            track = "jmb" if direction_name == "ЖМБ" else "qgb"

        else:

            track = "common"

            st.text_input(
                "Оқу бағыты",
                value="Жалпы курс",
                disabled=True
            )

    st.divider()

    try:

        course_result = (
            supabase.table("physics_courses")
            .select("id")
            .eq("grade", grade)
            .eq("track", track)
            .eq("is_published", True)
            .limit(1)
            .execute()
        )

        if not course_result.data:
            st.warning("Бұл сыныпқа жарияланған курс табылмады.")
            return

        course_id = course_result.data[0]["id"]

        units_result = (
            supabase.table("physics_units")
            .select("id, title, sort_order")
            .eq("course_id", course_id)
            .order("sort_order")
            .execute()
        )

        units = units_result.data or []

        if not units:
            st.info("Курс бөлімдері әлі енгізілмеген.")
            return

        unit_options = {"Барлық бөлімдер": None}

        for unit in units:
            unit_options[unit["title"]] = unit["id"]

        selected_unit = st.selectbox(
            "📖 Физика бөлімін таңда",
            list(unit_options.keys()),
            key="tasks_unit"
        )

        if unit_options[selected_unit] is not None:
            selected_unit_ids = [unit_options[selected_unit]]
        else:
            selected_unit_ids = [
                unit["id"] for unit in units
            ]

        lessons_result = (
            supabase.table("physics_lessons")
            .select("id, unit_id, title")
            .eq("is_published", True)
            .in_("unit_id", selected_unit_ids)
            .execute()
        )

        lessons = lessons_result.data or []

        if not lessons:
            st.info("Бұл бөлімде жарияланған сабақтар жоқ.")
            return

        lesson_ids = [
            lesson["id"] for lesson in lessons
        ]

        lesson_titles = {
            lesson["id"]: lesson["title"]
            for lesson in lessons
        }

        tasks_result = (
            supabase.table("physics_tasks")
            .select(
                "id, lesson_id, question, difficulty, "
                "task_type, sort_order"
            )
            .eq("is_published", True)
            .in_("lesson_id", lesson_ids)
            .order("sort_order")
            .execute()
        )

        tasks = tasks_result.data or []

        search_text = st.text_input(
            "🔍 Есеп іздеу",
            placeholder="Мысалы: жылдамдық, күш...",
            key="tasks_search"
        )

        if search_text.strip():

            keyword = search_text.strip().casefold()

            tasks = [
                task for task in tasks
                if keyword in str(
                    task.get("question", "")
                ).casefold()
            ]

        difficulty_labels = {
            "easy": "Жеңіл",
            "medium": "Орташа",
            "hard": "Күрделі"
        }

        available_difficulties = sorted({
            task.get("difficulty")
            for task in tasks
            if task.get("difficulty")
        })

        difficulty_options = ["Барлығы"] + [
            difficulty_labels.get(value, value)
            for value in available_difficulties
        ]

        selected_difficulty = st.selectbox(
            "📊 Есеп күрделілігі",
            difficulty_options,
            key="tasks_difficulty"
        )

        if selected_difficulty != "Барлығы":

            selected_code = next(
                (
                    code for code, label in difficulty_labels.items()
                    if label == selected_difficulty
                ),
                selected_difficulty
            )

            tasks = [
                task for task in tasks
                if task.get("difficulty") == selected_code
            ]

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Табылған есептер", len(tasks))

        with col2:
            st.metric("Сынып", f"{grade}-сынып")

        st.divider()

        if not tasks:
            st.info(
                "Есеп табылмады. Басқа бөлімді немесе "
                "іздеу сөзін таңдап көр."
            )
            return

        st.subheader("📝 Есептер тізімі")

        if "task_check_results" not in st.session_state:
            st.session_state.task_check_results = {}

        for number, task in enumerate(tasks, start=1):

            task_id = task["id"]

            lesson_title = lesson_titles.get(
                task["lesson_id"],
                "Физика сабағы"
            )

            with st.container(border=True):

                st.markdown(f"### Есеп №{number}")
                st.caption(f"📘 Сабақ: {lesson_title}")

                st.write(
                    task.get(
                        "question",
                        "Есеп шарты енгізілмеген."
                    )
                )

                difficulty_text = difficulty_labels.get(
                    task.get("difficulty"),
                    task.get("difficulty", "")
                )

                if difficulty_text:
                    st.caption(
                        f"Күрделілік: {difficulty_text}"
                    )

                with st.form(key=f"task_form_{task_id}"):

                    answer = st.text_input(
                        "Жауабыңды енгіз",
                        placeholder="Мысалы: 25 м/с",
                        key=f"student_answer_{task_id}"
                    )

                    submitted = st.form_submit_button(
                        "Жауабын тексеру",
                        use_container_width=True
                    )

                if submitted:

                    if not answer.strip():

                        st.warning(
                            "Алдымен жауабыңды енгіз."
                        )

                    else:

                        try:

                            check_result = supabase.rpc(
                                "check_physics_task_answer",
                                {
                                    "p_task_id": str(task_id),
                                    "p_answer": answer.strip()
                                }
                            ).execute()

                            result_data = check_result.data or []

                            if not result_data:

                                st.error(
                                    "Тексеру нәтижесі алынбады. "
                                    "Supabase функциясын тексер."
                                )

                            else:

                                st.session_state.task_check_results[
                                    str(task_id)
                                ] = result_data[0]

                        except Exception as e:

                            st.error(
                                "Жауапты тексеру кезінде қате шықты."
                            )

                            st.caption(
                                f"{type(e).__name__}: {str(e)[:250]}"
                            )

                result = st.session_state.task_check_results.get(
                    str(task_id)
                )

                if result:

                    if result.get("is_correct"):

                        st.success(
                            "✅ Дұрыс жауап! Жарайсың!"
                        )

                        if result.get("explanation"):

                            with st.expander(
                                "📘 Шешу жолын көрсету"
                            ):
                                st.write(result["explanation"])

                    else:

                        st.error(
                            "❌ Жауап дұрыс емес. "
                            "Қайта ойланып, тағы бір рет көр."
                        )

    except Exception as e:

        st.error(
            "Есептерді жүктеу кезінде қате пайда болды."
        )

        st.code(str(e))


# =====================================================
# 11. ПРОФИЛЬ
# =====================================================

def show_profile():

    user = st.session_state.user

    st.title("👤 Менің профилім")

    st.markdown(
        '<div class="main-banner">'
        '<div class="banner-label">ЖЕКЕ АҚПАРАТ</div>'
        '<div class="banner-title">Пайдаланушы профилі</div>'
        '<div class="banner-text">'
        'Жеке кабинетіңіздегі тіркелу мәліметтері.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        f"**Аты-жөні:** {user.get('fullname') or ''}"
    )

    st.write(
        f"**Мектеп:** {user.get('school') or ''}"
    )

    st.write(
        f"**Рөлі:** {user.get('role') or ''}"
    )

    if user["role"] == "student":

        st.write(
            f"**Сыныбы:** {user.get('grade') or 'Көрсетілмеген'}"
        )

    if user["role"] == "teacher":

        st.write(
            f"**Пәні:** {user.get('subject') or ''}"
        )

    if (
        user.get("requested_role") == "teacher"
        and user.get("role") != "teacher"
    ):

        st.warning(
            "Мұғалім аккаунты әкімші растауын күтуде."
        )


# =====================================================
# 12. ӘЗІРЛЕНУ ҮСТІНДЕГІ БӨЛІМДЕР
# =====================================================

def show_placeholder(title, description):

    st.title(title)

    st.markdown(f"""
    <div class="main-banner">
        <div class="banner-label">FIZIKA QADAM</div>
        <div class="banner-title">
            {html.escape(title)}
        </div>
        <div class="banner-text">
            {html.escape(description)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "Бұл бөлім әзірлену үстінде. "
        "Келесі кезеңдерде функционалы қосылады."
    )


# =====================================================
# 13. НЕГІЗГІ БЕТТЕР ЖӘНЕ SIDEBAR
# =====================================================

if st.session_state.user is not None:

    user = st.session_state.user

    menu_options = [
        "Басты бет",
        "Жалпы курс",
        "Есептер жинағы",
        "Олимпиада есептері",
        "Виртуалды зертхана",
        "QADAM шешімі",
        "Тест тапсырмалары",
        "Менің жетістіктерім",
        "Менің профилім"
    ]

    with st.sidebar:

        st.markdown("""
        <div style="padding:10px 5px 25px 5px;">
            <div style="font-size:27px;font-weight:800;color:#1769AA;">
                ⚛️ FIZIKA
            </div>
            <div style="font-size:12px;color:#718096;letter-spacing:2px;">
                QADAM PLATFORM
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.caption("НЕГІЗГІ МӘЗІР")

        current = st.session_state.selected_page

        if current not in menu_options:
            current = "Басты бет"
            st.session_state.selected_page = current

        selected = st.radio(
            "Навигация",
            menu_options,
            index=menu_options.index(current),
            label_visibility="collapsed"
        )

        st.session_state.selected_page = selected

        st.divider()

        st.markdown(f"""
        <div style="padding:10px 5px;">
            <div style="font-size:12px;color:#94A3B8;">
                ЖҮЙЕГЕ КІРГЕН ПАЙДАЛАНУШЫ
            </div>
            <div style="font-weight:700;color:#172B4D;margin-top:5px;">
                {html.escape(str(user.get('fullname') or ''))}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "↪ Жүйеден шығу",
            use_container_width=True
        ):
            logout()

    show_header()

    selected_navigation = st.session_state.selected_page

    if selected_navigation == "Басты бет":

        show_dashboard()

    elif selected_navigation == "Жалпы курс":

        show_physics_course()

    elif selected_navigation == "Есептер жинағы":

        show_tasks_collection()

    elif selected_navigation == "Олимпиада есептері":

        show_placeholder(
            "🏅 Олимпиада есептері",
            "Олимпиадалық деңгейдегі физика есептерін талдаңыз."
        )

    elif selected_navigation == "Виртуалды зертхана":

        show_placeholder(
            "🧪 Виртуалды зертхана",
            "Физикалық тәжірибелер мен құбылыстардың интерактивті модельдері."
        )

        show_physics_world()

    elif selected_navigation == "QADAM шешімі":

        show_placeholder(
            "🧠 QADAM шешімі",
            "Есептің берілгенін, формуласын және шешу жолын кезең-кезеңімен талдаңыз."
        )

    elif selected_navigation == "Тест тапсырмалары":

        show_placeholder(
            "📝 Тест тапсырмалары",
            "Білім деңгейіңізді тақырыптық тест арқылы тексеріңіз."
        )

    elif selected_navigation == "Менің жетістіктерім":

        show_placeholder(
            "🏆 Менің жетістіктерім",
            "Оқу барысындағы жетістіктеріңізді бақылаңыз."
        )

    elif selected_navigation == "Менің профилім":

        show_profile()

    show_footer()
# =====================================================
# 13. QADAM AI — ҚАЛҚЫМАЛЫ ЧАТ
# =====================================================

def show_floating_qadam_chat():

    # =================================================
    # ЧАТ АШЫҚ БОЛСА
    # =================================================

    if st.session_state.qadam_chat_open:

        with st.container(key="qadam_chat_open"):

            # Чат тақырыбы
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown("### 🤖 QADAM AI")

            with col2:

                if st.button(
                    "✖",
                    key="close_qadam_chat"
                ):

                    st.session_state.qadam_chat_open = False
                    st.rerun()

            st.caption(
                "Физика бойынша жеке AI көмекшісі"
            )

            # Сынып таңдау
            grade = st.selectbox(
                "Сынып",
                [
                    "7-сынып",
                    "8-сынып",
                    "9-сынып",
                    "10-сынып",
                    "11-сынып"
                ],
                index=2,
                key="qadam_grade"
            )

            # Жұмыс режимі
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

            # =================================================
            # ХАБАРЛАМАЛАР ТАРИХЫ
            # =================================================

            for message in st.session_state.qadam_messages:

                with st.chat_message(message["role"]):

                    st.markdown(
                        message["content"]
                    )

            # =================================================
            # СҰРАҚ ЕНГІЗУ
            # =================================================

            with st.form(
                "qadam_chat_form",
                clear_on_submit=True
            ):

                prompt = st.text_area(
                    "Сұрағыңды жаз...",
                    placeholder=(
                        "Мысалы: Ньютонның бірінші заңы дегеніміз не?"
                    ),
                    height=80
                )

                submitted = st.form_submit_button(
                    "Жіберу",
                    use_container_width=True
                )

            # =================================================
            # GEMINI-ГЕ СҰРАҚ ЖІБЕРУ
            # =================================================

            if submitted:

                if not prompt.strip():

                    st.warning(
                        "Алдымен сұрақ енгіз."
                    )

                else:

                    # Оқушы хабарламасын сақтау
                    st.session_state.qadam_messages.append({
                        "role": "user",
                        "content": prompt.strip()
                    })

                    # AI жауабын алу
                    with st.spinner(
                        "QADAM AI жауап дайындауда..."
                    ):

                        answer, error = ask_qadam_ai(
                            st.session_state.qadam_messages,
                            mode,
                            grade
                        )

                    # Қате болса
                    if error:

                        st.error(error)

                        # Қате болғанда соңғы сұрақты
                        # хабарламалар тарихында қалдырамыз.

                    # Жауап сәтті болса
                    else:

                        st.session_state.qadam_messages.append({
                            "role": "assistant",
                            "content": answer
                        })

                    st.rerun()

            st.divider()

            # =================================================
            # ЧАТТЫ ТАЗАЛАУ
            # =================================================

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

    # =================================================
    # ЧАТ ЖАБЫҚ БОЛСА
    # =================================================

    else:
        with st.container(
            key="qadam_chat_closed"
        ):
            
            if st.button(
                "🤖",
                key="open_qadam_chat"
            ):

                st.session_state.qadam_chat_open = True
                st.rerun()
    


# =====================================================
# 14. ЖҮЙЕГЕ КІРУ ЖӘНЕ ТІРКЕЛУ
# =====================================================
else:
    show_header()
    st.markdown("""
    <div class="main-banner">
        <div class="banner-label">
            БІЛІМ • ҒЫЛЫМ • ТЕХНОЛОГИЯ
        </div>
        <div class="banner-title">
            Физиканы жаңа деңгейде меңгер!
        </div>
        <div class="banner-text">
            Теорияны түсін, формулаларды үйрен,
            есептерді өз бетіңше шеш.
        </div>
    </div>
    """, unsafe_allow_html=True)

    show_physics_world()

    st.divider()

    login_tab, register_tab = st.tabs([
        "🔐 Жүйеге кіру",
        "📝 Тіркелу"
    ])

    # -----------------------------
    # ЖҮЙЕГЕ КІРУ
    # -----------------------------

    with login_tab:

        st.subheader("Жеке кабинетке кіру")

        with st.form("login_form"):

            login_email = st.text_input(
                "Электрондық пошта"
            )

            login_password = st.text_input(
                "Құпиясөз",
                type="password"
            )

            login_button = st.form_submit_button(
                "ЖҮЙЕГЕ КІРУ",
                use_container_width=True
            )

        if login_button:

            if (
                not login_email.strip()
                or not login_password
            ):

                st.warning(
                    "Email мен құпиясөзді енгізіңіз."
                )

            else:

                try:

                    response = supabase.auth.sign_in_with_password({
                        "email": login_email.strip(),
                        "password": login_password
                    })

                    auth_user = response.user

                    if auth_user is None:

                        st.error("Пайдаланушы табылмады.")

                    else:

                        profile_result = (
                            supabase.table("profiles")
                            .select("*")
                            .eq("id", str(auth_user.id))
                            .execute()
                        )

                        if not profile_result.data:

                            st.error(
                                "Пайдаланушы профилі табылмады."
                            )

                            supabase.auth.sign_out()

                        else:

                            profile = profile_result.data[0]

                            st.session_state.user = {
                                "id": str(auth_user.id),
                                "fullname": (
                                    profile.get("full_name") or ""
                                ),
                                "role": (
                                    profile.get("role") or "student"
                                ),
                                "requested_role": (
                                    profile.get("requested_role")
                                    or "student"
                                ),
                                "school": (
                                    profile.get("school") or ""
                                ),
                                "grade": profile.get("grade"),
                                "subject": (
                                    profile.get("subject") or ""
                                )
                            }

                            st.session_state.selected_page = "Басты бет"

                            st.rerun()

                except Exception as e:

                    st.error(
                        "Жүйеге кіру кезінде қате пайда болды."
                    )

                    st.caption(
                        f"Қате түрі: {type(e).__name__}"
                    )

    # -----------------------------
    # ТІРКЕЛУ
    # -----------------------------

    with register_tab:

        st.subheader("Жаңа аккаунт ашу")

        register_role = st.radio(
            "Тіркелу түрі",
            ["Оқушы", "Мұғалім"],
            horizontal=True,
            key="register_role"
        )

        with st.form("register_form"):

            fullname = st.text_input("Аты-жөні")

            school = st.text_input("Мектеп атауы")

            if register_role == "Оқушы":

                grade = st.selectbox(
                    "Сыныбы",
                    list(range(7, 12))
                )

                subject = ""

            else:

                grade = None
                subject = st.text_input("Пәні")

            register_email = st.text_input(
                "Электрондық пошта"
            )

            register_password = st.text_input(
                "Құпиясөз",
                type="password"
            )

            confirm_password = st.text_input(
                "Құпиясөзді қайталаңыз",
                type="password"
            )

            register_button = st.form_submit_button(
                "ТІРКЕЛУ",
                use_container_width=True
            )

        if register_button:

            if not fullname.strip():

                st.warning("Аты-жөніңізді енгізіңіз.")

            elif not school.strip():

                st.warning("Мектеп атауын енгізіңіз.")

            elif (
                register_role == "Мұғалім"
                and not subject.strip()
            ):

                st.warning("Пәніңізді енгізіңіз.")

            elif (
                not register_email.strip()
                or "@" not in register_email
            ):

                st.warning(
                    "Дұрыс электрондық пошта енгізіңіз."
                )

            elif len(register_password) < 8:

                st.warning(
                    "Құпиясөз кемінде 8 таңбадан тұруы керек."
                )

            elif register_password != confirm_password:

                st.error(
                    "Құпиясөздер сәйкес келмейді."
                )

            else:

                try:

                    requested_role = (
                        "student"
                        if register_role == "Оқушы"
                        else "teacher"
                    )

                    response = supabase.auth.sign_up({
                        "email": register_email.strip(),
                        "password": register_password,
                        "options": {
                            "data": {
                                "full_name": fullname.strip(),
                                "school": school.strip(),
                                "grade": (
                                    str(grade) if grade else ""
                                ),
                                "subject": subject.strip(),
                                "requested_role": requested_role
                            }
                        }
                    })

                    if response.user:

                        st.success(
                            "Тіркелу сұранысы қабылданды! "
                            "Электрондық поштаңызға келген "
                            "растау сілтемесін ашыңыз. "
                            "Содан кейін жүйеге кіре аласыз."
                        )

                    else:

                        st.warning(
                            "Тіркелу аяқталмады. Қайталап көріңіз."
                        )

                except Exception as e:

                    st.error(
                        "Тіркелу кезінде қате пайда болды."
                    )

                    st.caption(
                        f"Қате түрі: {type(e).__name__}"
                    )

    show_footer()
    # =====================================================
# QADAM AI ЧАТЫН ЭКРАНҒА ШЫҒАРУ
# =====================================================

if st.session_state.user is not None:
    show_floating_qadam_chat()
