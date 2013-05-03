angular.module('gdgorgua')

    .controller('EventsListCtrl', function ($scope, GEvent, $location, $window, $filter) {
        if ($window.sessionStorage) {
            try {
                $scope.events = JSON.parse($window.sessionStorage.getItem('gdgevents'));
            } catch (err) {}
        }
        var currentDate = new Date();
        $scope.isPast = function(e) {

            var date = new Date(e.date);
            return date<currentDate;
        }
        //$scope.events = GEvent.query()
        GEvent.query({},function(events) {
            events.forEach(function(e) {
                e.date = $filter('date')(e.date, 'yyyy-MM-dd');
            })
            $scope.events = events;
            if ($window.sessionStorage) {
                $window.sessionStorage.setItem("gdgevents",JSON.stringify(events));
            }
        });
        $scope.edit = function (id) {
            $location.path('/events/' + id);
        }
    })
    .factory('EventsFielder', function() {
        return function($scope) {
           $scope.addField = function() {
               if (!$scope.e.fields) $scope.e.fields = [];
               $scope.e.fields.push({});
           }
           $scope.deleteField = function(field) {
              var i = $scope.e.fields.indexOf(field);
              if (i>=0) $scope.e.fields.splice(i,1);
           }
        };
    })


    .controller('EventsCreateCtrl', function ($scope, $location, GEvent,EventsFielder) {
        EventsFielder($scope);
        $scope.editing = false;
        $scope.save = function () {
            GEvent.save($scope.e, function (e) {
                $location.path('/edit/' + e.id);
            });
        }
    })


    .controller('EventsEditCtrl', function ($scope, $location, $routeParams, GEvent, $http,Participant,$window, $filter, EventsFielder) {
        EventsFielder($scope);
        var self = this;

        $scope.editing = true;
        $scope.tab = 'info';

        $scope.keys = function(obj) {
            var r = 0;
            for (var k in obj) r++;
            return r;
        }



        if ($window.sessionStorage) {
            try {
                $scope.tab =  $window.sessionStorage.getItem('gdgeventsTab');
                if (!$scope.tab) $scope.tab = 'info';
                $scope.e = JSON.parse($window.sessionStorage.getItem('gdgevent'+$routeParams.eventId));
            } catch(err) {};
        }
        $scope.$watch('tab', function(tab) {
            if ($window.sessionStorage) $window.sessionStorage.setItem('gdgeventsTab', tab);
        });
        $scope.refresh = function() {
            $scope.loading = true;
            GEvent.get({id: $routeParams.eventId}, function (e) {
                $scope.loading = false;
                e.date = $filter('date')(e.date,'yyyy-MM-dd');
                e.closereg = $filter('date')(e.closereg,'yyyy-MM-dd');
                self.original = e;
                $scope.e = new GEvent(self.original);

                $window.sessionStorage.setItem('gdgevent'+$routeParams.eventId, JSON.stringify(e));

            });
        };
        $scope.filterEvent = function(p) {
           if ($scope.eFilter == "all") return true;
           if ($scope.eFilter == "approved") return $scope.accepted[p.id];
           else return !$scope.accepted[p.id]
        }
        $scope.eFilter = "all";
        $scope.toAccept = {};
        $scope.accepted = {};

        $scope.$watch('e.registrations', function(regs) {
           var r = {};
           for (var i in regs)
            if (regs[i].accepted) r[regs[i].googler_id] = true;
           $scope.accepted = r;
        });


        $scope.$watch('toAccept', function(v) {
           var r = [];
           for(var k in v)
            if (v[k]) r.push(k);
           $scope.toAcceptArray = r;
           if ($scope.e)
            $scope.allSelected = r.length == ($scope.keys($scope.e.registrations)-$scope.keys($scope.accepted));
        },true);


        $scope.approve = function() {
            if ($scope.toAcceptArray.length == 0) return;
            $scope.approving = true;

            $http.post('/api/events/'+$routeParams.eventId+'/approve',{participants:$scope.toAcceptArray,sendEmail: $scope.sendEmail})
                .success(function(res) {
                    var success = res.ok;
                    $scope.approving = false;
                    if (success) {
                        $scope.toAcceptArray.forEach(function(p) {
                            $scope.accepted[p] = true;
                        });
                        $scope.toAccept = {};
                        $scope.allSelected = false;
                    }
                    $scope.sendingFailed = !success;

                    $scope.refresh();
                });
        };

        $scope.selectAll = function() {
            $scope.toAccept = {};
            for(var i in $scope.e.registrations) {
                if (!$scope.e.registrations[i].accepted) $scope.toAccept[$scope.e.registrations[i].googler_id] = $scope.allSelected;
            }
        }


        $scope.refresh();

        $scope.isClean = function () {
            return angular.equals(self.original, $scope.e);
        }

        $scope.destroy = function () {
            self.original.$remove(function () {
                $location.path('/list');
            });
        };

        $scope.save = function () {
            $scope.e.$update(function () {
                $window.sessionStorage.setItem('gdgevent'+$routeParams.eventId, JSON.stringify($scope.e));
                $location.path('/');
            });
        };
        $scope.show = function(id) {
            $location.path('/participants/'+id);
        }

        $scope.showCard = function(id) {
            var reg;
            $scope.e.registrations.forEach(function(r) { if (r.googler_id==id) reg = r;})
            if (reg) {
                $window.open("/card/"+reg.cardUrl);
            }
        }


    })
    .controller('notificationResendCtrl',function($scope,$http,$routeParams){
        $scope.resend = function(id) {
            var reg;
            $scope.sending = true;
            $scope.e.registrations.forEach(function(r) { if (r.googler_id==id) reg = r;})
            if (reg) {
                $http.post('/api/events/' + $routeParams.eventId+'/resend',{id:id})
                    .then(function(){
                        $scope.sending = false;
                        $scope.dismiss();
                    })
            }
        }
    })


    .factory('GEvent', function ($resource) {
        var GEvent = $resource('/api/events/:id',
            {  id: "@id" }, {
                update: { method: 'PUT' }
            }
        );
        return GEvent;
    });
