angular.module("OrdersApp")
.controller("ordersController", ["$scope",
	"authService",
	'orderModel',
	'$interval',
	function ($scope, authService, orderModel, $interval) {
	"use strict";

	var nextPage, currentList;
	var latestOrder = 1000000;
	$scope.showprogressloadmore = false;
	$scope.showprogress = false;
	$scope.showloadmore = false;

	$scope.typeOfLists = {'All': orderModel.listAll,
	 'Open': orderModel.listOpen,
	 'Closed': orderModel.listClosed,
	 'Pending': orderModel.listPending
	}

	var showProgress = function (progressVar) {
		$scope[progressVar] = true;
	}

	var hideProgress = function (progressVar) {
		$scope[progressVar] = false;
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

	$interval(enquireNewOrders, 30*1000);

	$scope.getNewOrders = function () {
		$scope.orders = [];
		$scope.listAll(currentList);
		$scope.showneworders = false;
	}

	$scope.listAll = function (listType, progressVar, page) {
		if (! page) {
			hideLoadMore();
		}
		
		if (currentList != listType) {
			$scope.orders = [];
		}
		
		currentList = listType;
		var getter = $scope.typeOfLists[listType];

		showProgress(progressVar);
		getter(page).then(function (orders) {
			if ($scope.orders && $scope.orders.length != 0) {
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
			} else {
				hideLoadMore();
			}

			hideProgress(progressVar);
		}, function () {
			hideProgress(progressVar);
		})
	}

	$scope.listAll('All', "showprogress");

	$scope.loadMore = function () {
		$scope.listAll(currentList, "showprogressloadmore", nextPage);
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

	var getAgentDirections = function (order) { 
 	    // var url = "http://maps.googleapis.com/maps/api/directions/json?sensor=false&origin=" +
 	    // order.agent.latitude + "," + order.agent.longitude + "&destination=" + 
 	    // order.destination_lat + "," + order.destination_long;

 	    var url = "https://maps.googleapis.com/maps/api/directions/json?origin=Adelaide,SA&destination=Adelaide,SA&key=AIzaSyCK1V3YCn_Zb_2B8sGz1lXj72ETiqsrWuE";
	    return url;
	}

    $scope.getLocationUrl = function (order) {
    	 if (!order.agent) {
	    	return "https://maps.google.com/maps?q=" + 
	    	order.destination_lat +
	    	"," + order.destination_long + 
	    	"&hl=es;z=8&amp&output=embed";
	    }

	    return getAgentDirections(order);
    };

    var showAgentLoader = function (order) {
    	order.showagentloader = true;
    }

    var hideAgentLoader = function (order) {
    	order.showagentloader = false;
    }

    $scope.assignAgent = function (event, order, user_id) {
    	showAgentLoader(order);
    	event.stopPropagation();
    	orderModel.assignAgent(order, user_id).then(function (updated_order) {
    		hideAgentLoader(order);
    		console.log('got response', updated_order);

    		order = updated_order;

    	}, function (error) {
    		hideAgentLoader(order);
    		console.log('got error', error);
    	})
    };

}]).filter('trusted', ['$sce', function ($sce) {
    return function(url) {
        return $sce.trustAsResourceUrl(url);
    };
}]);