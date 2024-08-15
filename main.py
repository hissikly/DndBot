import streamlit as st
import static.data as data
import recogniton as rc
import gigachat_models as ggm
from playback import record_text, play_record_text, play_audio
from streamlit_option_menu import option_menu


def set_option_menu():
    with st.sidebar:
        selected = option_menu("Меню", ["Главная", "Узнать больше про игру"],
                               icons=["play-btn", "play-btn"], menu_icon="intersect", default_index=0)
        return selected 


def space_main_sidebar():
    with st.sidebar:
        st.title("Dungeons & Dragons", )
        with st.form("my_form"):
            location = st.selectbox('Локация', data.locations.keys())
            state = st.selectbox("Выбор музыкальной атмосферы", data.states.keys())
            voice_type = st.selectbox("Выберите озвучку", data.voice_types.keys())
            button_box = st.form_submit_button("Задать", "primary")

            st.session_state.voice_type = voice_type

        change_title_button()
        play_audio(state, location)
        commands_buttons()

    return {"location": location, 
            "state": state, 
            "voice_type": voice_type, 
            "button_box": button_box}


def space_about_sidebar():
    with st.sidebar:
        st.title("Dungeons & Dragons", )
        option = st.selectbox(
            "Параметры",
            data.long_properties
        )

    return {"option": option}
        

def commands_buttons():
    _, col2, col3 = st.columns([1, 2, 3])
    with col2:
        st.button("/help", on_click=rules_button_event, args=("/help",))
        st.button("/rules", on_click=rules_button_event, args=("/rules",))
    with col3:
        st.button("/image",  on_click=rules_button_event, args=("/image",))
        st.button("/dialog",  on_click=rules_button_event, args=("/dialog",))


def change_title_button():
    if not st.session_state.voice_record_button:
        button_voice = st.button("Запись голоса", type="primary", on_click=voice_button_event, key="voice_button")
    elif st.session_state.voice_record_button:
        button_voice = st.button("Записываю", type="primary", on_click=stop_button_event, key="voice_button")
    return button_voice


def voice_button_event():
    st.session_state.voice_record_button = True
    default_text = record_voice()
    st.session_state.is_recorded_voice = True

    st.session_state.default_text = default_text


def rules_button_event(text: str):
    st.session_state.default_text = text


def monster_button_event(name: str):
    row = data.monsters[name == data.monsters["Unnamed: 0"]]

    desc = row["0"]
    markdowned = f"""**{name}**. {desc}  \n\n"""

    info_dict = data.get_info_dict("assistant", markdowned)
    show_messages_states(info_dict)
    st.session_state.messages.append(info_dict)


def property_button_event(key: str):
    stor = data.properties[key]
    markdowned = ""

    for key, val in stor.items():
        if val[-1] == ",":
            markdowned += f"""   **{key}**. {val[:-1]}  \n\n"""
        else:
            markdowned += f"""   **{key}**. {val}  \n\n"""

    info_dict = data.get_info_dict("assistant", markdowned)
    show_messages_states(info_dict)
    st.session_state.messages.append(info_dict)


def stop_button_event():
    st.session_state.voice_record_button = False


def record_voice():
    if st.session_state.voice_record_button:
        return rc.va_listen()
    return ""


def set_default_text():
    default_chat_input_value = st.session_state.default_text
    js = f"""
        <script>
            function insertText(dummy_var_to_force_repeat_execution) {{
                var chatInput = parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
                var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                nativeInputValueSetter.call(chatInput, "{default_chat_input_value}");
                var event = new Event('input', {{ bubbles: true}});
                chatInput.dispatchEvent(event);
            }}
            insertText({len(st.session_state.default_text)});
        </script>
        """
    st.components.v1.html(js)


def show_messages_states(info_dict: dict):
    role = info_dict["role"]
    response = info_dict["content"]
    
    if "command" in info_dict:
        command = info_dict["command"]
        path = info_dict["path"]
    else:
        command = None
        path = None

    with st.chat_message(role):
        st.markdown(response)

    if command == "speak":
        path = info_dict["path"]
        audio_file = open(path, "rb")
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/ogg")
    elif command == "image":
        path = info_dict["path"]
        st.image(path)

    return response, command, path


def set_states():
    if "is_fsm_dialog" not in st.session_state:
        st.session_state.is_fsm_dialog = False
    if "is_fsm_img" not in st.session_state:
        st.session_state.is_fsm_img = False
    if "generated_images" not in st.session_state:
        st.session_state.generated_images = []
    if 'voice_record_button' not in st.session_state:
        st.session_state.voice_record_button = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "audio_voices" not in st.session_state:
        st.session_state.audio_voices = []
    if "default_text" not in st.session_state:
        st.session_state.default_input_text = ""


