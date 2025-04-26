// Main JavaScript file for MyDay application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Booking form calculations
    const bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        updateTotalPrice();
        
        // Listen for changes in sub-events and categories
        const subEventCheckboxes = document.querySelectorAll('.sub-event-checkbox');
        subEventCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                toggleSubEventCategories(this);
                updateTotalPrice();
            });
        });
        
        const categoryCheckboxes = document.querySelectorAll('.category-checkbox');
        categoryCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateTotalPrice);
        });
        
        // Guest count input
        const guestCountInput = document.getElementById('guest-count');
        if (guestCountInput) {
            guestCountInput.addEventListener('change', updateTotalPrice);
        }
        
        // Discount code application
        const applyDiscountBtn = document.getElementById('apply-discount-btn');
        if (applyDiscountBtn) {
            applyDiscountBtn.addEventListener('click', applyDiscount);
        }
    }
    
    // Chat functionality
    initializeChat();
});

// Toggle sub-event categories visibility
function toggleSubEventCategories(checkbox) {
    const subEventId = checkbox.value;
    const categoriesContainer = document.getElementById(`categories-${subEventId}`);
    
    if (categoriesContainer) {
        if (checkbox.checked) {
            categoriesContainer.classList.remove('d-none');
        } else {
            categoriesContainer.classList.add('d-none');
            // Uncheck all categories when sub-event is unchecked
            const categoryCheckboxes = categoriesContainer.querySelectorAll('input[type="checkbox"]');
            categoryCheckboxes.forEach(cb => {
                cb.checked = false;
            });
        }
    }
}

// Update total price based on selections
function updateTotalPrice() {
    const bookingForm = document.getElementById('booking-form');
    if (!bookingForm) return;
    
    let totalPrice = 0;
    
    // Add sub-event prices
    const selectedSubEvents = document.querySelectorAll('.sub-event-checkbox:checked');
    selectedSubEvents.forEach(subEvent => {
        const price = parseFloat(subEvent.dataset.price);
        totalPrice += price;
    });
    
    // Add category prices
    const selectedCategories = document.querySelectorAll('.category-checkbox:checked');
    selectedCategories.forEach(category => {
        const price = parseFloat(category.dataset.price);
        totalPrice += price;
    });
    
    // Apply guest count multiplier if needed
    // This is just an example - you might have different logic
    const guestCountInput = document.getElementById('guest-count');
    if (guestCountInput) {
        const guestCount = parseInt(guestCountInput.value);
        // You could apply a multiplier here if needed
    }
    
    // Apply discount if available
    const discountElement = document.getElementById('discount-amount');
    let finalPrice = totalPrice;
    
    if (discountElement && discountElement.dataset.percentage) {
        const discountPercentage = parseFloat(discountElement.dataset.percentage);
        const discountAmount = (totalPrice * discountPercentage) / 100;
        finalPrice = totalPrice - discountAmount;
        
        // Update discount display
        discountElement.textContent = `- $${discountAmount.toFixed(2)} (${discountPercentage}%)`;
    }
    
    // Update price displays
    const totalPriceElement = document.getElementById('total-price');
    const finalPriceElement = document.getElementById('final-price');
    
    if (totalPriceElement) {
        totalPriceElement.textContent = `$${totalPrice.toFixed(2)}`;
    }
    
    if (finalPriceElement) {
        finalPriceElement.textContent = `$${finalPrice.toFixed(2)}`;
    }
}

// Apply discount code
function applyDiscount(e) {
    e.preventDefault();
    
    const discountCodeInput = document.getElementById('discount-code');
    if (!discountCodeInput || !discountCodeInput.value.trim()) {
        showAlert('Please enter a discount code', 'warning');
        return;
    }
    
    const discountCode = discountCodeInput.value.trim();
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Send AJAX request to validate discount
    fetch('/bookings/apply-discount/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: `discount_code=${discountCode}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.valid) {
            // Update discount display
            const discountElement = document.getElementById('discount-amount');
            if (discountElement) {
                discountElement.dataset.percentage = data.percentage;
                updateTotalPrice();
            }
            showAlert(`Discount code applied: ${data.percentage}% off`, 'success');
        } else {
            showAlert(data.message || 'Invalid discount code', 'danger');
        }
    })
    .catch(error => {
        console.error('Error applying discount:', error);
        showAlert('Error applying discount code', 'danger');
    });
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertsContainer = document.getElementById('alerts-container');
    if (!alertsContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertsContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}

// Initialize chat functionality
function initializeChat() {
    const chatContainer = document.getElementById('chat-container');
    if (!chatContainer) return;
    
    const roomName = chatContainer.dataset.room;
    const senderId = chatContainer.dataset.sender;
    
    // Connect to WebSocket
    const chatSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/chat/' + roomName + '/'
    );
    
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        displayMessage(data.message, data.sender, data.message_type);
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    };
    
    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };
    
    // Send message function
    const messageInput = document.getElementById('chat-message-input');
    const sendButton = document.getElementById('chat-message-submit');
    
    if (sendButton && messageInput) {
        sendButton.addEventListener('click', function() {
            sendMessage(messageInput.value, 'text');
            messageInput.value = '';
        });
        
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendButton.click();
                e.preventDefault();
            }
        });
    }
    
    // File upload
    const fileInput = document.getElementById('chat-file-input');
    const fileButton = document.getElementById('chat-file-button');
    
    if (fileButton && fileInput) {
        fileButton.addEventListener('click', function() {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                uploadFile(this.files[0]);
            }
        });
    }
    
    // Send message to WebSocket
    function sendMessage(message, type = 'text', fileUrl = null) {
        if (message.trim() === '' && !fileUrl) return;
        
        chatSocket.send(JSON.stringify({
            'message': fileUrl || message,
            'sender': senderId,
            'type': type
        }));
    }
    
    // Display message in chat
    function displayMessage(message, sender, type = 'text') {
        const isCurrentUser = sender == senderId;
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${isCurrentUser ? 'sent' : 'received'}`;
        
        let content = '';
        
        switch (type) {
            case 'image':
                content = `<img src="${message}" class="img-fluid rounded" alt="Image">`;
                break;
            case 'audio':
                content = `<audio controls src="${message}" class="w-100"></audio>`;
                break;
            case 'file':
                const fileName = message.split('/').pop();
                content = `<a href="${message}" target="_blank" class="btn btn-sm btn-outline-primary">
                    <i class="fas fa-file me-2"></i>${fileName}
                </a>`;
                break;
            default: // text
                content = message;
        }
        
        messageElement.innerHTML = content;
        chatContainer.appendChild(messageElement);
    }
    
    // Upload file to server
    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('room_name', roomName);
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/chat/upload/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.url) {
                // Determine file type
                let fileType = 'file';
                if (file.type.startsWith('image/')) {
                    fileType = 'image';
                } else if (file.type.startsWith('audio/')) {
                    fileType = 'audio';
                }
                
                sendMessage(data.url, fileType, data.url);
            } else {
                showAlert('Error uploading file', 'danger');
            }
        })
        .catch(error => {
            console.error('Error uploading file:', error);
            showAlert('Error uploading file', 'danger');
        });
    }
}
