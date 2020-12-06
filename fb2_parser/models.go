package fb2_parser

import "fmt"

type Book struct {
	Title  string
	Author Author
}

func (r *Book) String() string {
	return fmt.Sprintf("«%s» by %s", r.Title, r.Author)
}

type Author struct {
	Fullname string
}

func (a *Author) String() string {
	return a.Fullname
}
