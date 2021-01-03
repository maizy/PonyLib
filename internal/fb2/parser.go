package fb2

import (
	"fmt"
	"io"
	"strings"

	"github.com/antchfx/xmlquery"

	"dev.maizy.ru/ponylib/fb2_parser"
	"dev.maizy.ru/ponylib/internal/binary"
	"dev.maizy.ru/ponylib/internal/u"
)

func ScanBookMetadata(source io.Reader) (*fb2_parser.Fb2Metadata, error) {
	xmlParser, err := xmlquery.CreateStreamParser(source, "/FictionBook/description/title-info|/FictionBook/binary")
	if err != nil {
		return nil, fmt.Errorf("XML parse error: %w", err)
	}
	// http://www.fictionbook.org/index.php/%D0%AD%D0%BB%D0%B5%D0%BC%D0%B5%D0%BD%D1%82_title-info
	var titleInfoNode *xmlquery.Node

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

			// look for converimage binary id
			coverpageImage := xmlquery.FindOne(titleInfoNode, "//coverpage/image")
			if coverpageImage != nil {
				id := coverpageImage.SelectAttr("href")
				if strings.HasPrefix(id, "#") {
					coverBinaryId = u.StrPtr(id[1:])
				}
			}
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
	if titleInfoNode != nil {
		if title := findText(titleInfoNode, "//book-title"); title != nil {
			book = &fb2_parser.Book{Title: title}
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
	}

	cover := parseCover(coverNode)

	return &fb2_parser.Fb2Metadata{
		Book:    book,
		Cover:   cover,
		Authors: bookAuthors}, nil
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

func findText(node *xmlquery.Node, query string) *string {
	if match := xmlquery.FindOne(node, query); match != nil {
		return u.StrPtr(match.InnerText())
	}
	return nil
}
