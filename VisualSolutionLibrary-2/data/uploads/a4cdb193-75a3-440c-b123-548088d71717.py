import streamlit as st
import json
import os

DATA_FILE = "solutions.json"

# Загрузка данных
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {"tasks": [], "solutions": []}

# Функция сохранения
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

st.set_page_config(page_title="Визуальная библиотека решений", layout="wide")
st.title("📚 Визуальная библиотека студенческих решений")

# --- Вкладки интерфейса ---
tab1, tab2, tab3 = st.tabs(["📋 Задания", "➕ Новое решение", "👁 Просмотр решений"])

# === Вкладка 1: Список заданий ===
with tab1:
    st.subheader("Задания")
    if data["tasks"]:
        for task in data["tasks"]:
            st.markdown(f"**{task['title']}**\n\n{task['description']}")
    else:
        st.info("Задания пока не добавлены.")

    with st.expander("➕ Добавить задание"):
        title = st.text_input("Название задания")
        desc = st.text_area("Описание задания")
        if st.button("Добавить задание"):
            data["tasks"].append({"id": len(data["tasks"]) + 1, "title": title, "description": desc})
            save_data()
            st.success("Задание добавлено!")

# === Вкладка 2: Добавление решения ===
with tab2:
    st.subheader("Новое решение")

    if not data["tasks"]:
        st.warning("Сначала добавьте хотя бы одно задание.")
    else:
        task_titles = [f"{t['id']}: {t['title']}" for t in data["tasks"]]
        selected_task = st.selectbox("Выберите задание", task_titles)
        task_id = int(selected_task.split(":")[0])
        author = st.text_input("Имя студента")
        steps_text = st.text_area("Решение (разделяйте шаги пустой строкой)")

        if st.button("Сохранить решение"):
            steps = [s.strip() for s in steps_text.strip().split("\n") if s.strip()]
            data["solutions"].append({
                "task_id": task_id,
                "author": author,
                "steps": steps
            })
            save_data()
            st.success("Решение сохранено!")

# === Вкладка 3: Просмотр решений ===
with tab3:
    st.subheader("Просмотр решений")
    if not data["solutions"]:
        st.info("Решения ещё не добавлены.")
    else:
        task_map = {t["id"]: t["title"] for t in data["tasks"]}
        selected_task = st.selectbox("Выберите задание", list(task_map.items()), format_func=lambda x: x[1])
        task_id = selected_task[0]
        filtered = [s for s in data["solutions"] if s["task_id"] == task_id]

        if filtered:
            selected_author = st.selectbox("Выберите студента", [s["author"] for s in filtered])
            solution = next(s for s in filtered if s["author"] == selected_author)

            st.markdown(f"### 👨‍🎓 {selected_author}")
            st.markdown(f"Задание: **{task_map[task_id]}**")

            step = st.slider("Шаг", 1, len(solution["steps"]), 1)
            st.info(solution["steps"][step - 1])
        else:
            st.info("Пока нет решений по этому заданию.")