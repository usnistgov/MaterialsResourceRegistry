;(function($, window, document, undefined) {
"use strict";

$.widget("ui.tagit", $.ui.tagit,
	{
	/** @type {string} */
	version: "@VERSION",

	isNew: function(name) {
        return !this._findTagByLabel(name);
    },

    createTag: function(value, additionalClass, duringInitialization, custom_id) {
        this._super(value, additionalClass, duringInitialization);
        var existingTag = this._findTagByLabel(value);
        if(existingTag && (custom_id != undefined) )
            existingTag.attr("custom_id", custom_id);
    },

    hasTag: function() {
        return this.assignedTags().length > 0;
    }
});

})(jQuery, window, document);