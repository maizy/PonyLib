ns('ponylib.Visual', 'SetLanguage', (function() {
    var sl = function ponylib_Visual_SetLanguage (opts) {
        this._opts = opts || {};
        this._opts = _.clone(this._opts);

        /** @type {jQuery} */
        this._$wrapper = undefined;

        $(_.bind(this._init, this));
    };

    sl.prototype._init = function() {
        var self = this;
        this._$wrapper = $(this._opts['sel']);
        if (this._$wrapper.length > 0) {
            var $langs = this._$wrapper.find('li a');
            $langs.on('click', function(event) {
                event.stopPropagation();
                var $langA = $(this);
                var code = $langA.attr('href').substring(1);
                code && self.setLanguage(code);
                return false;
            });
        }
    };

    sl.prototype.setLanguage = function(langCode) {
        var self = this;
        $.ajax({
            async: false,
            type: 'POST',
            url: this._opts['url'],
            data: {language: langCode},
            success:_.bind(this.afterSetLanguage, this)
        });
    };

    sl.prototype.afterSetLanguage = function() {
        window.location.reload();
    };

    return sl;
})());

var mainSl = new ponylib.Visual.SetLanguage({
    sel : '#set-language',
    url : '/i18n/setlang/'
});

ns('ponylib.Visual', 'Todo', (function() {
    var td = function() {
        $(_.bind(this._init, this));
    };

    td.prototype._init = function() {
        $('.todo').tooltip({
            placement: 'bottom',
            template: '<div class="tooltip"><div class="tooltip-arrow"></div>' +
                '<div class="tooltip-inner" style="background: red;"></div></div>'
        });
    };

    return new td();
})());

