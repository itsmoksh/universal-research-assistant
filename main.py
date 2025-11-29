import streamlit as st
from rag import process_urls,generate,reset_
st.title("Universal Research Assistant")

if "initialized" not in st.session_state:
    reset_vector_store()        # <<< reset happens here, and ONLY once
    st.session_state.initialized = True

#Url sidebar
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

#Showing previous conversations.
if 'message' not in st.session_state:
    st.session_state['message'] = []

for message in st.session_state['message']:
    if message['role'] == 'User':
        with st.chat_message(name = 'User'):
            st.caption("Query")
            st.markdown(message['query'])

    else:
        with st.chat_message(name = 'Assistant'):
            if 'result' in message:
                st.caption("Solution")
                st.markdown(message['result'])
            if 'source' in message:
                st.caption("Sources")
                st.markdown(message['source'])

# Generating results
if prompt:
    try:
        solution, sources = generate(prompt)
        with st.chat_message(name = "User"):
            st.caption("Query")
            st.markdown(prompt)
        st.session_state.message.append({'role':"User", 'query': prompt})
        with st.chat_message(name = 'Assistant'):
            st.caption("Solution")
            st.markdown(solution)
            if sources:
                st.caption("Source")
                unique_source = set(sources)
                for source in unique_source:
                    st.markdown(source)
        st.session_state.message.append({'role': "Assistant", 'result': solution})
        st.session_state.message.append({'role': "Assistant", 'source': source})

    except RuntimeError as e:
        st.error("You must process the url first")


