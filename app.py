
import streamlit as st
from supabase import create_client

# =====================================
# 1. БЕТ БАПТАУЛАРЫ
# =====================================

st.set_page_config(
    page_title="FIZIKA QADAM",
    page_icon="⚛️",
    layout="wide"
)

# =====================================
# 2. SUPABASE БАЙЛАНЫСЫ
# =====================================

# Клиентті әр қайта орындалғанда жаңадан құрмаймыз.
# Ол Streamlit сессиясында сақталады.

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


# =====================================
# 3. СЕССИЯ
# =====================================

if "user" not in st.session_state:
    st.session_state.user = None


# =====================================
# 4. ДИЗАЙН
# =====================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #101d36, #173c60);
    color: white;
}

h1, h2, h3, h4, p, label {
    color: white !important;
}

div.stButton > button {
    background: #16b8b0;
    color: white;
    border-radius: 10px;
    width: 100%;
    height: 45px;
    border: none;
}

div.stButton > button:hover {
    background: #119b95;
    color: white;
}

div[data-testid="stExpander"] {
    background: rgba(255,255,255,0.06);
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)


# =====================================
# 5. БАСТЫ ТАҚЫРЫП
# =====================================

st.markdown("""
<h1 style="text-align:center;">
    ⚛️ FIZIKA QADAM
</h1>

<p style="text-align:center;">
    Физикалық есептерді шешудің адаптивті цифрлық платформасы
</p>
""", unsafe_allow_html=True)

st.divider()


# =====================================
# 6. ФИЗИКА КУРСЫН КӨРСЕТУ
# =====================================

def show_physics_course():

    st.header("📚 ФИЗИКА КУРСЫ")

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

    # 10–11 сыныптарға оқу бағытын таңдау

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

    # Курсты Supabase-тен алу

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

            st.caption(
                f"Тексерілген сынып: {selected_grade}, "
                f"бағыт: {selected_track}"
            )

            return

        course = course_result.data[0]

        st.subheader(f"⚛️ {course['title']}")

        if course.get("description"):
            st.write(course["description"])

        # Курстың бөлімдерін алу

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

        st.write(f"**Курс бөлімдері: {len(units)}**")

        # Әр бөлімді көрсету

        for number, unit in enumerate(units, start=1):

            with st.expander(
                f"📂 {number}. {unit['title']}"
            ):

                if unit.get("description"):
                    st.write(unit["description"])

                # Бөлім сабақтарын алу

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
                        lessons,
                        start=1
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
                                st.write(
                                    lesson["learning_objective"]
                                )

                            if lesson.get("theory"):
                                st.markdown("### 📖 Теория")
                                st.write(lesson["theory"])

                            formulas = lesson.get("formulas") or []

                            if formulas:
                                st.markdown("### 🧮 Формулалар")

                                for formula in formulas:
                                    st.write(formula)

                            examples = lesson.get("examples") or []

                            if examples:
                                st.markdown("### 💡 Мысалдар")

                                for example in examples:
                                    st.write(example)

    except Exception as e:

        st.error(
            "Физика курсын жүктеу кезінде қате пайда болды."
        )

        st.caption(
            f"Қате түрі: {type(e).__name__}: {str(e)[:300]}"
        )


# =====================================
# 7. ЖЕКЕ КАБИНЕТ
# =====================================

