from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.dateformat import format
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

        if latest_message:
            chat_list.append({
                'user': partner,
                'latest_message': latest_message,
                'timestamp': latest_message.timestamp
            })

    # Sort by latest message timestamp
    chat_list.sort(key=lambda x: x['timestamp'], reverse=True)

    # Get all users for the new conversation modal
    # Exclude the current user and users they already have conversations with
    available_users = User.objects.exclude(
        id__in=[request.user.id] + [chat['user'].id for chat in chat_list]
    )

    context = {
        'chat_list': chat_list,
        'available_users': available_users
    }

    return render(request, 'chat/chat_home.html', context)

@login_required
def chat_room(request, user_id):
    # Get the other user
    other_user = get_object_or_404(User, id=user_id)

    # Get all messages between these users
    messages = ChatMessage.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')

    # Handle message submission
    if request.method == 'POST':
        message_text = request.POST.get('message')
        message_type = request.POST.get('message_type', 'text')
        file_url = request.POST.get('file_url', '')

        if message_text:
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
            return redirect('chat_room', user_id=user_id)

    context = {
        'other_user': other_user,
        'messages': messages,
    }

    return render(request, 'chat/chat_room.html', context)

@login_required
def create_chat(request, user_id):
    # Get the user to chat with
    other_user = get_object_or_404(User, id=user_id)

    # Redirect to the chat room with this user
    return redirect('chat_room', user_id=other_user.id)

@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']

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
        messages_data.append({
            'id': message.id,
            'message': message.message,
            'message_type': message.message_type,
            'file_url': message.file_url,
            'is_sender': message.sender == request.user,
            'timestamp': format(message.timestamp, 'M d, g:i a')
        })

    return JsonResponse({'new_messages': messages_data})
