
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

@st.cache_data
def get_config():
    return {
        "url": st.secrets["supabase"]["url"],
        "publishable_key": st.secrets["supabase"]["publishable_key"]
    }


try:
    config = get_config()

    supabase = create_client(
        config["url"],
        config["publishable_key"]
    )

except Exception as e:
    st.error("Supabase байланысы орнамады.")
    st.caption(f"Қате түрі: {type(e).__name__}")
    st.stop()


# =====================================
# 3. ДИЗАЙН
# =====================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #101d36, #173c60);
    color: white;
}

h1, h2, h3, p, label {
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
</style>
""", unsafe_allow_html=True)


# =====================================
# 4. СЕССИЯ
# =====================================

if "user" not in st.session_state:
    st.session_state.user = None


# =====================================
# 5. БАСТЫ ТАҚЫРЫП
# =====================================

st.markdown("""
<h1 style="text-align:center;">
    ⚛️ FIZIKA QADAM
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<p style="text-align:center;">
    Физикалық есептерді шешудің адаптивті цифрлық платформасы
</p>
""", unsafe_allow_html=True)

st.divider()


# =====================================
# 6. ЖЕКЕ КАБИНЕТ
# =====================================

if st.session_state.user is not None:

    user = st.session_state.user

    st.success(f"Қош келдіңіз, {user['fullname']}!")

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

    elif user["role"] == "student":

        st.title("🎓 ОҚУШЫ КАБИНЕТІ")

        st.write(f"Мектеп: {user['school']}")
        st.write(f"Сыныбы: {user['grade']}-сынып")

        st.subheader("Менің оқу бөлімдерім")

        col1, col2 = st.columns(2)

        with col1:
            st.info("📚 Физика курсы")
            st.info("🧮 Есептер банкі")
            st.info("🏆 Олимпиадаға дайындық")

        with col2:
            st.info("⚛️ QADAM шешімі")
            st.info("🧪 Виртуалды зертхана")
            st.info("📊 Менің жетістіктерім")

    else:

        st.title("👩‍🏫 МҰҒАЛІМ КАБИНЕТІ")

        st.write(f"Мектеп: {user['school']}")
        st.write(f"Пәні: {user['subject']}")

        st.subheader("Мұғалім мүмкіндіктері")

        st.info("👥 Оқушыларды басқару")
        st.info("📝 Тапсырмалар беру")
        st.info("📊 Оқушылардың нәтижелерін бақылау")

    st.divider()

    if st.button("ЖҮЙЕДЕН ШЫҒУ", key="logout_button"):

        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        st.session_state.user = None
        st.rerun()


# =====================================
# 7. ТІРКЕЛУ ЖӘНЕ КІРУ
# =====================================

else:

    login_tab, register_tab = st.tabs([
        "🔐 ЖҮЙЕГЕ КІРУ",
        "📝 ТІРКЕЛУ"
    ])

    # ---------------------------------
    # 7.1 ЖҮЙЕГЕ КІРУ
    # ---------------------------------

    with login_tab:

        st.subheader("Жеке кабинетке кіру")

        with st.form("login_form"):

            login_email = st.text_input(
                "Электрондық пошта",
                key="login_email"
            )

            login_password = st.text_input(
                "Құпиясөз",
                type="password",
                key="login_password"
            )

            login_button = st.form_submit_button("КІРУ")

        if login_button:

            if not login_email.strip() or not login_password:

                st.warning("Email мен құпиясөзді енгізіңіз!")

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

                            st.rerun()

                except Exception as e:
                    st.error("Кіру кезінде қате пайда болды.")
                    st.caption(f"Қате түрі: {type(e).__name__}")


    # ---------------------------------
    # 7.2 ТІРКЕЛУ
    # ---------------------------------

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

            register_button = st.form_submit_button("ТІРКЕЛУ")

        if register_button:

            if not fullname.strip():
                st.warning("Аты-жөніңізді енгізіңіз!")

            elif not school.strip():
                st.warning("Мектеп атауын енгізіңіз!")

            elif register_role == "Мұғалім" and not subject.strip():
                st.warning("Пәніңізді енгізіңіз!")

            elif not register_email.strip() or "@" not in register_email:
                st.warning("Дұрыс электрондық пошта енгізіңіз!")

            elif len(register_password) < 8:
                st.warning("Құпиясөз кемінде 8 таңбадан тұруы керек!")

            elif register_password != confirm_password:
                st.error("Құпиясөздер сәйкес келмейді!")

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


# =====================================
# 8. ТӨМЕНГІ БӨЛІМ
# =====================================

st.divider()

st.markdown("""
<p style="text-align:center;">
    FIZIKA QADAM © 2026
</p>
""", unsafe_allow_html=True)
