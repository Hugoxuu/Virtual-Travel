var map;

function initMap(directionsRequest) {
    document.getElementById('map').style.display = 'none';
}

function updateMap(response) {
    // The map
    map = new google.maps.Map(
        document.getElementById('map'), {
            zoom: 4, center: {
                lat: 40.462507, lng: -98.746465
            }});

    if (document.getElementById('map').style.display == 'none') {
        document.getElementById("toggleMap" + response).innerHTML = "Open the Map";
    } else {
        document.getElementById("toggleMap" + response).innerHTML = "Close the Map";
    }

    var route = document.getElementById("list-" + response).getAttribute('name');
    var splitRoute = route.split(",");
    splitRoute.pop();
    console.log(splitRoute);
    // route display
    var waypoints = [];
    var departureCity = "";
    var destinationCity = "";
    for (i = 0; i < splitRoute.length; i++) {
        var name = splitRoute[i].split("\n")[0];
        if (i == 0) {
            departureCity = name;
        } else if (i == splitRoute.length - 1) {
            destinationCity = name;
        } else {
            waypoints.push({
                location: name,
                stopover: true
            });
        }
    }

    var directionsRequest = {
        origin: departureCity,
        destination: destinationCity,
        waypoints: waypoints,
        provideRouteAlternatives: false,
        travelMode: 'DRIVING',
    }
    calculateAndDisplayRoute(directionsRequest, map);
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
            directionsDisplay.setDirections(response);
        } else {
            window.alert('Directions request failed due to ' + status);
        }
    });
}

function toggleMap(id) {
    if (document.getElementById('map').style.display == 'none') {
        document.getElementById('map').style.display = 'inherit';
        document.getElementById("toggleMap" + id).innerHTML = "Close the Map";
    } else {
        document.getElementById('map').style.display = 'none';
        document.getElementById("toggleMap" + id).innerHTML = "Open the Map";
    }   
}