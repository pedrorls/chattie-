'''Views for the chat app.'''

from django.contrib.auth import get_user_model
from .models import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


class ChatSessionView(APIView):
    '''Manage chat sessions.'''
    permissions_classes = (permissions.IsAuthenticated)

    def post(self, request, *args, **kwargs):
        '''create a new chat session.'''
        user = request.user
        chat_session = ChatSession.objects.create(owner=user)
        return Response({
            'status': 'SUCCESS', 'uri': chat_session.uri,
            'message': 'New chat session created'
        })

    def patch(self, request, *args, **kwargs):
        '''Add a user to a chat session'''
        User = get_user_model()
        uri = kwargs['uri']
        username = request.data['username']
        user = User.objects.get(username=username)
        chate_session = ChatSession.objects.get(uri=uri)
        owner = chate_session.owner

        if owner != user:
            chate_session.members.get_or_create(
                user=user, chate_session=chate_session
            )

        owner = deserialize_user(owner)
        members = [
            deserialize_user(chate_session.user)
            for chate_session in chate_session.members.all()
        ]
        members.insert(0, owner)
        return Response({
            'status': 'SUCCESS', 'members': members,
            'message': '%s joined that chat' % user.username,
            'user': deserialize_user(user)
        })


class ChatSessionMessageView(APIView):
    '''create or get chat session messages.'''
    def get(self, request, *args, **kwargs):
        '''return all messages in a chat session'''
        uri = kwargs['uri']
        chat_session = ChatSession.objects.get(uri=uri)
        messages = [
            chat_session_message.to_json()
            for chat_session_message in chat_session.message.all()
        ]
        return Response({
            'id': chat_session.id, 'uri': chat_session.uri,
            'messages': messages
        })

    def post(self, request, *args, **kwargs):
        '''create a new message in a chat session.'''
        uri = kwargs['uri']
        message = request.data['message']
        user = request.user
        chat_session = ChatSession.objects.get(uri=uri)
        ChatSessionMessage.objects.create(
            user=user, chat_session=chat_session, message=message
        )
        return Response({
            'status': 'SUCCESS', 'uri': chat_session.uri, 'message': message,
            'user': deserialize_user(user)
        })
