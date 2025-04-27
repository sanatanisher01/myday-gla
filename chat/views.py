from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.dateformat import format
from django.contrib import messages
from .models import ChatMessage
import cloudinary
import cloudinary.uploader

@login_required
def chat_home(request):
    # Get all users the current user has chatted with
    chat_partners = User.objects.filter(
        Q(sent_messages__receiver=request.user) | Q(received_messages__sender=request.user)
    ).distinct()

    # For each chat partner, get the latest message and count of unread messages
    chat_list = []
    for partner in chat_partners:
        # Get the latest message between these users
        latest_message = ChatMessage.objects.filter(
            (Q(sender=request.user) & Q(receiver=partner)) |
            (Q(sender=partner) & Q(receiver=request.user))
        ).order_by('-timestamp').first()

        # Count unread messages from this partner
        unread_count = ChatMessage.objects.filter(
            sender=partner,
            receiver=request.user,
            is_read=False
        ).count()

        # Always add the chat partner to the list, even if there's no message yet
        # This ensures that new chats initiated by managers are shown
        chat_list.append({
            'user': partner,
            'latest_message': latest_message,
            'timestamp': latest_message.timestamp if latest_message else partner.date_joined,  # Use date_joined as fallback
            'unread_count': unread_count,
            'is_manager': partner.profile.is_manager
        })

    # Sort by latest message timestamp
    chat_list.sort(key=lambda x: x['timestamp'], reverse=True)

    # Get all users for the new conversation modal
    # Exclude the current user and users they already have conversations with
    available_users_query = User.objects.exclude(
        id__in=[request.user.id] + [chat['user'].id for chat in chat_list]
    )

    # If the current user is not a manager, only show managers in the available users list
    if not request.user.profile.is_manager:
        available_users = available_users_query.filter(profile__is_manager=True)
    else:
        # Managers can chat with anyone
        available_users = available_users_query

    context = {
        'chat_list': chat_list,
        'available_users': available_users
    }

    return render(request, 'chat/chat_home.html', context)

@login_required
def chat_room(request, user_id):
    # Get the other user
    other_user = get_object_or_404(User, id=user_id)

    # Check if the current user is allowed to chat with the other user
    # Regular users can only chat with managers
    if not request.user.profile.is_manager and not other_user.profile.is_manager:
        messages.error(request, 'You can only chat with event managers.')
        return redirect('chat:chat_home')

    # Get all messages between these users
    messages = ChatMessage.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')

    # Mark messages from other user as read
    # Only mark as read if it's a GET request (initial page load)
    # For POST requests (sending messages), we don't mark as read to avoid race conditions
    if request.method == 'GET':
        ChatMessage.objects.filter(
            sender=other_user,
            receiver=request.user,
            is_read=False
        ).update(is_read=True)

    # Handle message submission
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        message_type = request.POST.get('message_type', 'text')
        file_url = request.POST.get('file_url', '')

        # Allow empty message text for image/video messages
        if message_text or file_url:
            # Create the message
            ChatMessage.objects.create(
                sender=request.user,
                receiver=other_user,
                message=message_text,
                message_type=message_type,
                file_url=file_url
            )

            # If it's an AJAX request, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})

            # Otherwise redirect back to the chat room
            return redirect('chat:chat_room', user_id=user_id)

    context = {
        'other_user': other_user,
        'messages': messages,
    }

    return render(request, 'chat/chat_room.html', context)

@login_required
def create_chat(request, user_id):
    # Get the user to chat with
    other_user = get_object_or_404(User, id=user_id)

    # Check if the current user is allowed to chat with the other user
    # Regular users can only chat with managers
    if not request.user.profile.is_manager and not other_user.profile.is_manager:
        messages.error(request, 'You can only chat with event managers.')
        return redirect('chat:chat_home')

    # Check if there are any existing messages between these users
    existing_messages = ChatMessage.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).exists()

    # If no existing messages and the current user is a manager, create a welcome message
    if not existing_messages and request.user.profile.is_manager:
        welcome_message = f"Hello {other_user.first_name if other_user.first_name else other_user.username}! How can I help you with your event planning today?"
        ChatMessage.objects.create(
            sender=request.user,
            receiver=other_user,
            message=welcome_message
        )

    # Redirect to the chat room with this user
    return redirect('chat:chat_room', user_id=other_user.id)

@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']

            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:  # 10MB in bytes
                return JsonResponse({
                    'error': 'File size exceeds 10MB limit'
                }, status=400)

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

@login_required
def check_new_messages(request, user_id):
    """
    Check for new messages since the last message ID.
    Returns JSON with new messages.
    """
    last_id = request.GET.get('last_id', '0')

    try:
        last_id = int(last_id)
    except ValueError:
        last_id = 0

    # Get the other user
    other_user = get_object_or_404(User, id=user_id)

    # Get new messages between these users
    new_messages = ChatMessage.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user)),
        id__gt=last_id
    ).order_by('timestamp')

    # Format messages for JSON response
    messages_data = []
    for message in new_messages:
        # Mark messages from other user as read
        if message.sender != request.user and not message.is_read:
            message.is_read = True
            message.save()

        messages_data.append({
            'id': message.id,
            'message': message.message,
            'message_type': message.message_type,
            'file_url': message.file_url,
            'is_sender': message.sender == request.user,
            'timestamp': format(message.timestamp, 'M d, g:i a'),
            'is_read': message.is_read,
            'is_manager': message.sender.profile.is_manager
        })

    return JsonResponse({'new_messages': messages_data})