def about():
    sidebar_dict = space_about_sidebar()
    option = sidebar_dict["option"]

    if option == "Монстры":
        monsters = data.monsters

        desc = data.markdowned_text(monsters)

        st.markdown("# Монстры")
        st.markdown(desc)

    elif option == "Снаряжение":
        equipment = data.equipment

        desc = data.markdowned_text(equipment)

        st.markdown("# Снаряжение")
        st.markdown(desc)

    elif option == "Особеннности":
        features = data.features

        desc = data.markdowned_text(features)

        st.markdown("# Особеннности")
        st.markdown(desc)

    elif option == "Магические предметы":
        magic_items = data.magic_items

        desc = data.markdowned_text(magic_items)

        st.markdown("# Магические предметы")
        st.markdown(desc)

    elif option == "Расы":
        races = data.races

        desc = data.markdowned_text(races)

        st.markdown("# Расы")
        st.markdown(desc)

    elif option == "Заклинания":
        spells = data.spells

        desc = data.markdowned_text(spells)

        st.markdown("# Заклинания")
        st.markdown(desc)


def main():
    st.title("Support Hissie Bot")

    set_states()

    sidebar_dict = space_main_sidebar()
    voice_type = sidebar_dict["voice_type"]

    for message_dict in st.session_state.messages:
        show_messages_states(message_dict)
    
    if "default_text" in st.session_state and st.session_state.default_text:
        set_default_text()
        st.session_state.default_text = ""


    if prompt := st.chat_input("/help - посмотреть, что умеет бот",):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        if prompt.strip().lower() == "/help":
            info_dict = data.get_info_dict("assistant", f"Прародитель:\n {data.help_answer}")
            show_messages_states(info_dict)
            st.session_state.messages.append(info_dict)

        elif st.session_state.is_fsm_dialog:
            if prompt.strip().lower() == "стоп":
                info_dict = data.get_info_dict("assistant", "Прародитель:\n Режим диалога деактивирован")
                show_messages_states(info_dict)
                
                st.session_state.messages.append(info_dict)
                st.session_state.is_fsm_dialog = False
            else:
                try:
                    voice_number = data.get_count_in_folder("static/music/voice/") + 1
                    path_to_voice = f"voice/voice{voice_number}.mp3"
                    llm_answer = ggm.get_message_by_gigachain(st.session_state.messages, prompt)

                    output_path = record_text(llm_answer, data.voice_types[voice_type], path=path_to_voice)["detail"]
                    info_dict = data.get_info_dict("assistant", llm_answer, command="speak", path=output_path)

                    show_messages_states(info_dict)
                    
                    st.session_state.messages.append(info_dict)
                except:
                    info_dict = data.get_info_dict("assistant", data.smth_wrong_replic)
                    show_messages_states(info_dict)
                    st.session_state.messages.append(info_dict)

        elif st.session_state.is_fsm_img:
            if prompt.strip().lower() == "стоп":
                info_dict = data.get_info_dict("assistant", "Прародитель:\n Генерация изображения остановлена")
                show_messages_states(info_dict)
                
                st.session_state.messages.append(info_dict)
            else:
                try:
                    _, path_to_generated_img = ggm.get_image_by_gigachain(prompt)
                    info_dict = data.get_info_dict("assistant", "Прародитель:\n", "image", path_to_generated_img)
                    show_messages_states(info_dict)
                    st.session_state.messages.append(info_dict)
                except:
                    info_dict = data.get_info_dict("assistant", data.smth_wrong_replic)
                    show_messages_states(info_dict)
                    st.session_state.messages.append(info_dict)

            st.session_state.is_fsm_img = False
    
        elif prompt.strip().lower() == "/image":
            info_dict = data.get_info_dict("assistant", f"Прародитель:\n Опишите то, что вы хотите увидеть на картинке. Генерация займет какое-то время. Для отмены генерации напишите 'стоп'")
            show_messages_states(info_dict)
            st.session_state.messages.append(info_dict)

            st.session_state.is_fsm_img = True

        elif prompt.strip().lower() == "/dialog":
            info_dict = data.get_info_dict("assistant","Прародитель:\n Активирован режим диалога, если хотите остановить, напишите 'стоп'")
            show_messages_states(info_dict)
            st.session_state.messages.append(info_dict)

            st.session_state.is_fsm_dialog = True

        elif prompt.strip().lower() == "/rules":
            info_dict = data.get_info_dict("assistant","Прародитель:\n Выберите интересующий раздел:")
            
            show_messages_states(info_dict)
            st.session_state.messages.append(info_dict)
            n_cols = (len(data.properties) + 1) // 4

            cols = st.columns([1] * n_cols)
            for i, (key, _) in enumerate(data.properties.items()):
                with cols[i // 4]:
                    st.button(key, on_click=property_button_event, args=(key,))


        elif prompt.strip().startswith("/"):
            info_dict = data.get_info_dict("assistant", "Прародитель:\n Такой команды нет... /help для просмотра списка команд")
            show_messages_states(info_dict)
            st.session_state.messages.append(info_dict)

        else:
            try:
                response = f"Прародитель:\n {prompt}"
                with st.chat_message("assistant"):
                    st.markdown(response)
                path_to_voice = play_record_text(voice_type, prompt)
                st.session_state.messages.append({"role": "assistant", "content": response, "command": "speak", "path": path_to_voice})
            except:
                st.session_state.messages.append({"role": "assistant", "content": data.smth_wrong_replic})
    

if __name__ == "__main__":
    selected = set_option_menu()

    if selected == "Главная":
        main()
    else:
        about()