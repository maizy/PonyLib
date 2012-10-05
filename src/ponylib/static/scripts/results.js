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
        this._loaderHtml = '';
    };

    n.prototype.onReady = function() {

        this._loaderHtml = jQuery('.loader').html();
        if (jQuery.ias) {
            this._paginator = jQuery.ias({
                container : '.books-list',
                item: '.book-row',
                pagination: '.pagination',
                next: 'li.next a',
                loader: '',
                customLoaderProc:_.bind(this._showLoaderAndScroll, this)
            });
        }

        return this;
    };

    n.prototype._showLoaderAndScroll = function() {
        var loader = $(".ias_loader");

        if (loader.length == 0) {
            loader = $("<div class='ias_loader'>"+this._loaderHtml+"</div>");
            loader.css('visible', 'none');
        }
        var lastEl = $('.books-list').find('.book-row').last();
        lastEl.after(loader);
        //fix iOS Safari problem with partially visible loader
        loader.fadeIn(function() {
            jQuery("html, body").animate({ scrollTop: $(document).height() }, "slow");
        });
    };

    /**
     * @return {jQuery.ias.paging}
     */
    n.prototype.getPaginator = function() {
        return self._paginator;
    };

    return n;
}()));