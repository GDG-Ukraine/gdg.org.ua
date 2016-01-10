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
                try {
                    e.date = $filter('date')(e.date.date, 'yyyy-MM-dd');
                } catch(e) {
                    e.date = $filter('date')(e.date, 'yyyy-MM-dd');
                }
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
               $scope.e.fields.push({type:'text'});
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
           });

           $scope.types = [
               {type:'text', name: 'Text'},
               {type:'checkbox', name: 'Checkbox'},
               {type:'select', name: 'Select'},
           ];
           $scope.addOption = function(field) {
               if (!field.options) field.options = [];
               field.options.push("");
           };
           $scope.removeOption = function(field, index) {
               field.options.splice(index,1);
           }
           $scope.formFields =[
               {name:'phone',title:'Telephone'},
               {name:'gplus',title:'Google+'},
               {name:'hometown',title:'Hometown'},
               {name:'company',title:'Company'},
               {name:'position',title:'Position'},
               {name:'www',title:'WWW'},
               {name:'experience_level',title:'Experience Level'},
               {name:'experience_desc',title:'Experience Description'},
               {name:'interests',title:'Interests'},
               {name:'events_visited',title:'Events visited'},
               {name:'english_knowledge',title:'English knowledge'},
               {name:'t_shirt_size',title:'T-shirt size'},
               {name:'gender',title:'Gender'},
               {name:'additional_info',title:'Additional Information'}
           ];
           var getHidden = function() {
               if (!$scope.e.hidden) $scope.e.hidden =  [];
               return $scope.e.hidden;
           }
           $scope.isHidden = function(field) {
               if (!$scope.e || !$scope.e.hidden) return false;

               return getHidden().indexOf(field.name) >= 0;
           }
           $scope.toggleHiddenField = function(e,field) {
               var h = getHidden();
               if (h.indexOf(field.name)==-1)
                   h.push(field.name);
               else
                   h.splice(h.indexOf(field.name),1);
               $scope.e.hidden = h;
           }

           // fix for fields without type
           $scope.$watch('e.fields', function(fields) {
               if (fields) angular.forEach(fields,function(field) { if (!field.type) field.type='text'});
           });


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
        $scope.fromEmail = $window.localStorage.getItem('fromEmail');
        if (!$scope.fromEmail) $scope.fromEmail = "kyiv@gdg.org.ua";
        $scope.$watch('fromEmail',function(nv) {
            $window.localStorage.setItem('fromEmail',nv);
        })

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
                try {
                    e.date = $filter('date')(e.date.date,'yyyy-MM-dd');
                } catch(e) {
                    e.date = $filter('date')(e.date, 'yyyy-MM-dd');
                }

                try {
                    e.closereg = $filter('date')(e.closereg.date, 'yyyy-MM-dd');
                } catch(e) {
                    e.closereg = $filter('date')(e.closereg,'yyyy-MM-dd');
                }
                self.original = e;
                $scope.e = new GEvent(self.original);

                $window.sessionStorage.setItem('gdgevent'+$routeParams.eventId, JSON.stringify(e));

            });
        };
        $scope.filterEvent = function(p) {
           if ($scope.eFilter == "all") return true;
           //if ($scope.eFilter == "approved") return $scope.accepted[p.id];
           //else return !$scope.accepted[p.id]
           if ($scope.eFilter == "approved") return p.accepted;
           else return !p.accepted;

        }
        $scope.eFilter = "all";
        $scope.toAccept = {};

        $scope.$watch('e.registrations', function(regs) {
           $scope.accepted = regs? regs.filter(function(r) { return r.accepted; }).length : 0;
        });


        $scope.$watch('toAccept', function(v) {
           var r = [];
           for(var k in v)
            if (v[k]) r.push(k);
           $scope.toAcceptArray = r;
           console.log(r);
           if ($scope.e)
                $scope.allSelected = r.length == ($scope.keys($scope.e.registrations)-$scope.accepted);
        },true);


        $scope.approve = function() {
            if ($scope.toAcceptArray.length == 0) return;
            $scope.approving = true;

            $http.post('/api/events/'+$routeParams.eventId+'/approve',{
                registrations:$scope.toAcceptArray,sendEmail: $scope.sendEmail,
                fromEmail:$scope.fromEmail
            })
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
        $scope.sendConfirm = function() {
            if ($scope.toAcceptArray.length == 0) return;
            $scope.sending = true;

            $http.post('/api/events/'+$routeParams.eventId+'/send-confirm',{
                registrations:$scope.toAcceptArray,sendEmail: $scope.sendEmail,
                fromEmail:$scope.fromEmail
            })
                .success(function(res) {
                    var success = res.ok;
                    $scope.sending = false;
                    if (success) {
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
                if (!$scope.e.registrations[i].accepted) $scope.toAccept[$scope.e.registrations[i].id] = $scope.allSelected;
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
            $scope.e.registrations.forEach(function(r) { if (r.id==id) reg = r;});
            if (reg) {
                $window.open("/card/"+reg.cardUrl);
            } else {
                console.log("No registrant found for "+id);
            }
        };
        $scope.openReportParticipants = function() {
            /*$window.open('events/participants.html');
            $window.getEventData = function(cb) {
                cb($scope.e);
            } */
            $scope.reporting = true;
            $http.post('/api/events/'+$routeParams.eventId+'/report?mode='+$scope.eFilter).then(function(r) {
                $scope.reporting = false;
                if (r.data.url)
                    $window.open(r.data.url);
                else {
                    console.log("Error while sending to Google Drive:",r.data);
                    alert('Error while sending to Drive. Please open console for more details.');
                }
            });
        }

        $scope.generateInvites = function(n) {
            $http.post('/api/events/'+$routeParams.eventId+'/invites', {number: n})
                .then(function(r) {
                    console.log("Invites generated", r);
                    if (!r.data.ok) {
                        console.log("Error while generating invites:",r.data);
                        alert('Error while generating invites. Please open console for more details.');

                    } else {
                        alert(n+" invites generated");
                        $scope.refresh();
                    }

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
                $http.post('/api/events/' + $routeParams.eventId+'/delete',{id:id})
                    .then(function(r){
                        console.log(r.data);
                        if (!r.data.ok) alert("Can't delete application");
                        $scope.deleting = false;
                        //$scope.e.registrations.splice($scope.e.registrations.indexOf(reg),1);
                        $scope.refresh();
                        $scope.dismiss();
                    })
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

