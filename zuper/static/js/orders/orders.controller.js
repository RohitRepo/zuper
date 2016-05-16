angular.module("OrdersApp")
.controller("ordersController", ["$scope",
	"authService",
	'orderModel',
	'$interval',
	function ($scope, authService, orderModel, $interval) {
	"use strict";

	var nextPage, currentList;
	var latestOrder = 1000000;

	$scope.typeOfLists = {'All': orderModel.listAll,
	 'Open': orderModel.listOpen,
	 'Closed': orderModel.listClosed,
	 'Pending': orderModel.listPending
	}

	var showProgress = function () {
		$scope.showprogress = true;
	}

	var hideProgress = function () {
		$scope.showprogress = false;
	}

	var showLoadMore = function () {
		$scope.showloadmore = true;
	}

	var hideLoadMore = function () {
		$scope.showloadmore = false;
	}

	var enquireNewOrders = function () {
		var getter = $scope.typeOfLists[currentList];

		getter().then(function (orders) {
			console.log('getter response 1', orders);
			if (orders.results && orders.results.length != 0) {
				var latestOrdernResults = orders.results[0].id;
			} else {
				latestOrdernResults = -1;
			}

			if (latestOrder < latestOrdernResults) {
				$scope.showneworders = true;
			}

		}, function () {
		})
	}

	$interval(enquireNewOrders, 5*1000);

	$scope.getNewOrders = function () {
		$scope.orders = [];
		$scope.listAll(currentList);
		$scope.showneworders = false;
	}

	$scope.listAll = function (listType, page) {
		if (currentList != listType) {
			$scope.orders = [];
		}
		
		currentList = listType;
		var getter = $scope.typeOfLists[listType];

		showProgress();
		getter(page).then(function (orders) {
			console.log('getter response', orders);
			if ($scope.orders && $scope.orders.length != 0) {
				console.log("get here", $scope.orders);
				$scope.orders.push.apply($scope.orders, orders.results);
			} else {
				$scope.orders = orders.results; 
				if ($scope.orders && $scope.orders.length != 0) {
					latestOrder = orders.results[0].id;
				} else {
					latestOrder = 1000000;
				}
			}

			if (orders.next) {
				showLoadMore();
				nextPage = orders.next.slice(-1)
				console.log('nextPage', nextPage);
			} else {
				hideLoadMore();
			}

			hideProgress();
		}, function () {
			hideProgress();
		})
	}

	$scope.listAll('All');

	$scope.loadMore = function () {
		$scope.listAll(currentList, nextPage);
	}


	$scope.showDetail = function (order) {
		order.showDetail = true;

		if ($scope.selectedOrder) {
			$scope.selectedOrder.showDetail = false;
		}

		if ($scope.selectedOrder == order) {
			$scope.selectedOrder = ''
		} else {
			$scope.selectedOrder = order;
		}
	}

	$scope.setStatus = function (statusCode) {
		return orderModel.status[statusCode];
	}

	$scope.setOrderType = function (orderCode) {
		return orderModel.orderType[orderCode];
	}

	$scope.setStatusColor = function (orderCode) {
		return orderModel.statusColor[orderCode];
	}

	$scope.openMenu = function($mdOpenMenu, ev) {
      var originatorEv = ev;
      $mdOpenMenu(ev);
    };

    $scope.logout = function () {
    	authService.logout();
    }
}]);