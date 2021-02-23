package ponylib_app

import "strings"

func NormalizeVersion(version string) string {
	if version == "" || !strings.HasPrefix(version, "v") {
		return "pre-release-" + version
	}
	return version
}
