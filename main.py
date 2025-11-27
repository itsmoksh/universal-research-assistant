import streamlit as st
from rag import process_urls,generate
st.title("Universal Research Assistant")

st.sidebar.subheader("Enter Url's")
url1 = st.sidebar.text_input("URL 1")
url2 = st.sidebar.text_input("URL 2")
url3 = st.sidebar.text_input("URL 3")

process_urls_button = st.sidebar.button("Process Urls")

if process_urls_button:
    urls = [url for url in [url1,url2,url3] if url!=""]

    if len(urls) == 0:
        st.error("No Urls entered, enter url to continue")

    else:
        with st.status("Storing Url content",expanded=True) as status:
            for url_status in process_urls(urls):
                st.write(url_status)
            status.update(label = "Chunks stored, now you can ask questions",expanded = False)

prompt = st.chat_input("Ask your Question")
if prompt:
    try:
        solution, sources = generate(prompt)
        with st.chat_message(name = "Assistant",avatar=None):
            st.subheader("Question")
            st.write(prompt)
            st.subheader("Answer:")
            st.write(solution)
            if sources:
                st.subheader("Source:")
                unique_source = set(sources)
                for source in unique_source:
                    st.write(source)

    except RuntimeError as e:
        st.error("You must process the url first")