if st.session_state.user is not None:

    user = st.session_state.user

    st.success(
        f"Қош келдіңіз, {user['fullname']}!"
    )

    # Мұғалім өтініші

    if (
        user["requested_role"] == "teacher"
        and user["role"] != "teacher"
    ):

        st.title("👤 ЖЕКЕ КАБИНЕТ")

        st.info(
            "Мұғалім аккаунтына өтінішіңіз қабылданды. "
            "Әкімші растағаннан кейін мұғалім мүмкіндіктері ашылады."
        )

        st.write(f"Мектеп: {user['school']}")
        st.write(f"Пәні: {user['subject']}")

    # Оқушы кабинеті

    elif user["role"] == "student":

        st.title("🎓 ОҚУШЫ КАБИНЕТІ")

        st.write(f"Мектеп: {user['school']}")
        st.write(f"Сыныбы: {user['grade']}-сынып")

        st.divider()

        show_physics_course()

        st.divider()

        st.subheader("Менің оқу бөлімдерім")

        col1, col2 = st.columns(2)

        with col1:
            st.info("🧮 Есептер банкі")
            st.info("🏆 Олимпиадаға дайындық")
            st.info("📝 Тест тапсырмалары")

        with col2:
            st.info("⚛️ QADAM шешімі")
            st.info("🧪 Виртуалды зертхана")
            st.info("📊 Менің жетістіктерім")

    # Мұғалім кабинеті

    elif user["role"] == "teacher":

        st.title("👩‍🏫 МҰҒАЛІМ КАБИНЕТІ")

        st.write(f"Мектеп: {user['school']}")
        st.write(f"Пәні: {user['subject']}")

        st.subheader("Мұғалім мүмкіндіктері")

        st.info("👥 Оқушыларды басқару")
        st.info("📝 Тапсырмалар беру")
        st.info("📊 Оқушылардың нәтижелерін бақылау")

    else:

        st.error("Аккаунт рөлі анықталмады.")

    st.divider()

    # Жүйеден шығу

    if st.button("ЖҮЙЕДЕН ШЫҒУ"):

        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        st.session_state.user = None
        st.session_state.pop("course_grade", None)
        st.session_state.pop("course_track", None)

        st.rerun()


# =====================================
# 8. ТІРКЕЛУ ЖӘНЕ КІРУ
# =====================================

else:

    login_tab, register_tab = st.tabs([
        "🔐 ЖҮЙЕГЕ КІРУ",
        "📝 ТІРКЕЛУ"
    ])

    # Жүйеге кіру

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
                "КІРУ"
            )

        if login_button:

            if (
                not login_email.strip()
                or not login_password
            ):

                st.warning(
                    "Email мен құпиясөзді енгізіңіз!"
                )

            else:

                try:

                    response = (
                        supabase.auth.sign_in_with_password({
                            "email": login_email.strip(),
                            "password": login_password
                        })
                    )

                    auth_user = response.user

                    if auth_user is None:

                        st.error(
                            "Пайдаланушы табылмады."
                        )

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
                                "fullname": profile.get("full_name") or "",
                                "role": profile.get("role") or "student",
                                "requested_role": profile.get("requested_role") or "student",
                                "school": profile.get("school") or "",
                                "grade": profile.get("grade"),
                                "subject": profile.get("subject") or ""
                            }

                            # Supabase клиенті мен оның auth
                            # сессиясы session_state ішінде қалады.

                            st.rerun()

                except Exception as e:

                    st.error(
                        "Жүйеге кіру кезінде қате пайда болды."
                    )

                    st.caption(
                        f"Қате түрі: {type(e).__name__}"
                    )


    # Тіркелу

    with register_tab:

        st.subheader("Жаңа аккаунт ашу")

        register_role = st.radio(
            "Тіркелу түрі",
            ["Оқушы", "Мұғалім"],
            horizontal=True
        )

        with st.form("register_form"):

            fullname = st.text_input(
                "Аты-жөні"
            )

            school = st.text_input(
                "Мектеп атауы"
            )

            if register_role == "Оқушы":

                grade = st.selectbox(
                    "Сыныбы",
                    list(range(7, 12))
                )

                subject = ""

            else:

                grade = None

                subject = st.text_input(
                    "Пәні"
                )

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
                "ТІРКЕЛУ"
            )

        if register_button:

            if not fullname.strip():

                st.warning(
                    "Аты-жөніңізді енгізіңіз!"
                )

            elif not school.strip():

                st.warning(
                    "Мектеп атауын енгізіңіз!"
                )

            elif (
                register_role == "Мұғалім"
                and not subject.strip()
            ):

                st.warning(
                    "Пәніңізді енгізіңіз!"
                )

            elif (
                not register_email.strip()
                or "@" not in register_email
            ):

                st.warning(
                    "Дұрыс электрондық пошта енгізіңіз!"
                )

            elif len(register_password) < 8:

                st.warning(
                    "Құпиясөз кемінде 8 таңбадан тұруы керек!"
                )

            elif register_password != confirm_password:

                st.error(
                    "Құпиясөздер сәйкес келмейді!"
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

                    st.error(
                        "Тіркелу кезінде қате пайда болды."
                    )

                    st.caption(
                        f"Қате түрі: {type(e).__name__}"
                    )


# =====================================
# 9. ТӨМЕНГІ БӨЛІМ
# =====================================

st.divider()

st.markdown("""
<p style="text-align:center;">
    FIZIKA QADAM © 2026
</p>
""", unsafe_allow_html=True)
