package fb2_parser

import (
	"fmt"
	"strconv"
	"strings"
	"time"
)

type Book struct {
	Title         *string
	Lang          *string
	FormattedDate *string
	Date          *time.Time
}

func (r *Book) String() string {
	return *r.Title
}

type PubInfo struct {
	Publisher *string
	PubYear   *int
	ISBN      *string
}

func (p *PubInfo) String() string {
	if p.Publisher != nil || p.PubYear != nil || p.ISBN != nil {
		var sb strings.Builder
		sb.WriteString("Published")
		if p.Publisher != nil {
			sb.WriteString(" by ")
			sb.WriteString(*p.Publisher)
		}
		if p.PubYear != nil {
			sb.WriteString(" at ")
			sb.WriteString(strconv.Itoa(*p.PubYear))
		}
		if p.ISBN != nil {
			sb.WriteString(", ISBN: ")
			sb.WriteString(*p.ISBN)
		}
		return sb.String()
	}
	return ""
}

type Sequence struct {
	Name   string
	Number int
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
	Book       *Book
	PubInfo    *PubInfo
	Authors    *[]Author
	Genries    *[]GenreIndexEntity
	Sequences  *[]Sequence
	Annotation *string
	Cover      *Cover // TODO: https://github.com/maizy/PonyLib/issues/61
}

func (f *Fb2Metadata) String() string {
	var sb strings.Builder
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
	if f.PubInfo != nil {
		sb.WriteString("\n\t")
		sb.WriteString(f.PubInfo.String())
	}
	return sb.String()
}
