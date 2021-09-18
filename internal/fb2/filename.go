package fb2

import (
	"dev.maizy.ru/ponylib/fb2_parser"
	"dev.maizy.ru/ponylib/fb2_scanner/resource"
	"strings"
)

// max filename - len(".fb2")
const filenameLimit = 251

func BuildFileName(rid resource.RId, metadata fb2_parser.Fb2Metadata) string {
	var sb strings.Builder
	if metadata.Book != nil {
		sb.WriteString(metadata.Book.Title)
	}
	authors := metadata.AuthorsString()
	if authors != "" {
		if sb.Len() > 0 {
			sb.WriteString(" - ")
		}
		sb.WriteString(authors)
	}
	if sb.Len() == 0 {
		return rid.ResourceBaseName()
	} else {
		if sb.Len() > filenameLimit {
			return sb.String()[:filenameLimit] + ".fb2"
		} else {
			sb.WriteString(".fb2")
			return sb.String()
		}
	}
}
