package search

import "fmt"

type BookSearchQuery struct {
	TextMatch string
}

func (s *BookSearchQuery) String() string {
	return fmt.Sprintf("BookSearchQuery(text='%s')", s.TextMatch)
}
