function initMap(directionsRequest) {
    var map = new google.maps.Map(
        document.getElementById('travel_select_map'), {
            zoom: 4, center: {
                lat: 40.462507, lng: -98.746465
            }});

    var cities = document.getElementById('travel_select_map').getAttribute('name');
    var cityArr = cities.split(",");
    cityArr.pop();

    var geocoder = new google.maps.Geocoder();
    var infowindow = new google.maps.InfoWindow();
    for (i = 0; i < cityArr.length; i++) {
        geocodeMarker(cityArr[i], geocoder, map, infowindow);
    }
}

function geocodeMarker(city, geocoder, map, infowindow) {
    geocoder.geocode({
        'address': city
    }, function(results, status) {
        if (status === 'OK') {
            var location = results[0].geometry.location;

            var marker = new google.maps.Marker({
                map: map,
                position: location,
                title: 'Click to View'
            });

            // Keep only one infowindow open
            google.maps.event.addListener(marker, 'click', function() {
                infowindow.setContent(city)
                infowindow.open(map, this);
            });

        } else {
            alert('Geocode was not successful for the following reason: ' + status);
        }
    });
}