import os
import openai
from datetime import datetime
from api.models.chat import ChatMessage, ChatRequest, ChatResponse


class ChatService:
    def __init__(self):
        self.api_key = os.getenv("SWISS_AI_PLATFORM_API_KEY")
        if not self.api_key:
            raise ValueError("SWISS_AI_PLATFORM_API_KEY environment variable is required")

        self.client = openai.OpenAI(
            api_key=self.api_key, base_url="https://api.swisscom.com/layer/swiss-ai-weeks/apertus-70b/v1"
        )

    async def get_chat_response(self, request: ChatRequest) -> ChatResponse:
        """Get a response from the Apertus 70B model via Swisscom API"""

        # Prepare messages for the API
        messages = [
            {
                "role": "system",
                "content": "You are a financial analyst AI assistant. You help users with investment decisions, portfolio analysis, and financial insights. Be professional, data-driven, and provide actionable advice.",
            }
        ]

        # Add chat history
        for msg in request.chat_history:
            messages.append({"role": msg.role, "content": msg.content})

        # Add the new user message
        messages.append({"role": "user", "content": request.message})

        try:
            # Make the API call
            response = self.client.chat.completions.create(
                model="swiss-ai/Apertus-70B", messages=messages, max_tokens=1000, temperature=0.7
            )

            # Extract the response
            assistant_message = response.choices[0].message.content

            # Create new chat history with the conversation
            new_chat_history = request.chat_history.copy()
            new_chat_history.append(ChatMessage(role="user", content=request.message, timestamp=datetime.now()))
            new_chat_history.append(ChatMessage(role="assistant", content=assistant_message, timestamp=datetime.now()))

            return ChatResponse(message=assistant_message, chat_history=new_chat_history)

        except Exception as e:
            # Return an error response
            error_message = f"Sorry, I encountered an error: {str(e)}"
            new_chat_history = request.chat_history.copy()
            new_chat_history.append(ChatMessage(role="user", content=request.message, timestamp=datetime.now()))
            new_chat_history.append(ChatMessage(role="assistant", content=error_message, timestamp=datetime.now()))

            return ChatResponse(message=error_message, chat_history=new_chat_history)


# Create a singleton instance
chat_service = ChatService()
