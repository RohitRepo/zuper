angular.module("OrdersApp")
.controller("ordersController", ["$scope",
	"authService",
	'orderModel',
	'$interval',
	'$mdDialog',
	'$mdMedia',
	function ($scope, authService, orderModel, $interval, $mdDialog, $mdMedia) {
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

 	    var url = "https://maps.googleapis.com/maps/api/directions/json?origin=Adelaide,SA&destination=Adelaide,SA&key=AIzaSyCK1V3YCn_Zb_2B8sGz1lXj72ETiqsrWuE&output=embed";
 	    url = 'https://www.google.com/maps/embed/v1/directions?key=AIzaSyCK1V3YCn_Zb_2B8sGz1lXj72ETiqsrWuE&origin=' +
 	     order.agent.latitude + 
 	     order.agent.longitude +
 	     '&destination=' +
 	     order.destination_lat +
 	     order.destination_long;
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

    var agentQuery;
    $scope.agentQueryCount = 0;

    $scope.assignAgent = function (index, user_id) {
    	var order = $scope.orders[index];
    	showAgentLoader(order);
    	$scope.agentQueryCount = 0;
    	orderModel.assignAgent(order, user_id).then(function () {
    		startAgentQuery(index)
    	}, function (error) {
    		hideAgentLoader(order);
    	})
    };

    $scope.updateOrder = function (index) {
    	var order = $scope.orders[index];

    	orderModel.get(order.id).then(function (updatedOrder) {
    			hideAgentLoader(order);
    			$scope.orders[index] = updatedOrder;
    	}, function () {});
    }


    var getOrder = function (index) {
    	var order = $scope.orders[index];
    	if ($scope.agentQueryCount == 12) {
    		hideAgentLoader(order);
    		return;
    	}

    	$scope.agentQueryCount =  $scope.agentQueryCount +1;

    	orderModel.get(order.id).then(function (updatedOrder) {
    		if (updatedOrder.agent){
    			hideAgentLoader(order);
    			if (agentQuery){
	    			$interval.cancel(agentQuery);
	    		}

    			$scope.orders[index] = updatedOrder;
    		}
    	}, function () {});
    }

    var startAgentQuery = function (index) {
    	agentQuery = $interval(getOrder, 5000, 13, true, index);
    }

    $scope.selectUser = function(ev, index) {
    var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'))  && $scope.customFullscreen;
    $mdDialog.show({
      controller: 'DialogController',
      templateUrl: 'static/js/orders/select.user.html',
      parent: angular.element(document.body),
      targetEvent: ev,
      clickOutsideToClose:true,
      fullscreen: useFullScreen
    })
    .then(function(user) {
      $scope.assignAgent(index, user.id)
    }, function() {
      console.log("No user selected");
    });
  };


}]).filter('trusted', ['$sce', function ($sce) {
    return function(url) {
        return $sce.trustAsResourceUrl(url);
    };
}]).controller('DialogController', [
	'$scope',
	'$mdDialog',
	'userModel',
	function ($scope, $mdDialog, userModel) {

		$scope.noAgents = false;
		$scope.agents = [];

		userModel.getActiveAgents().then(function (response) {
			$scope.agents = response.data;
			console.log('users', $scope.agents);
		}, function () {
			$scope.noAgents = true;
		});

	  $scope.cancel = function() {
	    $mdDialog.cancel();
	  };
	  $scope.answer = function(user) {
	    $mdDialog.hide(user);
	  };
	}
]);