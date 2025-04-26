// Tab Title Logo Script
document.addEventListener('DOMContentLoaded', function() {
    // Function to update the title with MD prefix
    const updateTabTitle = () => {
        const originalTitle = document.title;

        // Only add the prefix if it's not already there
        if (!originalTitle.includes('MD |')) {
            // Set a clean title format
            document.title = 'MD | MyDay';
        }
    };

    // Update the title initially
    setTimeout(updateTabTitle, 100);

    // Update the title when the page visibility changes (tab is selected)
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            updateTabTitle();
        }
    });

    // Also update when switching tabs
    window.addEventListener('focus', updateTabTitle);
});
