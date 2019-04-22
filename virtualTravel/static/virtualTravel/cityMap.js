function initMap(request) {
    $.ajax({
        url: "/virtualTravel/refresh_cityMap",
        dataType: "json",
        success: renderMap
    });
}

function renderMap(response) {
    if (response.length <= 0) {
        return;
    }
    // console.log(response);

    var mapOptions = {
        zoom: 13
    }
    var map = new google.maps.Map(document.getElementById('map'), mapOptions);

    var panormaOptions = {
        pov: {
            heading: 34,
            pitch: 10
        }
    }
    var panorama = new google.maps.StreetViewPanorama(document.getElementById('pano'), panormaOptions);
    // google.maps.event.trigger(panorama, 'resize');
    // set map location to current city
    var currentCity = response[0].fields.name;
    var geocoder = new google.maps.Geocoder();
    geocodeCity(currentCity, geocoder, map, panorama);

    // add markers
    var sites = [];
    $(response).each(function(i, value) {
        if (i != 0) {
            sites.push({
                name: this.fields.name,
                text: this.fields.description,
                url: this.fields.picture_url
            });
        }
    })
    
    var infowindow = new google.maps.InfoWindow();
    for (i = 0; i < sites.length; i++) {
        geocodeMarker(sites[i], geocoder, map, panorama, infowindow);
    }
}

function geocodeCity(name, geocoder, map, panorama) {
    geocoder.geocode({
        'address': name
    }, function(results, status) {
        if (status === 'OK') {
            var location = results[0].geometry.location;
            map.setCenter(location);
            panorama.setPosition(location);
            map.setStreetView(panorama);
            // constructor passing in this DIV.
            var controlDiv = document.createElement('div');
            var backControl = new BackControl(controlDiv, map, location);

            controlDiv.index = 1;
            map.controls[google.maps.ControlPosition.TOP_CENTER].push(controlDiv);
        } else {
            alert('Geocode was not successful for the following reason: ' + status);
        }
    });
}

function geocodeMarker(site, geocoder, map, panorama, infowindow) {
    geocoder.geocode({
        'address': site.name
    }, function(results, status) {
        if (status === 'OK') {
            var location = results[0].geometry.location;

            var markerImage = {
                url: site.url,
                scaledSize: new google.maps.Size(100, 75)
            };

            var marker = new google.maps.Marker({
                map: map,
                icon: markerImage,
                position: location,
                title: 'Click to View'
            });

            var contentString = '<div id="content">'+
                                '<div id="siteNotice"></div>'+
                                '<h1 id="firstHeading" class="firstHeading">'+ site.name +'</h1>'+
                                '<div id="bodyContent">'+
                                '<p>'+ site.text + '</p>'
                                '</div>'+
                                '</div>';

            map.setStreetView(panorama);

            // Keep only one infowindow open at a time
            google.maps.event.addListener(marker, 'click', function() {
                infowindow.setContent(contentString)
                infowindow.open(map, this);
                // map.setZoom(13.5);
                panorama.setPosition(location);
            });

            marker.setMap(map);
        } else {
            alert('Geocode was not successful for the following reason: ' + status);
        }
    });
}

function BackControl(controlDiv, map, location) {
    // Set CSS for the control border.
    var controlUI = document.createElement('div');
    controlUI.style.backgroundColor = 'rgb(73, 46, 65)';
    controlUI.style.border = '2px solid rgb(73, 46, 65)';
    controlUI.style.borderRadius = '3px';
    controlUI.style.boxShadow = '0 2px 6px rgba(0,0,0,.3)';
    controlUI.style.cursor = 'pointer';
    controlUI.style.marginBottom = '22px';
    controlUI.style.textAlign = 'center';
    controlUI.title = 'Click to Back to the Travel Page';
    controlDiv.appendChild(controlUI);

    // Set CSS for the control interior.
    var controlText = document.createElement('div');
    controlText.style.backgroundColor = 'rgb(73, 46, 65)';
    controlText.style.borderRadius = '3px';
    controlText.style.color = '#fff';
    controlText.style.fontFamily = 'Roboto,Arial,sans-serif';
    controlText.style.fontSize = '16px';
    controlText.style.lineHeight = '38px';
    controlText.style.paddingLeft = '5px';
    controlText.style.paddingRight = '5px';
    controlText.innerHTML = 'Back to Travel';
    controlUI.appendChild(controlText);

    // Setup the click event listeners: simply set the map to Chicago.
    controlUI.addEventListener('click', function() {
       window.location = "travel";
    });

}

