ns('Ponylib.Results', 'Navigation', (function() {

    var n = function Ponylib_Results_Navigation () {
        this._construct(_.toArray(arguments));
    };

    n.prototype._construct = function(opts) {
        $(_.bind(this.onReady, this));

        /**
         * @type {jQuery.ias.paging}
         * @private
         */
        this._paginator = undefined;
    };

    n.prototype.onReady = function() {

        var loaderHtml = jQuery('.loader').html();
        if (jQuery.ias) {
            this._paginator = jQuery.ias({
                container : '.books-list',
                item: '.book-row',
                pagination: '.pagination',
                next: 'li.next a',
                loader: loaderHtml
            });
        }

        return this;
    };

    /**
     * @return {jQuery.ias.paging}
     */
    n.prototype.getPaginator = function() {
        return self._paginator;
    };

    return n;
}()));