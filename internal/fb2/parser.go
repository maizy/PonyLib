package fb2

import (
	"errors"
	"fmt"
	"io"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/antchfx/xmlquery"

	"dev.maizy.ru/ponylib/fb2_parser"
	"dev.maizy.ru/ponylib/internal/binary"
	"dev.maizy.ru/ponylib/internal/u"
)

func ScanBookMetadata(source io.Reader) (*fb2_parser.Fb2Metadata, error) {
	xmlParser, err := xmlquery.CreateStreamParser(source,
		"/FictionBook/description/title-info|"+
			"/FictionBook/description/publish-info|"+
			"/FictionBook/binary")
	if err != nil {
		return nil, fmt.Errorf("XML parse error: %w", err)
	}
	// http://www.fictionbook.org/index.php/%D0%AD%D0%BB%D0%B5%D0%BC%D0%B5%D0%BD%D1%82_title-info
	var titleInfoNode *xmlquery.Node

	// http://www.fictionbook.org/index.php/%D0%AD%D0%BB%D0%B5%D0%BC%D0%B5%D0%BD%D1%82_publish-info
	var publishInfoNode *xmlquery.Node

	// http://www.fictionbook.org/index.php/%D0%AD%D0%BB%D0%B5%D0%BC%D0%B5%D0%BD%D1%82_coverpage
	var coverNode *xmlquery.Node
	var coverBinaryId *string
	var possibleCoverNodes []xmlquery.Node

	for {
		node, err := xmlParser.Read()
		if err != nil {
			break
		}
		switch node.Data {
		case "binary":
			if coverNode == nil {
				id := node.SelectAttr("id")
				// if we already knows cover binary id
				if coverBinaryId != nil && id == *coverBinaryId {
					coverNode = node
					possibleCoverNodes = nil
				} else {
					possibleCoverNodes = append(possibleCoverNodes, *node)
				}
			}

		case "title-info":
			titleInfoNode = node

			// look for cover image binary id
			coverpageImage := xmlquery.FindOne(titleInfoNode, "//coverpage/image")
			if coverpageImage != nil {
				id := coverpageImage.SelectAttr("href")
				if strings.HasPrefix(id, "#") {
					coverBinaryId = u.StrPtr(id[1:])
				}
			}
		case "publish-info":
			publishInfoNode = node
		}
	}

	if coverNode == nil && coverBinaryId != nil && len(possibleCoverNodes) > 0 {
		for _, node := range possibleCoverNodes {
			if node.SelectAttr("id") == *coverBinaryId {
				coverNode = &node
				break
			}
		}
	}

	if coverNode == nil && len(possibleCoverNodes) > 0 {
		for _, node := range possibleCoverNodes {
			if strings.HasPrefix(node.SelectAttr("id"), "cover.") {
				coverNode = &node
				break
			}
		}
	}

	var book *fb2_parser.Book
	var bookAuthors *[]fb2_parser.Author
	var genres *[]fb2_parser.GenreIndexEntity
	var sequences *[]fb2_parser.Sequence
	var annotation *string

	if titleInfoNode != nil {
		var title string
		if foundTitle := findText(titleInfoNode, "//book-title"); foundTitle != nil {
			title = *foundTitle
		}
		// fallback to publish-info/book-name if title is empty or not found
		if title == "" && publishInfoNode != nil {
			if bookName := findText(publishInfoNode, "//book-name"); bookName != nil {
				title = *bookName
			}
		}

		formatted, parsed := parseDate(titleInfoNode)
		lang := findText(titleInfoNode, "//lang")

		if title != "" || formatted != nil || parsed != nil || lang != nil {
			book = &fb2_parser.Book{
				Title:         title,
				Lang:          lang,
				FormattedDate: formatted,
				Date:          parsed,
			}
		}

		authorsNodes := xmlquery.Find(titleInfoNode, "//author")
		var authors []fb2_parser.Author
		for _, authorNode := range authorsNodes {
			if author := parseAuthor(authorNode); author != nil {
				authors = append(authors, *author)
			}
		}
		if len(authors) > 0 {
			bookAuthors = &authors
		}

		genresNodes := xmlquery.Find(titleInfoNode, "//genre")
		var foundGenres []fb2_parser.GenreIndexEntity
		for _, genreNode := range genresNodes {
			if genre, found := fb2_parser.GenreIndexByCode[genreNode.InnerText()]; found {
				foundGenres = append(foundGenres, genre)
			}
		}
		if len(foundGenres) > 0 {
			genres = &foundGenres
		}

		sequenceNodes := xmlquery.Find(titleInfoNode, "//sequence")
		var foundSequences []fb2_parser.Sequence
		for _, sequenceNode := range sequenceNodes {
			if name := findText(sequenceNode, "//@name"); name != nil {
				number := findInt(sequenceNode, "//@number")
				foundSequences = append(foundSequences, fb2_parser.Sequence{*name, number})
			}
		}
		if len(foundSequences) > 0 {
			sequences = &foundSequences
		}

		if annotationNode := xmlquery.FindOne(titleInfoNode, "//annotation"); annotationNode != nil {
			annotation = u.StrPtr(fb2MarkupToText(annotationNode))
		}
	}

	var pubInfo *fb2_parser.PubInfo
	if publishInfoNode != nil {
		publisher := findText(publishInfoNode, "//publisher")
		year := findInt(publishInfoNode, "//year")
		isbn := findText(publishInfoNode, "//isbn")
		if publisher != nil || year != nil || isbn != nil {
			pubInfo = &fb2_parser.PubInfo{publisher, year, isbn}
		}
	}

	cover := parseCover(coverNode)

	if book == nil && pubInfo == nil && cover == nil && bookAuthors == nil && genres == nil &&
		sequences == nil && annotation == nil {
		return nil, errors.New("metadata not found")
	}

	return &fb2_parser.Fb2Metadata{
		Book:       book,
		PubInfo:    pubInfo,
		Cover:      cover,
		Authors:    bookAuthors,
		Genres:     genres,
		Sequences:  sequences,
		Annotation: annotation}, nil
}

