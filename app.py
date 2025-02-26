import streamlit as st
from chatbot import ChatBot
from config import TASK_SPECIFIC_INSTRUCTIONS

def main():
    """Main function to run the Streamlit app."""
    # Set page title and configure layout
    st.set_page_config(
        page_title="Sunny Insurance Assistant",
        page_icon="🤖",
        layout="centered"
    )
    
    # Add header with logo and title
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("# 🤖")
    with col2:
        st.title("Sunny Insurance Assistant")
    
    st.markdown("---")
    
    # Initialize session state for storing conversation history
    if "messages" not in st.session_state:
        # Start with initial messages that provide context to Claude
        # but are hidden from the user
        st.session_state.messages = [
            {'role': "user", "content": TASK_SPECIFIC_INSTRUCTIONS},
            {'role': "assistant", "content": "Understood"},
        ]
        # Add welcome message
        st.session_state.messages.append(
            {'role': "assistant", "content": "Hello! I'm Eva, your virtual assistant from Sunny Insurance. How can I help you today?"}
        )

    # Create ChatBot instance
    chatbot = ChatBot(st.session_state)

    # Display conversation history (skipping the initial context messages)
    for message in st.session_state.messages[2:]:
        # Skip messages with complex content (like tool use)
        if isinstance(message["content"], str):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input for user
    if user_msg := st.chat_input("Type your message here..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_msg)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Eva is thinking..."):
                # Process user input and get response
                response_placeholder = st.empty()
                full_response = chatbot.process_user_input(user_msg)
                response_placeholder.markdown(full_response)

    # Add a sidebar with information about the assistant
    with st.sidebar:
        st.header("About Eva")
        st.markdown("""
        Eva is an AI assistant for Sunny Insurance. She can help you with:
        - Information about insurance products
        - Getting insurance quotes
        - General questions about Sunny Insurance
        """)
        
        st.markdown("---")
        
        st.markdown("**Contact Sunny Insurance**")
        st.markdown("📞 1-800-123-4567")
        st.markdown("⏰ Monday-Friday, 9 AM - 5 PM EST")

if __name__ == "__main__":
    main()