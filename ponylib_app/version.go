package ponylib_app

import "strings"

// autogen on build
var version string = "unknown"

func NormalizeVersion(version string) string {
	if version == "unknown" || version == "" {
		return "unknown-version"
	}
	if !strings.HasPrefix(version, "v") {
		return version + ".pre-release"
	}
	return version
}

var normalizedVersion = NormalizeVersion(version)

func GetVersion() string {
	return normalizedVersion
}
