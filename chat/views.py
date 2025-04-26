from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import ChatRoom, ChatMessage
import uuid
import cloudinary
import cloudinary.uploader

@login_required
def chat_home(request):
    # Get all chat rooms for the current user
    chat_rooms = ChatRoom.objects.filter(users=request.user).order_by('-updated_at')

    # Add other_user and message info to each chat room
    for room in chat_rooms:
        room.other_user = room.users.exclude(id=request.user.id).first()
        # Get the last message for this room
        last_message = ChatMessage.objects.filter(room_name=room.name).order_by('-created_at').first()
        room.last_message = last_message
        # Count unread messages
        room.unread_count = ChatMessage.objects.filter(room_name=room.name, is_read=False).exclude(sender=request.user).count()

    # Get all users for the new conversation modal
    # Exclude the current user and users they already have conversations with
    existing_chat_users = User.objects.filter(chat_rooms__in=chat_rooms).distinct()
    available_users = User.objects.exclude(id=request.user.id).exclude(id__in=existing_chat_users)

    context = {
        'chat_rooms': chat_rooms,
        'available_users': available_users
    }

    return render(request, 'chat/chat_home.html', context)

@login_required
def chat_room(request, room_id):
    # Get the chat room
    chat_room = get_object_or_404(ChatRoom, id=room_id, users=request.user)

    # Get all messages for this room
    chat_messages = ChatMessage.objects.filter(room_name=chat_room.name)

    # Mark unread messages as read
    unread_messages = chat_messages.filter(is_read=False).exclude(sender=request.user)
    unread_messages.update(is_read=True)

    # Get the other user in the chat
    other_user = chat_room.users.exclude(id=request.user.id).first()

    # Handle message submission
    if request.method == 'POST':
        message_text = request.POST.get('message')
        message_type = request.POST.get('message_type', 'text')
        file_url = request.POST.get('file_url')

        if message_text:
            # Create the message
            ChatMessage.objects.create(
                sender=request.user,
                room_name=chat_room.name,
                message=message_text,
                message_type=message_type,
                file_url=file_url
            )

            # Update the chat room's updated_at timestamp
            chat_room.save()  # This will update the auto_now field

            # If it's an AJAX request, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})

            # Otherwise redirect back to the chat room
            return redirect('chat_room', room_id=room_id)

    context = {
        'chat_room': chat_room,
        'messages': chat_messages,
        'other_user': other_user,
    }

    return render(request, 'chat/chat_room.html', context)

@login_required
def create_chat(request, user_id):
    # Get the user to chat with
    other_user = get_object_or_404(User, id=user_id)

    # Check if a chat room already exists with these users
    existing_rooms = ChatRoom.objects.filter(users=request.user).filter(users=other_user)

    if existing_rooms.exists():
        # Use the existing room
        chat_room = existing_rooms.first()
    else:
        # Create a new room with a unique name
        room_name = f"chat_{uuid.uuid4().hex[:10]}"
        chat_room = ChatRoom.objects.create(name=room_name)
        chat_room.users.add(request.user, other_user)

    return redirect('chat_room', room_id=chat_room.id)

@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']

            # Cloudinary is already configured in settings

            # Determine file type
            file_name = file.name.lower()
            is_image = file_name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'))
            is_video = file_name.endswith(('.mp4', '.mov', '.avi', '.webm'))

            # Only allow image and video uploads
            if not (is_image or is_video):
                return JsonResponse({
                    'error': 'Only image and video files are supported'
                }, status=400)

            # Upload to Cloudinary with appropriate resource_type
            if is_image:
                result = cloudinary.uploader.upload(file)
                url = result['secure_url']
                file_type = 'image'
            elif is_video:
                result = cloudinary.uploader.upload(
                    file,
                    resource_type="video"
                )
                url = result['secure_url']
                file_type = 'video'

            return JsonResponse({
                'url': url,
                'filename': file.name,
                'file_type': file_type
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'No file provided'}, status=400)
