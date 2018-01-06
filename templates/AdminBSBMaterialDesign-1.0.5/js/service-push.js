self.addEventListener('push', function(event) {
    if (!(self.Notification && self.Notification.permission === 'granted')) {
        return;
    }

    var data = {};
    if (event.data) {
        data = event.data.json();
    }
    console.log(data);
    
    switch(data.type) {
	case "alarm":
	    var title = data.title;
	    var message = data.message;
	    var icon = "/static/images/icon-alarm.png"
	    break;
	default:
	    var title = data.title;
	    var message = data.message;
	    var icon = "img/FM_logo_2013.png";
	    self.clickTarget = data.clickTarget;
    }

    if(data.clickMap) {
      self.clickMap = data.clickMap;
      actions= [
          {
            action: 'googleMaps',
            title: 'Karte anzeigen',
            icon: '/static/images/icon-map.png'
          }
        ];
    }

    event.waitUntil(self.registration.showNotification(title, {
        body: message,
        tag: 'push-demo',
        icon: icon,
        badge: icon,
        actions: actions
    }));
});

/**** START notificationActionClickEvent ****/
self.addEventListener('notificationclick', function(event) {
  if (!event.action) {
    // Was a normal notification click
    console.log('Notification Click.');
    return;
  }

  switch (event.action) {
    case 'googleMaps':
      event.waitUntil(clients.openWindow(self.clickTarget));
      break;
    default:
      console.log(`Unknown action clicked: '${event.action}'`);
      break;
  }
});
/**** END notificationActionClickEvent ****/

self.addEventListener('notificationclick', function(event) {
    console.log('[Service Worker] Notification click Received.');

    event.notification.close();

    if(clients.openWindow){
        event.waitUntil(clients.openWindow(self.clickTarget));
    }
});
