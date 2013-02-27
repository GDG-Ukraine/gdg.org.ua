angular.module('gdgorgua', ['ngResource'])

.config(function($routeProvider) {
    $routeProvider.
      when('/', {controller:'ListCtrl', templateUrl:'list.html'}).
      when('/edit/:participantId', {controller:'EditCtrl', templateUrl:'detail.html'}).
      when('/new', {controller:'CreateCtrl', templateUrl:'detail.html'}).
      otherwise({redirectTo:'/'});
  })

.controller('ListCtrl', function ($scope, Participant) {
  $scope.participants = Participant.query();
})


.controller('CreateCtrl', function ($scope, $location, Participant) {
  $scope.save = function() {
    Participant.save($scope.p, function(participant) {
      $location.path('/edit/' + participant.id);
    });
  }
})


.controller('EditCtrl', function ($scope, $location, $routeParams, Participant) {
  var self = this;

  Participant.get({id: $routeParams.participantId}, function(participant) {
    self.original = participant;
    $scope.p = new Participant(self.original);
  });

  $scope.isClean = function() {
    return angular.equals(self.original, $scope.p);
  }

  $scope.destroy = function() {
    self.original.remove(function() {
      $location.path('/list');
    });
  };

  $scope.save = function() {
    $scope.p.update(function() {
      $location.path('/');
    });
  };
})

.factory('Participant', function($resource) {
      var Participant = $resource('/api/participants/:id',
          { apiKey: 'getkeyduringauth' }, {
            update: { method: 'PUT' }
          }
      );
      return Participant;
});
