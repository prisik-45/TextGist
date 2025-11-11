import streamlit as st
import requests
import io


st.set_page_config(
    page_title="Text-GIST",
    page_icon="📝",
    layout="wide"
)

API_URL = "http://localhost:8000/summarize"

st.title("Text-GIST")
st.markdown("Summarize faster read better")
st.markdown("---")


col1, col2  = st.columns(2)

with col1:
    st.header("Input")

    tab1, tab2, tab3 = st.tabs(["Text Input", "Upload Document", "Website URL"])

    with tab1:
        text_input = st.text_area(
            "Paste your text here:", 
            height=300, 
            placeholder="Enter the full text you want to summarize...",
            label_visibility="collapsed"
        )
    
    with tab2:
        uploaded_file = st.file_uploader(
            "Upload a PDF or DOCX file",
            type=['pdf', 'docx'],
            accept_multiple_files=False
        )
        st.caption("Supported formats: .pdf, .docx")

    with tab3:
        url_input = st.text_input(
            "Enter the website URL:", 
            placeholder="https://example.com/article"
        )


    st.markdown("---")
    st.markdown("Summary Length")
  
    summary_length = st.radio(
        "Select Summary length:",
        ('Short', 'Medium', 'Long'),
        index=1,  
        horizontal=True,
        label_visibility="collapsed"
    ).lower()

   
    summarize_button = st.button("Generate Summary", use_container_width=True)


with col2:
    st.header("Summary")
    
    
    if 'summary_text' not in st.session_state:
        st.session_state.summary_text = ""
    if 'word_count' not in st.session_state:
        st.session_state.word_count = 0


    if summarize_button:
       
        data = {"summary_length": summary_length}
        files = None
        input_provided = False

     
        if text_input.strip():
            data['text_input'] = text_input
            input_provided = True
        
        
        elif uploaded_file is not None:
            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            input_provided = True
        
     
        elif url_input.strip():
            data['url'] = url_input
            input_provided = True
        
        if input_provided:
            with st.spinner("Summarizing... Please wait."):
                try:
                    response = requests.post(API_URL, data=data, files=files, timeout=90)
                    
                    if response.status_code == 200:
                        result = response.json()
                        summary = result.get("summary", "No summary content returned.")
                        st.session_state.summary_text = summary
                        st.session_state.word_count = len(summary.split())
                    
                    else:
                        error_detail = response.json().get('detail', 'An unknown error occurred.')
                        st.error(f"Error from API: {error_detail}")
                        st.session_state.summary_text = ""
                        st.session_state.word_count = 0

                except requests.exceptions.ConnectionError:
                    st.error("Connection Error")
                    st.session_state.summary_text = ""
                    st.session_state.word_count = 0
                except requests.exceptions.Timeout:
                    st.error("Timeout Error")
                    st.session_state.summary_text = ""
                    st.session_state.word_count = 0
                except Exception as e:
                    st.error(f"Unknown error : {e}")
                    st.session_state.summary_text = ""
                    st.session_state.word_count = 0
        else:
            st.warning("Please provide some content")
            st.session_state.summary_text = ""
            st.session_state.word_count = 0

    st.text_area(
        "Generated Summary:",
        value=st.session_state.summary_text,
        height=400,
        disabled=True,
        label_visibility="visible"
    )
    if st.session_state.word_count > 0:
        st.caption(f"Word count: {st.session_state.word_count}")
