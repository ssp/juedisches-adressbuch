jQuery(function () {
	var map = L.map('map').setView([52.5, 13.4], 11);
	
	L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
	    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
	}).addTo(map);
	
	
	jQuery('#note').text('Daten laden …');
	
	jQuery.getJSON('koordinaten.json', function (data) {
		jQuery('#note').text('Daten aufbereiten …');
		
		var log10 = Math.log(10);
		var markerLayer = new L.MarkerClusterGroup({
			maxClusterRadius: 50,
			iconCreateFunction: function(cluster) {
				var count = cluster.getChildCount();
				var magnitude = Math.floor(Math.log(count)/log10);
				var size = 20 + magnitude * 5;
				return new L.DivIcon({
					html:'<div><span>' + count + '</span></div>',
					className:'marker-cluster marker-cluster-' + magnitude,
					iconSize:L.point(size, size)
				});
			}
		});

		var heatmapLayer = new L.TileLayer.HeatCanvas({}, {
			'step':0.5,
			'degree':HeatCanvas.LINEAR,
			'opacity':0.7
		});
	
		for (var dataIndex in data) {
			var boebbelData = data[dataIndex];
			var lat = parseFloat(boebbelData[1]);
			var lon = parseFloat(boebbelData[2]);
			if (isNaN(lat) || isNaN(lon)) {
				console.log('lat/lon NaN: ' + boebbelData[1] + ' / ' + boebbelData[2]);
			}
			
			var boebbel = L.marker([lat, lon], {title: boebbelData[3]});
			boebbel.bindPopup(popupContent(boebbelData));
			markerLayer.addLayer(boebbel);
			
			heatmapLayer.pushData(lat, lon, 1);
		}
	
		// map.addLayer(heatmapLayer);
		jQuery('#note').hide();
		map.addLayer(markerLayer);
	});

	var popupContent = function (data) {
		var appendP = function (content, contentType) {
			if (content) {
				var p = document.createElement('p');
				p.appendChild(document.createTextNode(content));
				if (contentType) {
					p.setAttribute('class', contentType);
				}
				div.appendChild(p);
			}
		}
	
		var div = document.createElement('div');
		appendP(data[3], 'name');
		appendP(data[4], 'job' );
		appendP(data[5], 'adresse');
	
		return div;
	};
});