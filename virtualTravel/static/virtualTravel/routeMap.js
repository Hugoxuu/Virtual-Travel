function initMap(directionsRequest) {
    $.ajax({
        url: "/virtualTravel/refresh-map",
        dataType: "json",
        success: rendermap
    });
}

function rendermap(response) {
    // The map
    var map = new google.maps.Map(
        document.getElementById('map'), {
            zoom: 4, center: {
                lat: 40.462507, lng: -98.746465
            }});
    if (response.length != 1) {
        // need route display
        var waypoints = [];
        var departureCity = "";
        var currentCity = "";
        $(response).each(function(i, value) {
            if (i == 0) {
                departureCity = this.fields.name;
            } else if (i == response.length-1) {
                currentCity = this.fields.name;
            } else {
                waypoints.push({
                    location: this.fields.name,
                    stopover: true
                });
            }
        })
        var directionsRequest = {
            origin: departureCity,
            destination: currentCity,
            waypoints: waypoints,
            provideRouteAlternatives: false,
            travelMode: 'DRIVING',
        }
        calculateAndDisplayRoute(directionsRequest, map);

    } else
        var currentCity = response[0].fields.name;

    var geocoder = new google.maps.Geocoder();

    geocodeAddress(currentCity, geocoder, map);
}


function calculateAndDisplayRoute(directionsRequest, map) {

    // Instantiate a directions service.
    var directionsService = new google.maps.DirectionsService;

    // Create a renderer for directions and bind it to the map.
    var directionsDisplay = new google.maps.DirectionsRenderer({
        map: map, preserveViewport: true
    });

    // Retrieve the start and end locations and create a DirectionsRequest using
    // WALKING directions.
    directionsService.route(directionsRequest, function(response, status) {
        // Route the directions and pass the response to a function to create
        // markers for each step.
        if (status === 'OK') {
            document.getElementById('warnings').innerHTML =
            '<b>' + response.routes[0].warnings + '</b>';
            directionsDisplay.setDirections(response);
            // showSteps(response, markerArray, stepDisplay, map);
        } else {
            window.alert('Directions request failed due to ' + status);
        }
    });
}

function geocodeAddress(cityname, geocoder, resultsMap) {
    var currentCityIcon = "https://s3.amazonaws.com/project.17637.team52/red-star-icon.png";
    geocoder.geocode({
        'address': cityname
    }, function(results, status) {
        if (status === 'OK') {
            resultsMap.setCenter(results[0].geometry.location);
            var marker = new google.maps.Marker({
                map: resultsMap,
                position: results[0].geometry.location,
                icon: currentCityIcon
            });
        } else {
            alert('Geocode was not successful for the following reason: ' + status);
        }
    });
}