from drf_spectacular.utils import extend_schema, OpenApiTypes, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema_view


class WebSocketDocsView(APIView):
    """
    API Documentation for WebSocket connection to chat.
    """

    @extend_schema(
        summary="WebSocket Connection for Chat",
        description="""
        **WebSocket URL:**  
        `ws://yourserver.com/ws/chat/?conversation_id=<CONVERSATION_ID>`&token=your_auth_token

        **WebSocket Actions:**
        - `CREATE_MESSAGE`: Send a new chat message.
        - `EDIT_MESSAGE`: Edit an existing message (within 5 minutes).
        - `TYPING_STATUS_ON`: Notify that the user is typing.
        - `TYPING_STATUS_OFF`: Notify that the user has stopped typing.

        - Send message
        **Message Format:**
        ```json
        {
            "action": "CREATE_MESSAGE",
            "data": {
                "content": "Hello, World!"
            }
        }
        ```

        **Response Format:**
        ```json
        {
            "message": {
                "id": 1,
                "sender": "user123",
                "content": "Hello, World!",
                "timestamp": "2024-03-08T12:34:56Z"
            },
            "action": "CREATE_MESSAGE"
        }
        ```
        - Edit Message
        
        
        **Message Format:**
        ```json
        {
            "action": "EDIT_MESSAGE",
            "data": {
                "message_id":"my_message_id",
                "content": "Hello, World!"
            }
        }
        ```

        **Response Format:**
        ```json
        {
            "message": {
                "id": 1,
                "sender": "user123",
                "content": "Hello, World!",
                "timestamp": "2024-03-08T12:34:56Z"
            },
            "action": "EDIT_MESSAGE"
        }
        
        - Typing ON
        
                **Message Format:**
        ```json
        {
            "action": "TYPING_STATUS_ON",
        }
        ```

        **Response Format:**
        ```json
       {
        "action": "TYPING_STATUS_ON",
        "sender": {
                    "id": "f9d363cc-1dba-4867-a7bd-2994dc8e7bee",
                    "first_name": "Mohan",
                    "last_name": "kumar",
                    "email": "mohan@accuknox.com"
       }
       
       
       - Typing OFF
        
                **Message Format:**
        ```json
        {
            "action": "TYPING_STATUS_OFF",
        }
        ```

        **Response Format:**
        ```json
       {
        "action": "TYPING_STATUS_OFF",
        "sender": {
                    "id": "f9d363cc-1dba-4867-a7bd-2994dc8e7bee",
                    "first_name": "Mohan",
                    "last_name": "kumar",
                    "email": "mohan@accuknox.com"
       }
}
        ```
        
        
        
        """,
        parameters=[
            OpenApiParameter(
                name="conversation_id",
                description="ID of the conversation to connect to WebSocket",
                required=True,
                type=OpenApiTypes.STR
            )
        ],
        responses={200: OpenApiTypes.OBJECT}
    )
    def get(self, request):
        """WebSocket documentation endpoint"""
        return Response({
            "message": "Refer to the documentation for WebSocket details."
        })
