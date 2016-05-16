angular.module("module.models")
.factory('orderModel', ['$http', '$log', '$q', function ($http, $log, $q) {
	"use strict";

	var base_url = "/orders";
	var service = {};

    var status = {'PN': 'Pending',
        'AC': 'Accepted',
        'PK': 'Picked',
        'PR': 'Purchased',
        'DV': 'Delivery',
        'CM': 'Completed',
        'CN': 'Cancelled'
    };
    service.status = status;

    var statusColor = {'PN': '#003366',
        'AC': '#b32d00',
        'PK': '#604020',
        'PR': '#664400',
        'DV': '#4d2600',
        'CM': '#004d00',
        'CN': '#660000'
    };
    service.statusColor = statusColor;

    var orderType = {'PU': 'Purchase',
        'DL': 'Delivery'
    }
    service.orderType = orderType;

    service.listAll = function (page) {
        page = page || 1;
        return $http.get('/orders?page=' + page).then(function (response) {
            return response.data;
        }, function (error) {
            return $q.reject(error);
        });
    };

    service.listOpen = function (page) {
        page = page || 1;
        return $http.get('/orders/open?page=' + page).then(function (response) {
            return response.data;
        }, function (error) {
            return $q.reject(error);
        });
    };

    service.listClosed = function (page) {
        page = page || 1;
        return $http.get('/orders/closed?page=' + page).then(function (response) {
            return response.data;
        }, function (error) {
            return $q.reject(error);
        });
    };

    service.listPending = function (page) {
        page = page || 1;
        return $http.get('/orders/pending?page=' + page).then(function (response) {
            return response.data;
        }, function (error) {
            return $q.reject(error);
        });
    };

    service.listCancelled = function (artId) {
        page = page || 1;
        return $http.get('/orders/' + artId + '/associates').then(function (response) {
            return response.data;
        }, function (error) {
            return $q.reject(error);
        });
    };

    service.get = function (orderId) {
        return $http.get('/orders/' + orderId).then(function (response) {
            return response.data;
        }, function (error) {
            return $q.reject(error);
        });
    };

	return service;
}]);