package ponylib_app

import "strings"

// autogen on build
var version string = "unknown"

func NormalizeVersion(version string) string {
	if version == "" || !strings.HasPrefix(version, "v") {
		return "pre-release-" + version
	}
	return version
}

var normalizedVersion = NormalizeVersion(version)

func GetVersion() string {
	return normalizedVersion
}
