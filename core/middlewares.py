from django.utils.deprecation import MiddlewareMixin
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from channels.db import database_sync_to_async

class WSAuthenticationCheckMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.token_auth = TokenAuthentication()

    async def __call__(self, scope, receive, send):
        # Extract the token from the scope (e.g., from query parameters or headers)
        query_string = scope.get('query_string', b'').decode('utf-8')
        query_params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
        token = query_params.get('token', None)

        if token:
            try:
                # Authenticate the user using the token
                user, _ = await database_sync_to_async(self.token_auth.authenticate_credentials)(token)
                scope['user'] = user  # Add the user to the scope
            except AuthenticationFailed as e:
                # Handle authentication failure
                await send({
                    'type': 'websocket.close',
                    'code': 4001,  # Custom WebSocket close code
                    'reason': str(e),  # Send the authentication error message
                })
                return  # Stop further processing
        else:
            # No token provided
            await send({
                'type': 'websocket.close',
                'code': 4002,  # Custom WebSocket close code
                'reason': 'Authentication token not provided.',
            })
            return  # Stop further processing

        # Call the next middleware or the consumer
        return await self.get_response(scope, receive, send)