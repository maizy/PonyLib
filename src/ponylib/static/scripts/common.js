(function (root) {
    if (_.isUndefined(root.ns)) {
        //

        /**
         * Namaspace manipulation
         *
         * based on
         * https://github.com/shichuan/javascript-patterns/blob/master/object-creation-patterns/namespace.html
         *
         * @param ns_string
         * @param key
         * @param obj
         * @return {Object}
         *
         * Usage:
         *
         *  var AnyObject = {};
         *
         *  //set
         *  ns('Some.Namespace', 'Key', AnyObject);
         *
         *  //get
         *  ns('Some.Namespace.Key') === AnyObject;
         *
         *  //constructor template
         *  ns('Some.Namespace', 'Key', (function() {
         *      var c = function Some_Namespace_Key () {
         *          this._construct(_.toArray(arguments));
         *      };
         *
         *      c.prototype._construct = function(opts) {
         *
         *      };
         *
         *      return c;
         *  }()));
         */
        root.ns = function(ns_string, key, obj) {
            var parts = ns_string.split('.');
            var parent = root;

            _.each(parts, function (part) {
                if (_.isUndefined(parent[part])) {
                    parent[part] = {};
                }
                parent = parent[part];
            });

            if (!_.isUndefined(key)) {
                if (_.isUndefined(parent[key])) {
                    parent[key] = obj;
                }
            }

            return parent;
        };
    }
})(window);