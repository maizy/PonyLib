package main

import (
	"flag"
	"fmt"
	"os"
	"path"

	"dev.maizy.ru/ponylib/fb2_parser/metadata"
)

func main() {
	flag.Parse()
	files := flag.Args()
	if len(files) < 1 {
		_, _ = fmt.Fprintf(os.Stderr, "Usage: %s FILE [FILE]\n", path.Base(os.Args[0]))
		os.Exit(2)
	}
	for _, file := range files {
		fp, err := os.Open(file)
		if err != nil {
			_, _ = fmt.Fprintf(os.Stderr, "%s: unable to open file. %s\n", file, err)
			continue
		}
		parseMetadata, err := metadata.ParseMetadata(fp)
		if err != nil {
			_, _ = fmt.Fprintf(os.Stderr, "%s: unable to parse metadata: %s\n", file, err)
			continue
		}
		fmt.Printf("%s: %s\n", file, parseMetadata)
	}
}
