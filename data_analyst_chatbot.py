import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

def validate_api_key(api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Test")
        return True
    except Exception as e:
        return False

def generate_response(prompt):
    try:
        response = st.session_state.model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="Data Analyst Assistant", page_icon="📊", layout="wide")
    st.title("Data Analyst Assistant Chatbot")

    # Check if API key is already stored in session state
    if 'api_key_validated' not in st.session_state:
        st.session_state.api_key_validated = False

    if not st.session_state.api_key_validated:
        st.write("Welcome! Please enter your Google Gemini API key to start.")
        api_key = st.text_input("Enter your API key", type="password")
        if st.button("Validate and Start"):
            if validate_api_key(api_key):
                st.session_state.api_key = api_key
                st.session_state.api_key_validated = True
                genai.configure(api_key=api_key)
                st.session_state.model = genai.GenerativeModel('gemini-pro')
                st.success("API key validated successfully!")
                st.rerun()
            else:
                st.error("Invalid API key. Please try again.")
    else:
        # Initialize session state for conversation history and responses
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'report_responses' not in st.session_state:
            st.session_state.report_responses = []
        if 'best_practices_responses' not in st.session_state:
            st.session_state.best_practices_responses = []
        if 'error_responses' not in st.session_state:
            st.session_state.error_responses = []

        # Sidebar for topic selection
        topic = st.sidebar.selectbox(
            "Select a topic",
            ["General", "SQL", "Python", "Power BI", "Data Handling"]
        )

        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Chat", "Quick Report", "Best Practices", "Error Handling"])

        with tab1:
            st.write(f"Current topic: {topic}")

            # User input
            user_input = st.chat_input("Ask your question here...")

            if user_input:
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": user_input})

                # Generate context-aware prompt
                context = f"You are a helpful Data Analyst Assistant. The current topic is {topic}. "
                context += "Provide step-by-step solutions, code snippets when relevant, and links to documentation. "
                context += "If the question is vague, ask for clarification. "
                context += "Here's the conversation history and the latest question:\n\n"

                for message in st.session_state.messages:
                    context += f"{message['role'].capitalize()}: {message['content']}\n"

                # Generate response
                full_response = generate_response(context)

                if full_response:
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

            # Display chat history
            for message in reversed(st.session_state.messages):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        with tab2:
            st.header("Generate Quick Report Outline")
            report_topic = st.text_input("Enter a specific topic for the report outline:",
                                         placeholder="E.g., Customer Churn Analysis, Sales Trend Forecasting")
            if st.button("Generate Outline", key="generate_outline"):
                if report_topic:
                    report_prompt = f"Generate a quick report outline for a data analysis task related to {report_topic} in the context of {topic}. Include common Exploratory Data Analysis (EDA) tasks and potential insights to look for."
                    report_outline = generate_response(report_prompt)
                    if report_outline:
                        st.session_state.report_responses.insert(0, (report_topic, report_outline))
                else:
                    st.warning("Please enter a specific topic for the report outline before clicking the button.")

            # Display report responses
            for i, (topic, response) in enumerate(st.session_state.report_responses):
                with st.expander(f"Report Outline: {topic}", expanded=(i == 0)):
                    st.write(response)

        with tab3:
            st.header("Best Practices and Optimization Tips")
            best_practices_input = st.text_input("What specific area or task do you want best practices for?",
                                                 placeholder="E.g., data cleaning in Python, SQL query optimization, Power BI dashboard design")
            if st.button("Get Best Practices", key="get_best_practices"):
                if best_practices_input:
                    best_practices_prompt = f"Provide detailed best practices and optimization tips for {best_practices_input} in the context of {topic} for data analysis. Include specific examples and explanations where relevant."
                    best_practices = generate_response(best_practices_prompt)
                    if best_practices:
                        st.session_state.best_practices_responses.insert(0, (best_practices_input, best_practices))
                else:
                    st.warning("Please enter a specific area or task for best practices before clicking the button.")

            # Display best practices responses
            for i, (query, response) in enumerate(st.session_state.best_practices_responses):
                with st.expander(f"Best Practices for: {query}", expanded=(i == 0)):
                    st.write(response)

        with tab4:
            st.header("Error Handling Assistance")
            error_description = st.text_area("Describe the error you're facing:")
            if st.button("Get Error Solution", key="get_error_solution"):
                if error_description:
                    error_prompt = f"The user is experiencing the following error in {topic}: {error_description}. Provide potential causes and fixes."
                    error_solution = generate_response(error_prompt)
                    if error_solution:
                        st.session_state.error_responses.insert(0, (error_description, error_solution))
                else:
                    st.warning("Please describe the error before clicking the button.")

            # Display error responses
            for i, (error, solution) in enumerate(st.session_state.error_responses):
                with st.expander(f"Error: {error[:50]}...", expanded=(i == 0)):
                    st.write("Error Description:")
                    st.write(error)
                    st.write("Potential Causes and Fixes:")
                    st.write(solution)

if __name__ == "__main__":
    main()