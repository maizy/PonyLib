package metadata

import (
	"io"

	"dev.maizy.ru/ponylib/fb2_parser"
	"dev.maizy.ru/ponylib/internal/fb2"
)

type Fb2Metadata struct {
	Book  fb2_parser.Book
	Cover string
}

func ParseMetadata(source io.Reader) Fb2Metadata {

	// FIXME implements
	return Fb2Metadata{
		Book:  fb2.GetBookInfo(source),
		Cover: fb2.GetCover(source)}
}
