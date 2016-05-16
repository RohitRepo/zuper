angular.module("LoginApp")
.controller("loginController", ["$scope",
	"authService",
	function ($scope, authService) {
	"use strict";

	$scope.login = function (user) {
		// TODO show progress 

		authService.login(user.phone, user.password).then(function () {
			// Hide progressu
		}, function (error) {
			// Hide progress
			// Give error
		});
	};
}]);