angular.module("module.models")
.factory('userModel', ['$http', '$log', '$q', function ($http, $log, $q) {
	"use strict";

	var base_url = "/users";
	var service = {};

	service.getUser = function (userId) {
		return $http.get(base_url+'/'+userId).success(function (response) {
			return response;
		}).error(function (response) {
			$log.error("Error fetching user: ", response);
		});
	};

    service.getCurrentUser =  function () {
        return $http.get('/users/currentUser').then(function (response) {
            return response.data;
        }, function (response) {
            return $q.reject(response);
        });
    };

    service.getAgents = function (userId) {
        $http.get(base_url+'/'+userId).success(function (response) {
            return response;
        }).error(function (response) {
            $log.error("Error fetching user: ", response);
        });
    };

	service.login = function (phone, password) {
		return $http({method: 'POST', url: '/users/login', data: {phone: phone, password: password}})
		.success(function (response) {
			return response;
		})
		.error(function (response, status) {
			return $q.reject(status);
		});
	};

	service.logout = function () {
		return $http.get('/users/logout')
		.success(function (response) {
			return response;
		})
		.error(function (response) {
			$log.error("Error loggin out: ", response);
		});
	};

	service.getActiveAgents = function () {
		return $http.get(base_url+'/active-agents').success(function (response) {
			return response;
		}).error(function (response) {
			$log.error("Error fetching user: ", response);
		});
	};

	return service;
}]);