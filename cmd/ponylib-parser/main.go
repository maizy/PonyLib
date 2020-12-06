package main

import (
	"fmt"
	"os"
	"path"

	"dev.maizy.ru/ponylib/fb2_parser/metadata"
)

func main() {
	if len(os.Args) < 2 {
		_, _ = fmt.Fprintf(os.Stderr, "Usage: %s FILE\n", path.Base(os.Args[0]))
		os.Exit(2)
	}
	var file = os.Args[1]
	fp, err := os.Open(file)
	if err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "Unable to open file. %s\n", err)
		os.Exit(1)
	}
	fmt.Println(file, "metadata")
	fmt.Println(metadata.ParseMetadata(fp))
}
