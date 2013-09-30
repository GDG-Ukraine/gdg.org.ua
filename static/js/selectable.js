var app = angular.module('gdgorgua');

app.directive('selectable', function() {
  return {
    restrict: 'E',
    scope: {
      'source': '=',
      'model': '=',
      'customEnabled': '@custom'
    },
    template: '\
    <div>\
      <div ng-repeat="option in source">\
        <input ng-show="multiple" type="checkbox" ng-model="checked[$index]">\
        <input ng-hide="multiple" type="radio" ng-model="current.selected" value="{{option}}">{{option}}\
      </div>\
      <div ng-show="customEnabled">\
      <input ng-show="multiple" type="checkbox" ng-model="customChecked" ng-disabled="!custom">\
      <input ng-hide="multiple" type="radio" ng-disabled="!custom" ng-checked="custom == current.selected" ng-click="selectCustom()">\
      <input ng-model="custom"></div>\
    </div>', 
    link:function(scope, tElem, tAttr, ctrl) {
      scope.checked = {};
      scope.current = {selected:""};
      scope.multiple = tAttr.multiple == 'true';
      function update() {
        if (scope.multiple) {
        checked = scope.checked;
        if (checked) {
          var result = scope.model;
          if (!scope.model || !angular.isArray(result)) result = scope.model = [];
          result.length = 0;
          for(var kn in checked) {
            if (checked[kn]) result.push(scope.source[kn|0]);
          }
          if (scope.customChecked && scope.customEnabled) result.push(scope.custom);
        }}
        else {
          scope.model = scope.current.selected;
        }
      }
      scope.$watch('checked', update, true);
      scope.$watch('customChecked', update);
      scope.$watch('customEnabled', update);
      scope.$watch('current.selected', update);
      scope.$watch('custom', function(nv, ov) {
        if (!scope.multiple && ov == scope.current.selected) scope.current.selected = nv;
      })
      scope.selectCustom = function() {
        scope.current.selected = scope.custom;
      }
    }
  }
});
