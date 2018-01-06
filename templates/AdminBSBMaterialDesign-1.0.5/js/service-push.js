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
	    var message = data.body;
	    var icon = "https://fw.scherer.me/static/images/icon-alarm.png";
	    break;
	default:
	    var title = data.title;
	    var message = data.message;
	    var icon = "img/FM_logo_2013.png";
	    if(data.url){
		self.url = data.url;
	    }
    }

    var actions = [];
    if(data.urlMap) {
      self.urlMap = data.urlMap;
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
    // Click in the Notification
    event.notification.close();
    if (typeof self.url != 'undefined') {
	event.waitUntil(clients.openWindow(self.url));
    }
    return;
  }

  switch (event.action) {
    case 'googleMaps':
      event.waitUntil(clients.openWindow(self.urlMap));
      break;
    default:
      console.log(`Unknown action clicked: '${event.action}'`);
      break;
  }
});
/**** END notificationActionClickEvent ****/