angular.module('gdgorgua', ['ngResource','$strap'])
    .config(function($routeProvider,$httpProvider) {
        $routeProvider.
            when('/events/', {controller:'EventsListCtrl', templateUrl:'/templates/admin/events/list.html'}).
            when('/events/new', {controller:'EventsCreateCtrl', templateUrl:'/templates/admin/events/detail.html'}).
            when('/events/:eventId', {controller:'EventsEditCtrl', templateUrl:'/templates/admin/events/detail.html'}).

            when('/participants/', {controller:'ParticipantsListCtrl', templateUrl:'/templates/admin/participants/list.html'}).
            when('/participants/:participantId', {controller:'ParticipantsEditCtrl', templateUrl:'/templates/admin/participants/detail.html'}).
            when('/participants/new', {controller:'ParticipantsCreateCtrl', templateUrl:'/templates/admin/participants/detail.html'}).
            otherwise({redirectTo:'/events/'});

        $httpProvider.interceptors.push(function($q, $rootScope) {
            $rootScope.requests = 0;
            return {
                'request': function(config) {
                    $rootScope.requests++;
                    return config;
                },
                'response': function(response) {
                    $rootScope.requests--;
                    return response;
                },
                'responseError': function(rejection) {
                    $rootScope.error = true;
                    $rootScope.requests--;

                    return rejection;
                }
            }
         });
    })
.controller('MainCtrl', function($scope, $location,$http) {
   $scope.info = $http.get('/api/info').then(function(r) { return r.data;});
   $scope.$watch(function() { return $location.path()}, function(nv) {
       var parts = nv.split('/');
       $scope.current = parts[1];
   });
});
