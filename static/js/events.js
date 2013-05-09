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
    .factory('EventsFielder', function($http) {
        return function($scope) {
           $scope.addField = function() {
               if (!$scope.e.fields) $scope.e.fields = [];
               $scope.e.fields.push({});
           };
           $scope.deleteField = function(field) {
              var i = $scope.e.fields.indexOf(field);
              if (i>=0) $scope.e.fields.splice(i,1);
           };
           $scope.places = $http.get('/api/places',{cache:true}).then(function(r) { return r.data;});
           $scope.logoForPlace = function(placeId) {
               var place;
               for (var p in $scope.places) if ($scope.places[p] && $scope.places[p].id==placeId) place = $scope.places[p];
               if (place) return place.logo;
           }
           $scope.$watch('e.max_regs', function() {
               if ($scope.e)
                $scope.max_regs_active = $scope.e.max_regs != undefined;
           });
           $scope.switchMaxRegs = function() {
               $scope.e.max_regs = $scope.e.max_regs==null?0:null;
           };
           $scope.$watch('myForm.$invalid', function() {
               console.log("invalid?",$scope.myForm.$invalid);
           })
        };
    })

    .controller('EventsCreateCtrl', function ($scope, $location, GEvent,EventsFielder) {
        EventsFielder($scope);
        $scope.editing = false;
        $scope.enable = true;
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
        $scope.enable = false;

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
                if ($scope.e && $scope.e.title) $scope.enable = true;
            } catch(err) {};
        }
        $scope.$watch('tab', function(tab) {
            if ($window.sessionStorage) $window.sessionStorage.setItem('gdgeventsTab', tab);
        });
        $scope.refresh = function() {
            $scope.loading = true;
            GEvent.get({id: $routeParams.eventId}, function (e) {
                $scope.enable = true;
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
        };

        $scope.showCard = function(id) {
            var reg;
            $scope.e.registrations.forEach(function(r) { if (r.googler_id==id) reg = r;});
            if (reg) {
                $window.open("/card/"+reg.cardUrl);
            }
        };
        $scope.openReportParticipants = function() {
            /*$window.open('events/participants.html');
            $window.getEventData = function(cb) {
                cb($scope.e);
            } */
            $scope.reporting = true;
            $http.post('/api/events/'+$routeParams.eventId+'/report').then(function(r) {
                $scope.reporting = false;
                if (r.data.url)
                    $window.open(r.data.url);
                else alert('Strange response:'+ JSON.stringify(r.data));
            });
        }


    })
    .controller('notificationResendCtrl',function($scope,$http,$routeParams){
        $scope.resend = function(id) {
            var reg;
            $scope.sending = true;
            $scope.e.registrations.forEach(function(r) { if (r.googler_id==id) reg = r;});
            if (reg) {
                $http.post('/api/events/' + $routeParams.eventId+'/resend',{id:id})
                    .then(function(){
                        $scope.sending = false;
                        $scope.dismiss();
                    })
            }
        }
    })
    .controller('notificationDeleteAppCtrl',function($scope,$http,$routeParams){
        $scope.deleteApp = function(id) {
            var reg;
            $scope.deleting = true;
            $scope.e.registrations.forEach(function(r) { if (r.googler_id==id) reg = r;});
            if (reg) {
                $http.post('/api/events/' + $routeParams.eventId+'/delete',{id:id})
                    .then(function(){
                        $scope.deleting = false;
                        $scope.e.registrations.splice($scope.e.registrations.indexOf(reg),1);
                        $scope.refresh();
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

