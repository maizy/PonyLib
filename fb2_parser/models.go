package fb2_parser

import (
	"fmt"
	"strings"
)

type Book struct {
	Title *string
}

func (r *Book) String() string {
	return *r.Title
}

type Author struct {
	FirstName  *string
	LastName   *string
	MiddleName *string
	Nickname   *string
}

func (a *Author) String() string {
	if a.Nickname != nil {
		return *a.Nickname
	} else {
		parts := make([]string, 0)
		if a.FirstName != nil {
			parts = append(parts, *a.FirstName)
		}
		if a.MiddleName != nil {
			parts = append(parts, *a.MiddleName)
		}
		if a.LastName != nil {
			parts = append(parts, *a.LastName)
		}
		if len(parts) == 0 {
			return ""
		}
		return strings.Join(parts, " ")
	}
}

type Cover struct {
	Base64Content string
	ContentType   string
}

func (c *Cover) String() string {
	return fmt.Sprintf("<%d bytes>", len(c.Base64Content))
}

func (c *Cover) Size() int {
	return 3 * len(c.Base64Content) / 4
}

func (c *Cover) SizeFormatted() string {
	size := c.Size()
	if size == 0 {
		return "0 bytes"
	} else if size == 1 {
		return "1 byte"
	}
	return fmt.Sprintf("%d bytes", size)
}

type Fb2Metadata struct {
	Book    *Book
	Authors *[]Author
	Cover   *Cover
}

func (f *Fb2Metadata) String() string {
	var sb strings.Builder
	sb.WriteString("Fb2(")
	if f.Book != nil {
		sb.WriteString("«")
		sb.WriteString(f.Book.String())
		sb.WriteString("»")
	} else {
		sb.WriteString("?")
	}
	if f.Authors != nil {
		sb.WriteString(" by ")
		for index, author := range *f.Authors {
			if index > 0 {
				sb.WriteString(", ")
			}
			sb.WriteString(author.String())
		}
	}
	if f.Cover != nil {
		sb.WriteString(", cover: ")
		sb.WriteString(f.Cover.SizeFormatted())
	}
	sb.WriteString(")")
	return sb.String()
}
