import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title("Simple Streamlit Browser")

# Input for URL
url = st.text_input("Enter URL:", "https://www.google.com")

# Display the embedded content using an iframe
# if url:
#     st.components.v1.html(f'<iframe src="{url}" width="100%" height="600px"></iframe>', height=620)
# else:
#     st.info("Please enter a URL to display content.")


# Validate and fetch links
if url:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for bad responses

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')

        # Display the iframe
        st.components.v1.html(f'<iframe src="{url}" width="100%" height="600px"></iframe>', height=620)

        st.subheader("Links Found on Page")
        if links:
            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True) or href
                if href:
                    st.markdown(f"- [{text}]({href})")
        else:
            st.info("No links found on the page.")
    except Exception as e:
        st.error(f"Error fetching URL: {e}")
else:
    st.info("Please enter a URL to display content.")