package main

import (
	"dev.maizy.ru/ponylib/cmd/ponylib/cmd"
)

var Version string = "unknown"

func main() {
	_ = cmd.Execute(Version)
}
