import html
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from openai import OpenAI
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

        fig.add_trace(
            go.Scatter3d(
                x=x, y=y, z=z,
                mode="lines",
                line=dict(color="#55A6E8", width=5)
            )
        )

    fig.add_trace(
        go.Scatter3d(
            x=[0], y=[0], z=[0],
            mode="markers",
            marker=dict(
                size=22,
                color="#FF9F43",
                line=dict(color="#D96B27", width=2)
            )
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=[1.35, -0.75, 0],
            y=[0, 0.95, -1.35],
            z=[0.25, 0.75, 0.0],
            mode="markers",
            marker=dict(
                size=9,
                color=["#1769AA", "#7B61FF", "#19A7A0"],
                line=dict(color="white", width=1)
            )
        )
    )

    return style_3d_figure(
        fig, "АТОМ ҚҰРЫЛЫСЫ • 3D модель"
    )


def magnetic_figure():
    fig = go.Figure()
    t = np.linspace(0, 2*np.pi, 220)

    for radius in [0.55, 0.85, 1.15, 1.45]:
        x = radius*np.cos(t)
        y = 0.72*radius*np.sin(t)
        z = 0.42*np.sin(2*t) * (1.5-radius/2)

        fig.add_trace(
            go.Scatter3d(
                x=x, y=y, z=z,
                mode="lines",
                line=dict(color="#287BC1", width=5)
            )
        )

    fig.add_trace(
        go.Scatter3d(
            x=[-1.6, 1.6],
            y=[0, 0],
            z=[0, 0],
            mode="markers+text",
            text=["N", "S"],
            textposition="top center",
            marker=dict(
                size=13,
                color=["#E65C5C", "#287BC1"]
            )
        )
    )

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

    fig.add_trace(
        go.Scatter3d(
            x=length*np.sin(arc),
            y=0*arc,
            z=-length*np.cos(arc),
            mode="lines",
            line=dict(color="#9AB8D6", width=4, dash="dot")
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=[0, bob_x],
            y=[0, 0],
            z=[0, bob_z],
            mode="lines",
            line=dict(color="#1769AA", width=7)
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=[0], y=[0], z=[0],
            mode="markers",
            marker=dict(size=8, color="#17365D")
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=[bob_x],
            y=[0],
            z=[bob_z],
            mode="markers",
            marker=dict(
                size=19,
                color="#FF9F43",
                line=dict(color="#D96B27", width=2)
            )
        )
    )

    return style_3d_figure(
        fig,
        f"МАТЕМАТИКАЛЫҚ МАЯТНИК • бұрыш {angle_degrees}°"
    )


def prism_figure():
    fig = go.Figure()

    x = [0, 1.4, 0.7, 0, 1.4, 0.7]
    y = [-0.7, -0.7, 0.7, -0.7, -0.7, 0.7]
    z = [-0.6, -0.6, -0.6, 0.6, 0.6, 0.6]

    fig.add_trace(
        go.Mesh3d(
            x=x, y=y, z=z,
            i=[0, 0, 0, 3, 3, 1, 1, 2],
            j=[1, 2, 3, 4, 5, 4, 2, 5],
            k=[2, 3, 1, 5, 4, 2, 5, 4],
            color="#77B8E8",
            opacity=0.48,
            flatshading=True
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=[-1.3, 0.05],
            y=[0, 0],
            z=[0, 0],
            mode="lines",
            line=dict(color="#F2B705", width=8)
        )
    )

    colors = [
        "#E53935", "#FB8C00", "#FDD835",
        "#43A047", "#1E88E5", "#5E35B1"
    ]

    for i, color in enumerate(colors):
        yy = -0.48 + i*0.19

        fig.add_trace(
            go.Scatter3d(
                x=[1.1, 2.0],
                y=[0.05, yy],
                z=[0.0, 0.12*(i-2.5)],
                mode="lines",
                line=dict(color=color, width=6)
            )
        )

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
# 6. QADAM AI — OPENAI RESPONSES API
# =====================================================
QADAM_INSTRUCTIONS = """
Сен FIZIKA QADAM платформасының қазақ тілінде сөйлейтін физика пәні көмекшісісің.
Негізгі аудитория: 7–11 сынып оқушылары. Тек физикаға қатысты сұрақтарға жауап бер.
Түсіндіруші режимде ұғымды қарапайым тілмен, күнделікті өмірден қауіпсіз мысалмен түсіндір.
Есеп шығарушы режимде: Берілгені, ХБЖ-ға келтіру, Формула, Шешуі, Жауабы ретімен көрсет.
Формуладағы әр шаманы түсіндір, өлшем бірліктерін жаз, есептеуді тексер.
Егер есептің шарты толық болмаса, жетіспейтін мәліметті сұра; ойдан сан қоспа.
Сенімді болмасаң, оны ашық айт. Оқушыны өз бетімен ойлануға жетелейтін бір қысқа тексеру сұрағын қос.
Жеке деректерді сұрама және қажет етпе. Қауіпті тәжірибелерді орындауға нұсқаулық берме.
Физикадан тыс сұрақ келсе, сыпайы түрде физика тақырыбына қайта бағытта.
"""


