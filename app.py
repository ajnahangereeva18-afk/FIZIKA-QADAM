
import streamlit as st
import sqlite3
import hashlib
import secrets

st.set_page_config(
    page_title="FIZIKA QADAM",
    page_icon="⚛️",
    layout="wide"
)

# Деректер базасы
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

# Құпиясөзді хэштеу
def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        bytes.fromhex(salt),
        200000
    ).hex()

# Дизайн
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#101d36,#173c60);
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
}
</style>
""", unsafe_allow_html=True)

# Жүйеге кірген қолданушы
if "user" not in st.session_state:
    st.session_state.user = None

# Басты тақырып
st.markdown(
    "<h1 style='text-align:center'>⚛️ FIZIKA QADAM</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center'>"
    "Физикалық есептерді шешудің адаптивті цифрлық платформасы"
    "</p>",
    unsafe_allow_html=True
)

st.divider()

# Егер қолданушы жүйеге кірсе
if st.session_state.user:

    user = st.session_state.user

    st.success(f"Қош келдіңіз, {user['fullname']}!")

    if user["role"] == "Оқушы":
        st.title("🎓 Оқушы кабинеті")
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
        st.title("👩‍🏫 Мұғалім кабинеті")
        st.write(f"Мектеп: {user['school']}")
        st.write(f"Пәні: {user['detail']}")

        st.subheader("Мұғалім мүмкіндіктері")

        st.info("👥 Оқушыларды басқару")
        st.info("📝 Тапсырмалар беру")
        st.info("📊 Оқушылардың нәтижелерін бақылау")

    if st.button("ЖҮЙЕДЕН ШЫҒУ"):
        st.session_state.user = None
        st.rerun()

# Егер жүйеге кірмесе
else:

    login_tab, register_tab = st.tabs([
        "🔐 Жүйеге кіру",
        "📝 Тіркелу"
    ])

    # Жүйеге кіру
    with login_tab:

        st.subheader("Жеке кабинетке кіру")

        with st.form("login_form"):

            username = st.text_input("Логин")
            password = st.text_input(
                "Құпиясөз",
                type="password"
            )

            login_button = st.form_submit_button("КІРУ")

        if login_button:

            conn = connect_db()

            user = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            ).fetchone()

            conn.close()

            if user:
                saved_hash = user[6]
                salt = user[7]

                entered_hash = hash_password(password, salt)

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
                    st.error("Құпиясөз дұрыс емес!")

            else:
                st.error("Мұндай логин тіркелмеген!")

    # Тіркелу
    with register_tab:

        st.subheader("Жаңа аккаунт ашу")

        role = st.radio(
            "Тіркелу түрі",
            ["Оқушы", "Мұғалім"],
            horizontal=True
        )

        with st.form("register_form"):

            fullname = st.text_input("Аты-жөні")
            school = st.text_input("Мектеп атауы")

            if role == "Оқушы":
                detail = st.selectbox(
                    "Сыныбы",
                    [f"{i}-сынып" for i in range(7, 12)]
                )
            else:
                detail = st.text_input("Пәні")

            username = st.text_input("Логин")

            password = st.text_input(
                "Құпиясөз",
                type="password"
            )

            confirm_password = st.text_input(
                "Құпиясөзді қайталаңыз",
                type="password"
            )

            register_button = st.form_submit_button("ТІРКЕЛУ")

        if register_button:

            if not all([
                fullname.strip(),
                school.strip(),
                detail.strip(),
                username.strip(),
                password
            ]):
                st.warning("Барлық өрісті толтырыңыз!")

            elif len(password) < 8:
                st.warning(
                    "Құпиясөз кемінде 8 таңбадан тұруы керек!"
                )

            elif password != confirm_password:
                st.error("Құпиясөздер сәйкес келмейді!")

            else:
                salt = secrets.token_hex(16)
                password_hash = hash_password(password, salt)

                conn = connect_db()

                try:
                    conn.execute("""
                        INSERT INTO users
                        (fullname, role, school, detail,
                         username, password_hash, salt)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        fullname.strip(),
                        role,
                        school.strip(),
                        detail.strip(),
                        username.strip(),
                        password_hash,
                        salt
                    ))

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

st.divider()

st.markdown(
    "<p style='text-align:center'>"
    "FIZIKA QADAM © 2026"
    "</p>",
    unsafe_allow_html=True
)
