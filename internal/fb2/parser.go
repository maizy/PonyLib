package fb2

import (
	"fmt"
	"io"

	"dev.maizy.ru/ponylib/fb2_parser"
)

func GetBookInfo(source io.Reader) fb2_parser.Book {
	return fb2_parser.Book{
		Title:  fmt.Sprintf("Title from %v", source),
		Author: fb2_parser.Author{Fullname: "Test Author"}}
}

func GetCover(source io.Reader) string {
	return "todo"
}