def ask_qadam_ai(messages, mode, grade):
    try:
        api_key = st.secrets["openai"]["api_key"]
    except Exception:
        return None, (
            "OpenAI API кілті әлі бапталмаған. "
            "Оны Streamlit Cloud → Settings → Secrets бөліміне "
            "жеке енгізу қажет. Кілтті чатқа немесе GitHub-қа жазбаңыз."
        )

    if not api_key or not str(api_key).strip():
        return None, (
            "OpenAI API кілті бос. "
            "Streamlit Secrets баптауын тексеріңіз."
        )

    mode_instruction = {
        "Түсіндіруші": (
            "Оқушының сұрағын тақырыпты түсіндіру ретінде қарастыр. "
            "Қарапайым тіл мен мысал қолдан."
        ),
        "Есеп шығарушы": (
            "Есептің толық шешімін ретімен көрсет: "
            "Берілгені, ХБЖ, Формула, Шешуі, Жауабы."
        ),
        "Екі режим": (
            "Алдымен ұғымды қысқаша түсіндір, содан кейін "
            "қажет болса формуламен және қадамдық шешумен көрсет."
        )
    }[mode]

    try:
        client = OpenAI(
            api_key=str(api_key).strip(),
            timeout=30.0,
            max_retries=1
        )

        response = client.responses.create(
            model="gpt-5.5",
            instructions=(
                QADAM_INSTRUCTIONS
                + f"\nОқушы сыныбы: {grade}."
                + f"\nЖауап режимі: {mode}. {mode_instruction}"
            ),
            input=[
                {
                    "role": item["role"],
                    "content": item["content"]
                }
                for item in messages[-10:]
            ],
            max_output_tokens=750,
            store=False
        )

        answer = (
            response.output_text
            or "Жауапты дайындау мүмкін болмады."
        ).strip()

        return answer, None

    except Exception as e:
        return None, (
            f"AI қызметіне қосылу кезінде қате шықты "
            f"({type(e).__name__}). API баптауын және "
            "интернет байланысын тексеріңіз."
        )


def show_floating_qadam_chat():
    """Жүйеге кірген пайдаланушыға көрсетілетін қалқымалы чат."""

    if st.session_state.user is None:
        return

    if st.session_state.qadam_chat_open:

        with st.container(key="qadam_chat_open"):

            header_col, close_col = st.columns([5, 1])

            with header_col:
                st.markdown("**⚛️ QADAM AI**")
                st.caption("Физика бойынша жеке көмекші")

            with close_col:
                if st.button(
                    "✕",
                    key="qadam_close",
                    help="Чатты жабу"
                ):
                    st.session_state.qadam_chat_open = False
                    st.rerun()

            mode = st.selectbox(
                "Жауап беру режимі",
                [
                    "Екі режим",
                    "Түсіндіруші",
                    "Есеп шығарушы"
                ],
                key="qadam_mode"
            )

            with st.container(height=265, border=True):
                for message in st.session_state.qadam_messages[-8:]:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            try:
                grade = (
                    st.session_state.user.get("grade")
                    or "көрсетілмеген"
                )
            except Exception:
                grade = "көрсетілмеген"

            with st.form(
                "qadam_chat_form",
                clear_on_submit=True
            ):
                question = st.text_input(
                    "Сұрағыңды жаз",
                    placeholder=(
                        "Мысалы: Ньютонның екінші заңы деген не?"
                    ),
                    max_chars=1200
                )

                send = st.form_submit_button(
                    "Жіберу",
                    use_container_width=True
                )

            clear_col, note_col = st.columns([1, 2])

            with clear_col:
                if st.button(
                    "Тазарту",
                    key="qadam_clear"
                ):
                    st.session_state.qadam_messages = [{
                        "role": "assistant",
                        "content": (
                            "Чат тазартылды. "
                            "Физикадан жаңа сұрағыңды жаза бер!"
                        )
                    }]
                    st.rerun()

            with note_col:
                st.caption("Жеке деректерді жазбаңыз.")

            if send:

                if not question.strip():
                    st.warning("Алдымен сұрағыңызды жазыңыз.")

                elif sum(
                    1 for m in st.session_state.qadam_messages
                    if m["role"] == "user"
                ) >= 20:
                    st.warning(
                        "Бұл сессиядағы сұрақ шегіне жеттіңіз. "
                        "Чатты тазалап, жалғастыруға болады."
                    )

                else:
                    st.session_state.qadam_messages.append({
                        "role": "user",
                        "content": question.strip()
                    })

                    answer, error = ask_qadam_ai(
                        st.session_state.qadam_messages,
                        mode,
                        grade
                    )

                    if error:
                        st.error(error)
                    else:
                        st.session_state.qadam_messages.append({
                            "role": "assistant",
                            "content": answer
                        })
                        st.rerun()

    else:
        with st.container(key="qadam_chat_closed"):

            if st.button(
                "💬",
                key="qadam_open",
                help="QADAM AI чатын ашу"
            ):
                st.session_state.qadam_chat_open = True
                st.rerun()


