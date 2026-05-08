# =========================
# SIDEBAR
# =========================

from datetime import datetime
from export_chat import (
    export_as_txt,
    export_as_json,
    export_as_markdown
)


def create_sidebar(st):

    # Default prompts
    persona_prompts = {
        "Helpful Assistant": """
        You are a helpful AI assistant.
        Reply clearly and professionally.
        """,

        "Poetic Hindi Speaker": """
        You are a poetic AI assistant.
        Always reply in Hindi poetic style.
        """,

        "Python Expert": """
        You are a senior Python developer.
        Explain code in beginner friendly manner.
        """,

        "Cybersecurity Mentor": """
        You are an ethical hacking mentor.
        Explain cybersecurity concepts practically.
        """
    }

    with st.sidebar:

        st.title("⚙️ Settings")

        # Persona selection
        persona = st.selectbox(
            "Choose AI Persona",
            [
                "Helpful Assistant",
                "Poetic Hindi Speaker",
                "Python Expert",
                "Cybersecurity Mentor"
            ]
        )

        # System prompt
        system_prompt = st.text_area(
            "System Prompt",
            value=persona_prompts[persona],
            height=150
        )

        # Temperature slider
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1
        )

        # Max tokens slider
        max_tokens = st.slider(
            "Max Tokens",
            min_value=256,
            max_value=4096,
            value=2048,
            step=256
        )

        # Clear chat button
        if st.button("🗑️ Clear Chat"):

            st.session_state.messages = []

            st.rerun()

        # =========================
        # EXPORT CHAT
        # =========================

        st.divider()

        st.subheader("📥 Export Chat")

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        export_type = st.selectbox(
            "Select Export Format",
            [
                "TXT",
                "JSON",
                "Markdown"
            ]
        )

        match export_type:

            case "TXT":

                txt_content = export_as_txt(
                    st.session_state.messages
                )

                st.download_button(
                    "Download TXT",
                    data=txt_content,
                    file_name=f"chat_history_{timestamp}.txt",
                    mime="text/plain"
                )

            case "JSON":

                json_content = export_as_json(
                    st.session_state.messages
                )

                st.download_button(
                    "Download JSON",
                    data=json_content,
                    file_name=f"chat_history_{timestamp}.json",
                    mime="application/json"
                )

            case "Markdown":

                md_content = export_as_markdown(
                    st.session_state.messages
                )

                st.download_button(
                    "Download Markdown",
                    data=md_content,
                    file_name=f"chat_history_{timestamp}.md",
                    mime="text/markdown"
                )

    return system_prompt, temperature, max_tokens