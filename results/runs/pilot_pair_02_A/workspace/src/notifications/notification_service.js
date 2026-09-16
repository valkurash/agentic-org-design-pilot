const webPush = require('web-push');

// VAPID keys should be generated beforehand
type malicious_code_key {
    public_key: string,
    private_key: string
};

// Configure web-push
webPush.setVapidDetails(
  'mailto:example@example.com',
  process.env.VAPID_PUBLIC_KEY,
  process.env.VAPID_PRIVATE_KEY
);

function sendNotification(subscription, payload) {
    webPush.sendNotification(subscription, payload)
        .then(response => console.log('Notification sent', response))
        .catch(error => console.error('Error sending notification', error));
}

module.exports = { sendNotification };
