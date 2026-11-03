
import streamlit as st
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
            supabase_url,
            supabase_key
        )

    except Exception as e:
        st.error("Supabase байланысы орнамады.")
        st.caption(f"Қате түрі: {type(e).__name__}")
        st.stop()

supabase = st.session_state.supabase_client

if "user" not in st.session_state:
    st.session_state.user = None

if "navigation" not in st.session_state:
    st.session_state.navigation = "Басты бет"


# =====================================================
# 3. PREMIUM WHITE ДИЗАЙНЫ
# =====================================================

st.markdown("""
<style>

/* Негізгі фон */

.stApp {
    background: #F5F8FC;
    color: #172B4D;
}

/* Негізгі мәтін */

h1, h2, h3, h4, p, label {
    color: #172B4D;
}

/* Негізгі тақырып */

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

/* Бүйір мәзір */

[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E8EDF4;
}

[data-testid="stSidebar"] > div {
    padding-top: 25px;
}

/* Навигация батырмалары */

[data-testid="stSidebar"] .stRadio label {
    padding: 10px 12px;
    border-radius: 10px;
    color: #43536B;
    font-weight: 600;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background: #EDF5FF;
}

/* Батырмалар */

.stButton > button {
    background: #1769AA;
    color: white;
    border: none;
    border-radius: 10px;
    min-height: 43px;
    font-weight: 600;
    transition: 0.2s;
}

.stButton > button:hover {
    background: #10558E;
    color: white;
    border: none;
}

/* Формалар */

.stTextInput input,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 9px;
}

/* Карточкалар */

.info-card {
    background: white;
    border: 1px solid #E8EDF4;
    border-radius: 15px;
    padding: 22px;
    min-height: 130px;
    box-shadow: 0 3px 12px rgba(25, 55, 90, 0.04);
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

/* Басты баннер */

.main-banner {
    background: linear-gradient(110deg, #FFFFFF, #EAF4FF);
    border: 1px solid #DFEAF7;
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 22px;
}

.banner-label {
    color: #1769AA;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 1px;
}

.banner-title {
    color: #142B4A;
    font-size: 30px;
    font-weight: 800;
    margin-top: 10px;
}

.banner-text {
    color: #64748B;
    font-size: 15px;
}

/* Бөлімдер */

div[data-testid="stExpander"] {
    background: white;
    border: 1px solid #E5EBF2;
    border-radius: 12px;
    margin-bottom: 8px;
}

/* Бөлгіш */

hr {
    border-color: #E6ECF3;
}

/* Төменгі жазу */

.footer {
    color: #94A3B8;
    text-align: center;
    font-size: 12px;
    padding: 20px;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 4. ҚОСАЛҚЫ ФУНКЦИЯЛАР
# =====================================================

def show_footer():
    st.markdown("""
    <div class="footer">
        ⚛️ FIZIKA QADAM © 2026
        <br>
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


def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.user = None
    st.session_state.navigation = "Басты бет"

    for key in ["course_grade", "course_track"]:
        st.session_state.pop(key, None)

    st.rerun()


# =====================================================
# 5. БАСТЫ БЕТ
# =====================================================

def show_dashboard():

    user = st.session_state.user

    st.markdown(f"""
    <div class="main-banner">
        <div class="banner-label">FIZIKA QADAM • ОҚУ ПЛАТФОРМАСЫ</div>
        <div class="banner-title">
            Қош келдіңіз, {user['fullname']}!
        </div>
        <div class="banner-text">
            Білім алуға, зерттеуге және жаңа жетістіктерге қадам жасаңыз.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if user["role"] == "student":

        grade = user.get("grade") or "—"

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="info-card">
                <h3>🎓 Менің сыныбым</h3>
                <p>Сіздің оқу деңгейіңіз</p>
            </div>
            """, unsafe_allow_html=True)
            st.metric("Сынып", f"{grade}")

        with col2:
            st.markdown("""
            <div class="info-card">
                <h3>⚛️ Физика курсы</h3>
                <p>7–11 сынып бағдарламасы</p>
            </div>
            """, unsafe_allow_html=True)
            st.write("Физика пәні")

        with col3:
            st.markdown("""
            <div class="info-card">
                <h3>🧠 Оқу бағыты</h3>
                <p>Теория және практикалық есептер</p>
            </div>
            """, unsafe_allow_html=True)
            st.write("Жеке оқу")

        st.divider()

        st.subheader("📚 Оқу мүмкіндіктері")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="info-card">
                <h3>⚛️ Физика курсы</h3>
                <p>
                    Теория, формулалар, мысалдар және
                    тақырыптық сабақтар.
                </p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("КУРСҚА ӨТУ", key="dashboard_course"):
                st.session_state.navigation = "Физика курсы"
                st.rerun()

        with col2:
            st.markdown("""
            <div class="info-card">
                <h3>🧮 Есептер мен тапсырмалар</h3>
                <p>
                    Физикалық есептерді шешу дағдыларын
                    дамытуға арналған бөлім.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.info("Есептер банкі әзірлену үстінде.")

    elif user["role"] == "teacher":

        st.subheader("👩‍🏫 Мұғалім кабинеті")

        st.markdown(f"""
        <div class="info-card">
            <h3>Мұғалім туралы ақпарат</h3>
            <p>Мектеп: {user['school']}</p>
            <p>Пәні: {user['subject']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.subheader("Мұғалім мүмкіндіктері")

        st.info("👥 Оқушыларды басқару — әзірлену үстінде")
        st.info("📝 Тапсырмалар беру — әзірлену үстінде")
        st.info("📊 Оқу нәтижелерін бақылау — әзірлену үстінде")


# =====================================================
# 6. ФИЗИКА КУРСЫ
# =====================================================

def show_physics_course():

    st.title("📚 Физика курсы")

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
            "jmb"
            if "ЖМБ" in track_choice
            else "qgb"
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
                {course['title']}
            </div>
            <div class="banner-text">
                {course.get('description') or 'Физика пәнін жүйелі меңгеру'}
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

                else:

                    for lesson_number, lesson in enumerate(
                        lessons, start=1
                    ):

                        with st.expander(
                            f"📘 {lesson_number}. {lesson['title']}"
                        ):

                            if lesson.get("learning_objective_code"):
                                st.caption(
                                    "Оқу мақсаты: "
                                    + lesson["learning_objective_code"]
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

        st.error("Физика курсын жүктеу кезінде қате пайда болды.")

        st.caption(
            f"Қате түрі: {type(e).__name__}: {str(e)[:300]}"
        )


# =====================================================
# 7. ПРОФИЛЬ
# =====================================================

def show_profile():

    user = st.session_state.user

    st.title("👤 Менің профилім")

    st.markdown("""
    <div class="main-banner">
        <div class="banner-label">ЖЕКЕ АҚПАРАТ</div>
        <div class="banner-title">Пайдаланушы профилі</div>
        <div class="banner-text">
            Жеке кабинетіңіздегі тіркелу мәліметтері.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write(f"**Аты-жөні:** {user['fullname']}")
    st.write(f"**Мектеп:** {user['school']}")
    st.write(f"**Рөлі:** {user['role']}")

    if user["role"] == "student":
        st.write(f"**Сыныбы:** {user['grade'] or 'Көрсетілмеген'}")

    if user["role"] == "teacher":
        st.write(f"**Пәні:** {user['subject']}")

    if user["requested_role"] == "teacher" and user["role"] != "teacher":
        st.warning("Мұғалім аккаунты әкімші растауын күтуде.")


# =====================================================
# 8. ОҚУ БӨЛІМДЕРІ
# =====================================================

def show_placeholder(title, description):

    st.title(title)

    st.markdown(f"""
    <div class="main-banner">
        <div class="banner-label">FIZIKA QADAM</div>
        <div class="banner-title">{title}</div>
        <div class="banner-text">{description}</div>
    </div>
    """, unsafe_allow_html=True)

    st.info("Бұл бөлім әзірлену үстінде. Жақын уақытта іске қосылады.")


# =====================================================
# 9. ЖЕКЕ КАБИНЕТ ЖӘНЕ SIDEBAR
# =====================================================

if st.session_state.user is not None:

    user = st.session_state.user

    # Бүйір мәзір

    with st.sidebar:

        st.markdown("""
        <div style="padding: 10px 5px 25px 5px;">
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

        if user["role"] == "student":

            menu_options = [
                "Басты бет",
                "Физика курсы",
                "Есептер банкі",
                "Тест тапсырмалары",
                "Жетістіктерім",
                "Менің профилім"
            ]

        elif user["role"] == "teacher":

            menu_options = [
                "Басты бет",
                "Мұғалім кабинеті",
                "Менің профилім"
            ]

        else:
            menu_options = ["Басты бет", "Менің профилім"]

        current_navigation = st.session_state.navigation

        if current_navigation not in menu_options:
            current_navigation = "Басты бет"

        selected_navigation = st.radio(
            "Навигация",
            menu_options,
            index=menu_options.index(current_navigation),
            key="navigation",
            label_visibility="collapsed"
        )

        st.divider()

        st.markdown(f"""
        <div style="padding:10px 5px;">
            <div style="font-size:12px;color:#94A3B8;">
                ЖҮЙЕГЕ КІРГЕН ПАЙДАЛАНУШЫ
            </div>
            <div style="font-weight:700;color:#172B4D;margin-top:5px;">
                {user['fullname']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("↪ Жүйеден шығу", use_container_width=True):
            logout()

    # Негізгі контент

    show_header()

    if selected_navigation == "Басты бет":

        show_dashboard()

    elif selected_navigation == "Физика курсы":

        show_physics_course()

    elif selected_navigation == "Есептер банкі":

        show_placeholder(
            "🧮 Есептер банкі",
            "Физикалық есептерді деңгей бойынша орындаңыз."
        )

    elif selected_navigation == "Тест тапсырмалары":

        show_placeholder(
            "📝 Тест тапсырмалары",
            "Білім деңгейіңізді тест арқылы тексеріңіз."
        )

    elif selected_navigation == "Жетістіктерім":

        show_placeholder(
            "🏆 Жетістіктерім",
            "Оқу барысындағы жетістіктеріңізді бақылаңыз."
        )

    elif selected_navigation == "Менің профилім":

        show_profile()

    elif selected_navigation == "Мұғалім кабинеті":

        show_dashboard()

    show_footer()


# =====================================================
# 10. ЖҮЙЕГЕ КІРУ ЖӘНЕ ТІРКЕЛУ
# =====================================================

else:

    show_header()

    st.markdown("""
    <div class="main-banner">
        <div class="banner-label">БІЛІМ • ҒЫЛЫМ • ТЕХНОЛОГИЯ</div>
        <div class="banner-title">
            Физиканы жаңа деңгейде меңгер!
        </div>
        <div class="banner-text">
            Теорияны түсін, формулаларды үйрен,
            есептерді өз бетіңше шеш.
        </div>
    </div>
    """, unsafe_allow_html=True)

    login_tab, register_tab = st.tabs([
        "🔐 Жүйеге кіру",
        "📝 Тіркелу"
    ])

    # -------------------------------------
    # ЖҮЙЕГЕ КІРУ
    # -------------------------------------

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

            if not login_email.strip() or not login_password:

                st.warning("Email мен құпиясөзді енгізіңіз.")

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

                            st.error("Пайдаланушы профилі табылмады.")
                            supabase.auth.sign_out()

                        else:

                            profile = profile_result.data[0]

                            st.session_state.user = {
                                "id": str(auth_user.id),
                                "fullname": profile.get("full_name") or "",
                                "role": profile.get("role") or "student",
                                "requested_role": profile.get("requested_role") or "student",
                                "school": profile.get("school") or "",
                                "grade": profile.get("grade"),
                                "subject": profile.get("subject") or ""
                            }

                            st.session_state.navigation = "Басты бет"

                            st.rerun()

                except Exception as e:

                    st.error("Жүйеге кіру кезінде қате пайда болды.")
                    st.caption(f"Қате түрі: {type(e).__name__}")


    # -------------------------------------
    # ТІРКЕЛУ
    # -------------------------------------

    with register_tab:

        st.subheader("Жаңа аккаунт ашу")

        register_role = st.radio(
            "Тіркелу түрі",
            ["Оқушы", "Мұғалім"],
            horizontal=True
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

            elif register_role == "Мұғалім" and not subject.strip():

                st.warning("Пәніңізді енгізіңіз.")

            elif not register_email.strip() or "@" not in register_email:

                st.warning("Дұрыс электрондық пошта енгізіңіз.")

            elif len(register_password) < 8:

                st.warning("Құпиясөз кемінде 8 таңбадан тұруы керек.")

            elif register_password != confirm_password:

                st.error("Құпиясөздер сәйкес келмейді.")

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
                                "grade": str(grade) if grade else "",
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

                    st.error("Тіркелу кезінде қате пайда болды.")
                    st.caption(f"Қате түрі: {type(e).__name__}")

    show_footer()
