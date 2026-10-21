import streamlit as st

from memory import Memory
from model import create_client
from run_Agent import run_agent


st.set_page_config(
    page_title="Research assistant",
    page_icon=":material/travel_explore:",
    layout="centered",
)

st.session_state.setdefault("chat_history", [])
if "agent_memory" not in st.session_state:
    st.session_state.agent_memory = Memory()

with st.sidebar:
    st.title("Your API")
    st.caption("These settings apply only to your current browser session.")
    api_key = st.text_input(
        "API key",
        type="password",
        placeholder="Enter your API key",
        help="Your key is used for requests from this session and is not saved to a file.",
    )
    base_url = st.text_input(
        "API base URL",
        value="https://api.openai.com/v1",
        help="Use your provider's OpenAI-compatible API endpoint.",
    )
    model_name = st.text_input(
        "Model",
        placeholder="e.g. gpt-4o-mini",
        help="Enter a model name supported by your API provider.",
    )
    test_connection = st.button(
        "Test API connection",
        type="primary",
        width="stretch",
        disabled=not api_key.strip() or not model_name.strip(),
    )
    st.caption("Compatible with OpenAI-style chat completions APIs.")

    if st.button("Clear conversation", width="stretch"):
        st.session_state.chat_history = []
        st.session_state.agent_memory = Memory()

if test_connection:
    try:
        client = create_client(api_key, base_url)
        client.chat.completions.create(
            model=model_name.strip(),
            messages=[{"role": "user", "content": "Reply with OK."}],
        )
        st.sidebar.success("Connection successful. The API returned a response.")
    except Exception as error:
        st.sidebar.error(f"Connection failed ({type(error).__name__}): {error}")

st.title("Research assistant")
st.write("Ask a question and let the assistant search and research the web for an answer.")

if not api_key.strip() or not model_name.strip():
    st.info("Add your API key and model in the sidebar to start a conversation.")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input(
    "Ask a question",
    disabled=not api_key.strip() or not model_name.strip(),
)

if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    st.session_state.agent_memory.add_memory("user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            client = create_client(api_key, base_url)
            with st.status("Working on your answer...", expanded=True) as status:
                response = run_agent(
                    st.session_state.agent_memory,
                    client,
                    model_name.strip(),
                    emit=lambda event_type, message: status.write(
                        f"**{event_type}** · {message}"
                    ),
                )
                if not isinstance(response, str) or not response.strip():
                    raise RuntimeError("The model returned an empty response.")
                status.update(label="Answer ready", state="complete", expanded=False)

            st.markdown(response)
            st.session_state.agent_memory.add_memory("assistant", response)
            st.session_state.chat_history.append(
                {"role": "assistant", "content": response}
            )
        except Exception as error:
            st.error(f"Request failed ({type(error).__name__}): {error}")
