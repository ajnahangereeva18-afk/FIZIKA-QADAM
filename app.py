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
        show_placeholder(
            "🧮 Есептер жинағы",
            "Физикалық есептерді тақырып және күрделілік деңгейі бойынша орындаңыз."
        )

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
