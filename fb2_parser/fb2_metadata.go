package fb2_parser

import (
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/mitchellh/go-wordwrap"

	"dev.maizy.ru/ponylib/internal/u"
)

type Book struct {
	Title         string     `json:"title"`
	Lang          *string    `json:"lang,omitempty"`
	FormattedDate *string    `json:"formatted_date,omitempty"`
	Date          *time.Time `json:"date,omitempty"`
}

func (b *Book) String() string {
	return b.Title
}

func (b *Book) WrittenAt() string {
	if b.Date != nil {
		if b.Date.Month() == time.January && b.Date.Day() == 1 {
			return b.Date.Format("2006")
		}
		return b.Date.Format("2006-01-02")
	} else if b.FormattedDate != nil {
		return *b.FormattedDate
	}
	return ""
}

func (b *Book) AdditionalInfoString() *string {
	if b.Date != nil || b.FormattedDate != nil || b.Lang != nil {
		var sb strings.Builder
		if b.Lang != nil {
			sb.WriteString("Lang: ")
			sb.WriteString(*b.Lang)
		}
		if b.Date != nil || b.FormattedDate != nil {
			if sb.Len() > 0 {
				sb.WriteString(", ")
			}
			sb.WriteString("Written at: ")
			sb.WriteString(b.WrittenAt())
		}
		return u.StrPtr(sb.String())
	}
	return nil
}

type PubInfo struct {
	Publisher *string `json:"publisher,omitempty"`
	PubYear   *int    `json:"pub_year,omitempty"`
	ISBN      *string `json:",omitempty"`
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
	Name   string `json:"name"`
	Number *int   `json:"n,omitempty"`
}

func (s *Sequence) String() string {
	var sb strings.Builder
	sb.WriteString(s.Name)
	if s.Number != nil {
		sb.WriteString(" [")
		sb.WriteString(strconv.Itoa(*s.Number))
		sb.WriteString("]")
	}
	return sb.String()
}

type Author struct {
	FirstName  *string `json:"first,omitempty"`
	LastName   *string `json:"last,omitempty"`
	MiddleName *string `json:"middle,omitempty"`
	Nickname   *string `json:"nick,omitempty"`
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

// TODO: https://github.com/maizy/PonyLib/issues/61
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
	Book       *Book               `json:"book"`
	PubInfo    *PubInfo            `json:"pub_info,omitempty"`
	Authors    *[]Author           `json:"authors,omitempty"`
	Genres     *[]GenreIndexEntity `json:"genres,omitempty"`
	Sequences  *[]Sequence         `json:"sequences,omitempty"`
	Annotation *string             `json:"annotation,omitempty"`
}

func (f *Fb2Metadata) String() string {
	var sb strings.Builder
	var titleSb strings.Builder
	var maxWidth uint = 100

	if f.Book != nil {
		titleSb.WriteString("«")
		titleSb.WriteString(f.Book.String())
		titleSb.WriteString("»")
	} else {
		titleSb.WriteString("?")
	}
	if f.Authors != nil {
		titleSb.WriteString(" by ")
		for index, author := range *f.Authors {
			if index > 0 {
				titleSb.WriteString(", ")
			}
			titleSb.WriteString(author.String())
		}
	}
	sb.WriteString(wordwrap.WrapString(titleSb.String(), maxWidth))
	if f.Book != nil {
		if additionalInfo := f.Book.AdditionalInfoString(); additionalInfo != nil {
			sb.WriteString("\n\t")
			sb.WriteString(*additionalInfo)
		}
	}
	if f.PubInfo != nil {
		sb.WriteString("\n\t")
		sb.WriteString(f.PubInfo.String())
	}
	if f.Genres != nil {
		sb.WriteString("\n\tGenres:\n")
		for index, genre := range *f.Genres {
			if index > 0 {
				sb.WriteString("\n")
			}
			sb.WriteString("\t  * ")
			sb.WriteString(genre.String())
		}
	}
	if f.Sequences != nil {
		sb.WriteString("\n\tSequences: ")
		for index, sequence := range *f.Sequences {
			if index > 0 {
				sb.WriteString(", ")
			}
			sb.WriteString(sequence.String())
		}
	}
	if f.Annotation != nil {
		sb.WriteString("\n\tAnnotation:\n")
		wrapped := wordwrap.WrapString(*f.Annotation, maxWidth-10)
		sb.WriteString("\t  ")
		sb.WriteString(strings.ReplaceAll(wrapped, "\n", "\n\t  "))
	}
	return sb.String()
}
