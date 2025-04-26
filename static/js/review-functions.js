// Review Functions
document.addEventListener('DOMContentLoaded', function() {
    // Read More functionality
    const readMoreButtons = document.querySelectorAll('.read-more-btn');

    readMoreButtons.forEach(button => {
        button.addEventListener('click', function() {
            const reviewId = this.getAttribute('data-review-id');
            const reviewContent = this.closest('.review-content');
            const shortText = reviewContent.querySelector('.short-text');
            const fullText = reviewContent.querySelector('.full-text');

            if (shortText.style.display !== 'none') {
                // Show full text
                shortText.style.display = 'none';
                fullText.style.display = 'block';
                this.innerHTML = '<small>Show less</small>';
            } else {
                // Show short text
                shortText.style.display = 'block';
                fullText.style.display = 'none';
                this.innerHTML = '<small>Read more</small>';
            }
        });
    });

    // Like functionality removed

    // Helper function to show toast notifications
    function showToast(type, message) {
        // Check if SweetAlert2 is available
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: type,
                title: message,
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 3000,
                timerProgressBar: true
            });
        } else {
            // Fallback to console
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Review Modal functionality for mobile
    const reviewTexts = document.querySelectorAll('.review-text');

    reviewTexts.forEach(text => {
        text.addEventListener('click', function() {
            if (window.innerWidth < 768) {
                const reviewContent = this.closest('.review-content');
                const fullText = reviewContent.querySelector('.full-text').textContent;
                const reviewCard = this.closest('.testimonial-card');
                const userName = reviewCard.querySelector('h5').textContent;
                const userImg = reviewCard.querySelector('.testimonial-img') || reviewCard.querySelector('.d-flex.align-items-center.justify-content-center');
                const rating = reviewCard.querySelector('[style*="color: #ffbe0b"]').innerHTML;
                const date = reviewCard.querySelector('p[style*="font-size: 0.8rem"]').textContent;

                // Create modal
                showReviewModal(userName, userImg.outerHTML, rating, date, fullText);
            }
        });
    });

    // Function to show review modal
    function showReviewModal(userName, userImg, rating, date, comment) {
        // Create modal elements
        const modal = document.createElement('div');
        modal.className = 'review-modal';

        modal.innerHTML = `
            <div class="review-modal-content">
                <span class="review-modal-close">&times;</span>
                <div class="review-modal-header">
                    <div class="review-modal-user-img">
                        ${userImg.includes('img') ? userImg : '<i class="fas fa-user"></i>'}
                    </div>
                    <div class="review-modal-user-info">
                        <h4>${userName}</h4>
                        <div class="review-modal-rating">
                            ${rating}
                        </div>
                        <div class="review-modal-date">${date}</div>
                    </div>
                </div>
                <div class="review-modal-body">
                    ${comment}
                </div>
            </div>
        `;

        // Add modal to body
        document.body.appendChild(modal);

        // Show modal
        setTimeout(() => {
            modal.classList.add('active');
        }, 10);

        // Close modal on click
        const closeBtn = modal.querySelector('.review-modal-close');
        closeBtn.addEventListener('click', () => {
            modal.classList.remove('active');
            setTimeout(() => {
                document.body.removeChild(modal);
            }, 300);
        });

        // Close modal on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
                setTimeout(() => {
                    document.body.removeChild(modal);
                }, 300);
            }
        });
    }
});