# =====================================================
# 7. БАСТЫ БЕТ
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
                cards[start:start+3]
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
# 8. ЖАЛПЫ ФИЗИКА КУРСЫ
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
                                + str(
                                    lesson["learning_objective_code"]
                                )
                            )

                        if lesson.get("learning_objective"):
                            st.markdown("#### 🎯 Оқу мақсаты")
                            st.write(
                                lesson["learning_objective"]
                            )

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
# 9. ЕСЕПТЕР ЖИНАҒЫ
# =====================================================
def show_tasks_collection():

    st.title("📚 Есептер жинағы")
    st.caption(
        "Физикалық есептерді ізде, таңда және өз біліміңді тексер."
    )

    st.divider()

    # Сынып таңдау
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

    # Күрделілік
    difficulty = st.selectbox(
        "📊 Есеп күрделілігі",
        ["Барлығы", "Жеңіл", "Орташа", "Күрделі"],
        key="tasks_difficulty"
    )

    st.divider()

    # Курс пен бөлімдерді жүктеу
    try:
        course_result = (
            supabase.table("physics_courses")
            .select("id, grade, track, title")
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

        unit_options = {"Барлық бөлімдер": None}

        for unit in units:
            unit_options[unit["title"]] = unit["id"]

        selected_unit = st.selectbox(
            "📖 Физика бөлімін таңда",
            list(unit_options.keys()),
            key="tasks_unit"
        )

        # Есептерді іздеу
        search_text = st.text_input(
            "🔍 Есеп іздеу",
            placeholder=(
                "Мысалы: Ньютон заңы, жылдамдық, күш, қысым..."
            ),
            key="tasks_search"
        )

        st.caption(
            "Есептің шартындағы сөздер арқылы іздеуге болады."
        )

        # Есептерді Supabase-тен алу
        query = (
            supabase.table("physics_tasks")
            .select("id, unit_id, question, difficulty")
            .eq("is_published", True)
        )

        if unit_options[selected_unit] is not None:
            query = query.eq(
                "unit_id",
                unit_options[selected_unit]
            )

        tasks_result = query.execute()
        tasks = tasks_result.data or []

        # Күрделілік бойынша сүзгі
        if difficulty != "Барлығы":
            tasks = [
                task for task in tasks
                if str(task.get("difficulty", "")).casefold()
                == difficulty.casefold()
            ]

        # Мәтін бойынша іздеу
        if search_text.strip():
            keyword = search_text.strip().casefold()

            tasks = [
                task for task in tasks
                if keyword in str(
                    task.get("question", "")
                ).casefold()
            ]

        st.divider()

        # Нәтиже саны
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Табылған есептер", len(tasks))

        with col2:
            st.metric("Таңдалған сынып", f"{grade}-сынып")

        st.divider()

        if not tasks:
            st.info(
                "Есеп табылмады. Басқа тақырып немесе сөз енгізіп көр."
            )
            return

        st.subheader("📝 Есептер тізімі")

        # Есептерді көрсету
        for number, task in enumerate(tasks, start=1):

            task_id = task["id"]

            with st.container(border=True):

                st.markdown(f"### Есеп №{number}")

                st.write(
                    task.get(
                        "question",
                        "Есеп шарты енгізілмеген."
                    )
                )

                if task.get("difficulty"):
                    st.caption(
                        f"Күрделілік деңгейі: {task['difficulty']}"
                    )

                answer = st.text_input(
                    "Жауабыңды енгіз",
                    placeholder="Мысалы: 25 м/с",
                    key=f"student_answer_{task_id}"
                )

                st.button(
                    "Жауабын тексеру",
                    key=f"check_task_{task_id}",
                    disabled=True,
                    help="Автоматты тексеру келесі кезеңде қосылады."
                )

                with st.expander("📘 Шешу жолы"):
                    st.info(
                        "Бұл есептің шешу жолын көрсету "
                        "функциясын келесі кезеңде қосамыз."
                    )

    except Exception as e:
        st.error(
            "Есептерді жүктеу кезінде қате пайда болды."
        )
        st.caption(f"Қате түрі: {type(e).__name__}")


# =====================================================
# 9. ПРОФИЛЬ ЖӘНЕ ӘЗІРЛЕНУ ҮСТІНДЕГІ БӨЛІМДЕР
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
# 10. НЕГІЗГІ БЕТТЕР ЖӘНЕ SIDEBAR
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
    show_floating_qadam_chat()


# =====================================================
# 11. ЖҮЙЕГЕ КІРУ ЖӘНЕ ТІРКЕЛУ
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