func parseCover(coverNode *xmlquery.Node) *fb2_parser.Cover {
	if coverNode != nil {
		content := coverNode.InnerText()
		if len(content) < 1 {
			return nil
		}
		contentType := coverNode.SelectAttr("content-type")
		if contentType == "" {
			contentType = "application/octet-stream"
		}
		return &fb2_parser.Cover{
			Base64Content: binary.CleanBase64String(content),
			ContentType:   contentType,
		}
	}
	return nil
}

// http://www.fictionbook.org/index.php/%D0%AD%D0%BB%D0%B5%D0%BC%D0%B5%D0%BD%D1%82_author
func parseAuthor(node *xmlquery.Node) *fb2_parser.Author {
	if node == nil {
		return nil
	}
	lastName := findText(node, "last-name")
	firstName := findText(node, "first-name")
	middleName := findText(node, "middle-name")
	nickname := findText(node, "nickname")
	if lastName != nil || firstName != nil || middleName != nil || nickname != nil {
		return &fb2_parser.Author{firstName, lastName, middleName, nickname}
	}
	return nil
}

func parseDate(parentNode *xmlquery.Node) (formatted *string, parsed *time.Time) {
	if parentNode == nil {
		return
	}
	formatted = findText(parentNode, "//date")
	if value := findText(parentNode, "//date/@value"); value != nil {
		if parsedDate, err := time.Parse("2006-01-02", *value); err == nil {
			parsed = &parsedDate
		}
	}
	return
}

func fb2ToTextInner(node *xmlquery.Node, sb *strings.Builder, depth int) []string {
	var result []string
	var iterateChildren = false
	postfix := ""
	ifTagMatched := func(regex string) bool {
		matched, _ := regexp.MatchString(regex, node.Data)
		return matched
	}
	switch node.Type {
	case xmlquery.ElementNode:
		switch node.Data {
		// text blocks
		case "p", "ul", "blockquote", "poem", "stanza", "epigraph":
			iterateChildren = true
			postfix = "\n"
		// blocks to ignore, but iterate over children
		case "style", "code":
			iterateChildren = true
		// list elements
		case "li":
			iterateChildren = true
			sb.WriteString("* ")
			postfix = "\n"
		case "title", "subtitle":
			sb.WriteString("\n")
			sb.WriteString(node.InnerText())
			sb.WriteString("\n")
		// special list-like elements (for poem)
		case "v", "text-author", "date":
			sb.WriteString(node.InnerText())
			sb.WriteString("\n")
		case "br", "empty-line":
			sb.WriteString("\n")
		case "strikethrough":
			sb.WriteString("~~")
			iterateChildren = true
			postfix = "~~"
		case "hr":
			sb.WriteString("\n----------\n")
		case "a":
			sb.WriteString(node.InnerText())
			if href := node.SelectAttr("href"); href != "" {
				sb.WriteString(" (")
				sb.WriteString(href)
				sb.WriteString(")")
			}
		// ignored tags
		case "img", "image":
			break
		default:
			switch {
			// headers
			case ifTagMatched(`h\d+`):
				sb.WriteString("\n")
				sb.WriteString(node.InnerText())
				sb.WriteString("\n")
			// just append inner text
			// expect at least: b, strong, emphasis, em, sub, sup
			// all unknown elements produced concatenation of all included text nodes because
			// .InnerText is recursive itself
			default:
				sb.WriteString(node.InnerText())
			}

		}
	case xmlquery.TextNode:
		sb.WriteString(strings.TrimSpace(node.InnerText()))
	case xmlquery.CharDataNode:
		sb.WriteString(strings.TrimSpace(node.InnerText()))
	}

	if iterateChildren && depth < 100 {
		for child := node.FirstChild; child != nil; child = child.NextSibling {
			fb2ToTextInner(child, sb, depth+1)
		}
	}
	sb.WriteString(postfix)
	return result
}

func fb2MarkupToText(root *xmlquery.Node) string {
	var sb strings.Builder
	for child := root.FirstChild; child != nil; child = child.NextSibling {
		fb2ToTextInner(child, &sb, 0)
	}
	return strings.TrimSpace(sb.String())
}

func findText(node *xmlquery.Node, query string) *string {
	if match := xmlquery.FindOne(node, query); match != nil {
		return u.StrPtr(match.InnerText())
	}
	return nil
}

func findInt(node *xmlquery.Node, query string) *int {
	if match := xmlquery.FindOne(node, query); match != nil {
		if value, err := strconv.Atoi(match.InnerText()); err == nil {
			return &value
		}
	}
	return nil
}
