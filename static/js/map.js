(function (factory) {
  if (typeof define === "function" && define.amd) {
    // AMD. Register as an anonymous module.
    define(["google"], factory);
  } else if (typeof module === "object" && module.exports) {
    // Node/CommonJS
    module.exports = factory(require("google"));
  } else {
    // Browser globals
    factory(google);
  }
}(function (google) {
  "use strict";

  var DEFAULT_PARAMS = {
    clat: 0.0,
    clng: 0.0,
    places: [],
    zoom: 0,
  };

  var initializeMap = function(node, attrs) {
    var clat = attrs.clat ? parseFloat(attrs.clat) : DEFAULT_PARAMS.clat;
    var clng = attrs.clng ? parseFloat(attrs.clng) : DEFAULT_PARAMS.clng;
    var places = attrs.places ? JSON.parse(attrs.places) : DEFAULT_PARAMS.places;
    var zoom = attrs.zoom ? parseFloat(attrs.zoom) : DEFAULT_PARAMS.zoom;

    var mapOptions = {
      center: new google.maps.LatLng(clat, clng),
      zoom: zoom,
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      scrollwheel: false,
    };
    var map = new google.maps.Map(node, mapOptions);
    places.forEach(function(p) {
      var marker = new google.maps.Marker({
        position: new google.maps.LatLng(p.lat, p.lng),
        map: map,
      });
      var infoWindow = new google.maps.InfoWindow({
        content: "<a href=\"" + p.url + "\">GDG " + p.name + "</a>",
      });
      google.maps.event.addListener(
        marker, "click",
        function() { infoWindow.open(map, marker); }
      );
      google.maps.event.addListener(
        map, "click",
        function() { infoWindow.close(); }
      );
    });
  };

  var mapNodes = document.querySelectorAll("[data-extends=map]");
  mapNodes.forEach(function(node) {
    initializeMap(node, node.dataset);
  });
}));
