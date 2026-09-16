import streamlit as st

from rag import answer_question, collection


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="GIAN Knowledge Base",
    page_icon="🔎",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        margin-bottom: 25px;
    }

    .source-card {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #dddddd;
        margin-bottom: 10px;
    }

    .answer-box {
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #dddddd;
        margin-top: 15px;
    }

    .small-text {
        font-size: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">🔎 GIAN Knowledge Base</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    Multi-Source Retrieval-Augmented Generation (RAG) Assistant
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("📚 Knowledge Base")

    st.write(
        "This system retrieves information from multiple "
        "GIAN-related sources."
    )


    st.divider()


    st.subheader("Sources")

    st.write("📄 51st Shodhyatra")

    st.write("📄 53rd Shodhyatra")

    st.write("🔗 Shodhyatra relationships")

    st.write("📊 GIAN Nidhi")


    st.divider()


    st.subheader("System")

    st.metric(
        "Knowledge Base Records",
        collection.count()
    )

    st.write(
        "**Vector DB:** ChromaDB"
    )

    st.write(
        "**Embedding:** "
        "paraphrase-multilingual-MiniLM-L12-v2"
    )

    st.write(
        "**LLM:** "
        "Groq / openai/gpt-oss-20b"
    )


# ============================================================
# INTRODUCTION
# ============================================================

st.markdown(
    """
    ### Ask the Knowledge Base

    Ask questions about innovators, innovations, projects,
    participants, colleges, relationships, and information
    contained in the available sources.

    The system retrieves evidence from the knowledge base
    before generating an answer.
    """
)


# ============================================================
# EXAMPLE QUESTIONS
# ============================================================

st.subheader("💡 Example Questions")

example_questions = [

    "Who developed the thornless Khejri technique?",

    "Who developed the water-and-electricity welding machine?",

    "What is project ID 640?",

    "Which project is associated with Belgi Akanksha Manoj?",

    "Which projects are associated with Government Polytechnic Miraj?"
]


cols = st.columns(2)


for index, example in enumerate(
    example_questions
):

    with cols[index % 2]:

        if st.button(
            example,
            key=f"example_{index}",
            use_container_width=True
        ):

            st.session_state[
                "question"
            ] = example


# ============================================================
# QUESTION INPUT
# ============================================================

st.subheader("🔍 Ask a Question")

with st.form("question_form"):

    question = st.text_input(
        "Enter your question:",
        value=st.session_state.get(
            "question",
            ""
        ),
        placeholder=(
            "Example: Who developed the thornless Khejri technique?"
        )
    )

    ask_button = st.form_submit_button(
        "🚀 Ask Knowledge Base",
        use_container_width=True
    )


# ============================================================
# PROCESS QUESTION
# ============================================================

if ask_button:

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        # ----------------------------------------------------
        # Loading indicator
        # ----------------------------------------------------

        with st.spinner(
            "Searching the knowledge base and generating answer..."
        ):

            try:

                answer = answer_question(
                    question
                )


                # =================================================
                # ANSWER
                # =================================================

                st.divider()

                st.subheader(
                    "💬 Answer"
                )


                with st.container(border=True):

                    st.markdown(answer)


                # =================================================
                # SOURCE INFORMATION
                # =================================================

                st.divider()

                st.subheader(
                    "📌 Source Traceability"
                )


                st.info(
                    """
                    The answer above was generated from
                    retrieved knowledge-base evidence.

                    Source attribution and record/page
                    information are displayed in the
                    terminal retrieval log.
                    """
                )


            except Exception as e:

                st.error(
                    "An error occurred while processing "
                    "the question."
                )


                st.exception(
                    e
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "GIAN Multi-Source Knowledge Base | "
    "ChromaDB + Sentence Transformers + Groq"
)