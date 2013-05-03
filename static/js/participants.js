angular.module('gdgorgua')

.controller('ParticipantsListCtrl', function ($scope, Participant, $location, $window) {
  if ($window.sessionStorage) {
            try {
                $scope.participants = JSON.parse($window.sessionStorage.getItem('gdgparticipants'));
            } catch (err) {}
  }

  Participant.query({},function(ps) {
      $scope.participants = ps;
      if ($window.sessionStorage) {
          $window.sessionStorage.setItem("gdgparticipants",JSON.stringify(ps));
      }
  });
  $scope.edit = function(id) {
      $location.path('/participants/'+id);
  }
})


.controller('ParticipantsCreateCtrl', function ($scope, $location, Participant) {
  $scope.save = function() {
    Participant.save($scope.p, function(participant) {
      $location.path('/participants/' + participant.id);
    });
  }
})


.controller('ParticipantsEditCtrl', function ($scope, $location, $routeParams, Participant, $window,GEvent, $http) {
  var self = this;
  if ($window.sessionStorage) {
            try {
                $scope.p = JSON.parse($window.sessionStorage.getItem('gdgparticipant'+$routeParams.participantId));
            } catch(err) {};
  }
  Participant.get({id: $routeParams.participantId}, function(participant) {
    self.original = participant;
    $scope.p = new Participant(self.original);
    if ($window.sessionStorage)  $window.sessionStorage.setItem('gdgparticipant'+$routeParams.participantId, JSON.stringify(participant));

  });

  $scope.isClean = function() {
    return angular.equals(self.original, $scope.p);
  }

  $scope.destroy = function() {
    self.original.$remove(function() {
      $location.path('/participants/');
    });
  };

  $scope.save = function() {
    $scope.p.$update(function() {
      $location.path('/participants/');
    });
  };
  $scope.back = function() {
      $window.history.back();
  }
  $scope.show = function(id) {
      $location.path('/events/'+id);
  }

})

.factory('Participant', function($resource) {
      var Participant = $resource('/api/participants/:id',
          { id: "@id" }, {
            update: { method: 'PUT' }
          }
      );
      return Participant;
});
