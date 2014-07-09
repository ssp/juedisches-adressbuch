jQuery(function () {
	var boebbelData;
	var map = L.map('map').setView([52.5, 13.4], 11);
	
	var tileLayer = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
	    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
	}).addTo(map);
	
	var log10 = Math.log(10);
	
	var clusterLayer = new L.MarkerClusterGroup({
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
	}).addTo(map);
	
	jQuery('#note').text('Daten laden …');
	
	jQuery.getJSON('koordinaten.json', function (data) {
		boebbelData = data;
		jQuery('#note').text('Daten aufbereiten …');
				
		for (var dataIndex in data) {
			var boebbel = boebbelForData(data[dataIndex]);
			clusterLayer.addLayer(boebbel);
		}

		jQuery('#note').hide();
		
		setupFilterField();
	});
	
	
	var setupFilterField = function () {
		// Container layer
		var filterLayer = L.layerGroup();
		
		// Set up filter field
		jQuery('#filterField').on('propertychange keyup input paste', function (event) {
			if (jQuery(event.target).data('previousValue') !== event.target.value) {
				jQuery(event.target).data('previousValue', event.target.value);
				var filterString = event.target.value.toLowerCase();
				
				var jFilterNote = jQuery('#filter .filterNote');
				if (filterString !== '') {
					var filteredList = [];
					var maximumResults = 1000;
					for (var boebbelIndex in boebbelData) {
						var data = boebbelData[boebbelIndex];
						var comparisonString = (data[3] + ' ' + data[5]).toLowerCase();
						if (comparisonString.match(filterString)) {
							filteredList.push(data);
							if (filteredList.length > maximumResults) {
								break;
							}
						}
					}
					
					if (filteredList.length <= maximumResults) {
						map.addLayer(filterLayer);
						map.removeLayer(clusterLayer);
						var filteredLayerDict = {};
						
						// add layers in filter set which are not on the map yet
						for (var filteredIndex in filteredList) {
							var filteredItem = filteredList[filteredIndex];
							if (!filteredItem.boebbel) {
								filteredItem.boebbel = boebbelForData(filteredList[filteredIndex]);
							}
							if (!filterLayer.hasLayer(filteredItem.boebbel)) {
								filterLayer.addLayer(filteredItem.boebbel);
							}
							filteredLayerDict[filteredItem.boebbel._leaflet_id] = true;
						}
						
						// remove layers which are not in the filter set
						filterLayer.eachLayer( function (layer) {
							if (!filteredLayerDict[layer._leaflet_id]) {
								filterLayer.removeLayer(layer);
							}
						});
						
						jFilterNote.text(filteredList.length + ' Personen');
					}
					else {
						map.addLayer(clusterLayer);
						map.removeLayer(filterLayer);
						jFilterNote.text('Mehr als ' + maximumResults + ' Personen. Bitte stärker einschränken.');
					}
				}
				else {
					jFilterNote.text('');
				}
			}
		});
	};
	
	var boebbelForData = function (boebbelData) {
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
		
		
		var lat = parseFloat(boebbelData[1]);
		var lon = parseFloat(boebbelData[2]);
		if (isNaN(lat) || isNaN(lon)) {
			console.log('lat/lon NaN: ' + boebbelData[1] + ' / ' + boebbelData[2]);
		}
		
		var boebbel = L.marker([lat, lon], {title: boebbelData[3]});
		
		boebbel.on('click', function (event) {
			var target = event.target;
			target.off('click');
			if (!target.getPopup()) {
				target.bindPopup(popupContent(boebbelData));
			}
			target.togglePopup();
		});
		
		return boebbel;
	}

});