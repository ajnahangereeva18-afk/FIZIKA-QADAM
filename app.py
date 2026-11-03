
import streamlit as st

st.set_page_config(
    page_title="FIZIKA QADAM",
    page_icon="⚛️",
    layout="wide"
)

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

login, register = st.tabs([
    "🔐 Жүйеге кіру",
    "📝 Тіркелу"
])

with login:
    st.subheader("Жеке кабинетке кіру")

    role = st.selectbox(
        "Қолданушы түрі",
        ["Оқушы", "Мұғалім"]
    )
   username = st.text_input("Логин", key="login_username")

with login:
    st.subheader("Жеке кабинетке кіру")

    role = st.selectbox(
        "Қолданушы түрі",
        ["Оқушы", "Мұғалім"],
        key="login_role"
    )

    username = st.text_input(
        "Логин",
        key="login_username"
    )

    password = st.text_input(
        "Құпиясөз",
        type="password",
        key="login_password"
    )

    st.button("КІРУ")

with register:
    st.subheader("Жаңа аккаунт ашу")

    role = st.radio(
        "Тіркелу түрі",
        ["Оқушы", "Мұғалім"],
        horizontal=True
    )

   with register:
    st.subheader("Жаңа аккаунт ашу")

    role = st.radio(
        "Тіркелу түрі",
        ["Оқушы", "Мұғалім"],
        horizontal=True,
        key="register_role"
    )

    fullname = st.text_input("Аты-жөні", key="fullname")
    school = st.text_input("Мектеп атауы", key="school")

    if role == "Оқушы":
        detail = st.selectbox(
            "Сыныбы",
            [f"{i}-сынып" for i in range(7, 12)],
            key="grade"
        )
    else:
        detail = st.text_input("Пәні", key="subject")

    username = st.text_input("Логин", key="register_username")

    password = st.text_input(
        "Құпиясөз",
        type="password",
        key="register_password"
    )

    st.button("ТІРКЕЛУ")

st.divider()

st.markdown(
    "<p style='text-align:center'>"
    "FIZIKA QADAM © 2026"
    "</p>",
    unsafe_allow_html=True
)
