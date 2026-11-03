
import streamlit as st
import sqlite3
import hashlib
import secrets

# =====================================
# 1. БЕТ БАПТАУЛАРЫ
# =====================================

st.set_page_config(
    page_title="FIZIKA QADAM",
    page_icon="⚛️",
    layout="wide"
)

# =====================================
# 2. ДЕРЕКТЕР БАЗАСЫ
# =====================================

def connect_db():
    return sqlite3.connect("fizika_users.db")


def create_table():
    conn = connect_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            role TEXT NOT NULL,
            school TEXT NOT NULL,
            detail TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


create_table()

# =====================================
# 3. ҚҰПИЯСӨЗДІ ҚОРҒАУ
# =====================================

def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        200000
    ).hex()


# =====================================
# 4. ДИЗАЙН
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
# 5. СЕССИЯ
# =====================================

if "user" not in st.session_state:
    st.session_state.user = None


# =====================================
# 6. БАСТЫ ТАҚЫРЫП
# =====================================

st.markdown(
    """
    <h1 style="text-align:center;">
        ⚛️ FIZIKA QADAM
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style="text-align:center;">
        Физикалық есептерді шешудің адаптивті цифрлық платформасы
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()


# =====================================
# 7. ЖЕКЕ КАБИНЕТ
# =====================================

if st.session_state.user is not None:

    user = st.session_state.user

    st.success(
        f"Қош келдіңіз, {user['fullname']}!"
    )

    if user["role"] == "Оқушы":

        st.title("🎓 ОҚУШЫ КАБИНЕТІ")

        st.write(f"Мектеп: {user['school']}")
        st.write(f"Сыныбы: {user['detail']}")

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
        st.write(f"Пәні: {user['detail']}")

        st.subheader("Мұғалім мүмкіндіктері")

        st.info("👥 Оқушыларды басқару")
        st.info("📝 Тапсырмалар беру")
        st.info("📊 Оқушылардың нәтижелерін бақылау")

    st.divider()

    if st.button("ЖҮЙЕДЕН ШЫҒУ", key="logout_button"):

        st.session_state.user = None
        st.rerun()


# =====================================
# 8. ТІРКЕЛУ ЖӘНЕ ЖҮЙЕГЕ КІРУ
# =====================================

else:

    login_tab, register_tab = st.tabs([
        "🔐 ЖҮЙЕГЕ КІРУ",
        "📝 ТІРКЕЛУ"
    ])


    # ---------------------------------
    # 8.1 ЖҮЙЕГЕ КІРУ
    # ---------------------------------

    with login_tab:

        st.subheader("Жеке кабинетке кіру")

        with st.form("login_form"):

            login_username = st.text_input(
                "Логин",
                key="login_username"
            )

            login_password = st.text_input(
                "Құпиясөз",
                type="password",
                key="login_password"
            )

            login_button = st.form_submit_button(
                "КІРУ"
            )

        if login_button:

            username = login_username.strip()

            if not username or not login_password:

                st.warning(
                    "Логин мен құпиясөзді енгізіңіз!"
                )

            else:

                conn = connect_db()

                user = conn.execute(
                    """
                    SELECT * FROM users
                    WHERE username = ?
                    """,
                    (username,)
                ).fetchone()

                conn.close()

                if user is not None:

                    saved_hash = user[6]
                    salt = user[7]

                    entered_hash = hash_password(
                        login_password,
                        salt
                    )

                    if secrets.compare_digest(
                        saved_hash,
                        entered_hash
                    ):

                        st.session_state.user = {
                            "fullname": user[1],
                            "role": user[2],
                            "school": user[3],
                            "detail": user[4],
                            "username": user[5]
                        }

                        st.rerun()

                    else:

                        st.error(
                            "Құпиясөз дұрыс емес!"
                        )

                else:

                    st.error(
                        "Мұндай логин тіркелмеген!"
                    )


    # ---------------------------------
    # 8.2 ТІРКЕЛУ
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

            fullname = st.text_input(
                "Аты-жөні"
            )

            school = st.text_input(
                "Мектеп атауы"
            )

            if register_role == "Оқушы":

                detail = st.selectbox(
                    "Сыныбы",
                    [
                        f"{i}-сынып"
                        for i in range(7, 12)
                    ]
                )

            else:

                detail = st.text_input(
                    "Пәні"
                )

            register_username = st.text_input(
                "Логин"
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

            elif not detail.strip():

                st.warning(
                    "Пән немесе сыныпты таңдаңыз!"
                )

            elif not register_username.strip():

                st.warning(
                    "Логин енгізіңіз!"
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

                salt = secrets.token_hex(16)

                password_hash = hash_password(
                    register_password,
                    salt
                )

                conn = connect_db()

                try:

                    conn.execute(
                        """
                        INSERT INTO users (
                            fullname,
                            role,
                            school,
                            detail,
                            username,
                            password_hash,
                            salt
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            fullname.strip(),
                            register_role,
                            school.strip(),
                            detail.strip(),
                            register_username.strip(),
                            password_hash,
                            salt
                        )
                    )

                    conn.commit()

                    st.success(
                        "Тіркелу сәтті аяқталды! "
                        "Енді жүйеге кіре аласыз."
                    )

                except sqlite3.IntegrityError:

                    st.error(
                        "Бұл логин бұрын тіркелген. "
                        "Басқа логин таңдаңыз."
                    )

                finally:

                    conn.close()


# =====================================
# 9. ТӨМЕНГІ БӨЛІМ
# =====================================

st.divider()

st.markdown(
    """
    <p style="text-align:center;">
        FIZIKA QADAM © 2026
    </p>
    """,
    unsafe_allow_html=True
)
