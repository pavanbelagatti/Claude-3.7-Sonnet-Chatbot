from anthropic import Anthropic
from config import IDENTITY, TOOLS, MODEL, get_quote
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ChatBot:
    def __init__(self, session_state):
        """Initialize the ChatBot with Anthropic client and session state."""
        # Initialize Anthropic client with API key from environment variables
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        # Store session state for conversation history
        self.session_state = session_state

    def generate_message(self, messages, max_tokens):
        """Generate a response from Claude using the provided messages."""
        try:
            # Call the Anthropic API to generate a response
            response = self.anthropic.messages.create(
                model=MODEL,
                system=IDENTITY,
                max_tokens=max_tokens,
                messages=messages,
                tools=TOOLS,
            )
            return response
        except Exception as e:
            # Return error message if API call fails
            return {"error": str(e)}

    def process_user_input(self, user_input):
        """Process user input, handle tool use, and return response."""
        # Add user message to conversation history
        self.session_state.messages.append({"role": "user", "content": user_input})

        # Generate initial response from Claude
        response_message = self.generate_message(
            messages=self.session_state.messages,
            max_tokens=2048,
        )

        # Handle errors in the response
        if isinstance(response_message, dict) and "error" in response_message:
            return f"An error occurred: {response_message['error']}"

        # Check if response contains a tool use request
        if response_message.content and response_message.content[-1].type == "tool_use":
            # Extract tool use details
            tool_use = response_message.content[-1]
            func_name = tool_use.name
            func_params = tool_use.input
            tool_use_id = tool_use.id

            # Execute the tool and get result
            result = self.handle_tool_use(func_name, func_params)
            
            # Add assistant response with tool use to conversation history
            self.session_state.messages.append(
                {"role": "assistant", "content": response_message.content}
            )
            
            # Add tool result to conversation history
            self.session_state.messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": f"{result}",
                }],
            })

            # Generate follow-up response from Claude after tool use
            follow_up_response = self.generate_message(
                messages=self.session_state.messages,
                max_tokens=2048,
            )

            # Handle errors in follow-up response
            if isinstance(follow_up_response, dict) and "error" in follow_up_response:
                return f"An error occurred: {follow_up_response['error']}"

            # Extract text from follow-up response
            response_text = follow_up_response.content[0].text
            
            # Add assistant follow-up response to conversation history
            self.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )
            return response_text
        
        elif response_message.content and response_message.content[0].type == "text":
            # Extract text from response if no tool use
            response_text = response_message.content[0].text
            
            # Add assistant response to conversation history
            self.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )
            return response_text
        
        else:
            # Handle unexpected response type
            raise Exception("An error occurred: Unexpected response type")

    def handle_tool_use(self, func_name, func_params):
        """Handle tool use requests from Claude."""
        # Process get_quote tool
        if func_name == "get_quote":
            premium = get_quote(**func_params)
            return f"Quote generated: ${premium:.2f} per month"
        
        # Handle unexpected tool use
        raise Exception(f"An unexpected tool was used: {func_name}")