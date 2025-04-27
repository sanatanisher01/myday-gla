/**
 * Keep-alive script for MyDay application
 * 
 * This script periodically pings the health check endpoint to keep the application alive
 * on free hosting platforms like Render that spin down after inactivity.
 */

(function() {
    // Configuration
    const PING_INTERVAL = 10 * 60 * 1000; // 10 minutes in milliseconds
    const HEALTH_CHECK_URL = '/health/';
    
    // Function to ping the health check endpoint
    function pingHealthCheck() {
        fetch(HEALTH_CHECK_URL, { 
            method: 'HEAD',
            cache: 'no-store'
        })
        .then(response => {
            console.log('Keep-alive ping successful:', response.status);
        })
        .catch(error => {
            console.error('Keep-alive ping failed:', error);
        });
    }
    
    // Start pinging when the page loads
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Keep-alive script initialized');
        
        // Ping immediately
        pingHealthCheck();
        
        // Set up interval for regular pings
        setInterval(pingHealthCheck, PING_INTERVAL);
    });
})();
