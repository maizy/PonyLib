(function (root) {
    if (_.isUndefined(root.ns)) {
        // based on
        // https://github.com/shichuan/javascript-patterns/blob/master/object-creation-patterns/namespace.html
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