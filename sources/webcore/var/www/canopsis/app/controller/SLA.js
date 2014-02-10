//need:app/lib/controller/cgrid.js,app/view/Rule/Grid.js,app/view/Rule/Form.js,app/store/Rules.js
/*
# Copyright (c) 2011 "Capensis" [http://www.capensis.com]
#
# This file is part of Canopsis.
#
# Canopsis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Canopsis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Canopsis.  If not, see <http://www.gnu.org/licenses/>.
*/
Ext.define('canopsis.controller.SLA', {
	extend: 'canopsis.lib.controller.cgrid',

	views: ['SLA.Grid', 'SLA.Form'],
	stores: ['SLA'],
	models: ['SLA'],

	logAuthor: '[controller][sla]',

	storeDefaultAction: undefined,

	init: function() {
		log.debug('Initialize ...', this.logAuthor);

		this.formXtype = 'SLAForm';
		this.listXtype = 'SLAGrid';

		this.modelId = 'SLA';

		this.callParent(arguments);
	}
});