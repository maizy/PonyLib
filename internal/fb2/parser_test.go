package fb2

import (
	"io"
	"os"
	"path"
	"reflect"
	"regexp"
	"strings"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	"dev.maizy.ru/ponylib/fb2_parser"
	"dev.maizy.ru/ponylib/internal/u"
)

func openTestBook(name string) io.Reader {
	file, err := os.Open(path.Join("test", "data", name))
	if err != nil {
		panic(err)
	}
	return file
}

func longText(text string) *string {
	noTabs := regexp.MustCompile("(?m)^\t+").ReplaceAllString(text, "")
	noNL := regexp.MustCompile("(?m)\n").ReplaceAllString(noTabs, " ")
	withExpectedNL := strings.ReplaceAll(noNL, "\\n ", "\n")
	return &withExpectedNL
}

func TestScanBookMetadata(t *testing.T) {
	tests := []struct {
		name    string
		source  io.Reader
		want    *fb2_parser.Fb2Metadata
		wantErr bool
	}{
		{"parse minimal.fb2",
			openTestBook("minimal.fb2"),
			&fb2_parser.Fb2Metadata{
				Book: &fb2_parser.Book{
					Title: "Compulsory",
					Lang:  u.StrPtr("en"),
				},
				Authors: &[]fb2_parser.Author{{LastName: u.StrPtr("Wells")}},
				Genres:  &[]fb2_parser.GenreIndexEntity{fb2_parser.GenreIndexByCode["sf"]},
			},
			false},

		{"parse broken.fb2",
			openTestBook("broken.fb2"),
			nil,
			true},

		{"parse empty.fb2",
			openTestBook("empty.fb2"),
			nil,
			true},

		{"parse full-metadata.fb2",
			openTestBook("full-metadata.fb2"),
			&fb2_parser.Fb2Metadata{
				Book: &fb2_parser.Book{
					Title:         "Compulsory",
					Lang:          u.StrPtr("en"),
					FormattedDate: u.StrPtr("2018"),
					Date:          u.TimePtr(time.Date(2018, 12, 16, 0, 0, 0, 0, time.UTC)),
				},
				PubInfo: &fb2_parser.PubInfo{
					Publisher: u.StrPtr("Wired Magazine"),
					PubYear:   u.IntPtr(2018),
					ISBN:      u.StrPtr("978-1-250-22986-1"),
				},
				Authors: &[]fb2_parser.Author{
					{FirstName: u.StrPtr("Martha"), LastName: u.StrPtr("Wells")},
					{FirstName: u.StrPtr("Some"), MiddleName: u.StrPtr("Co"), LastName: u.StrPtr("Author")},
				},
				Genres: &[]fb2_parser.GenreIndexEntity{
					fb2_parser.GenreIndexByCode["sf"],
					fb2_parser.GenreIndexByCode["sf_cyberpunk"],
				},
				Sequences: &[]fb2_parser.Sequence{
					{"The Murderbot Diaries", u.IntPtr(0)},
					{"Best Of The Best", u.IntPtr(100500)},
				},
				Annotation: longText(`Martha Wells is an American writer of speculative fiction.\n
					She has published a number of fantasy novels, young adult novels, media tie-ins, short stories,
					and nonfiction essays on fantasy and science fiction subjects. Her novels have been translated
					into twelve languages. Wells has won a Nebula Award, two Locus Awards, and two Hugo Awards.\n
					----------\n
					Wikipedia (https://en.wikipedia.org/wiki/Martha_Wells)`),
			},
			false},

		{"normalize whitespaces in with-uncommon-whitespaces.fb2",
			openTestBook("with-uncommon-whitespaces.fb2"),
			&fb2_parser.Fb2Metadata{
				Book: &fb2_parser.Book{
					Title: "TAB=|    |",
					Lang:  u.StrPtr("en"),
				},
				Authors: &[]fb2_parser.Author{{
					FirstName: u.StrPtr("CR=| |"), MiddleName: u.StrPtr("NEL=|\n|"), LastName: u.StrPtr("NBSP=| |")}},
				Genres: &[]fb2_parser.GenreIndexEntity{fb2_parser.GenreIndexByCode["sf"]},
			},
			false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := ScanBookMetadata(tt.source)
			if (err != nil) != tt.wantErr {
				t.Errorf("ScanBookMetadata() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("ScanBookMetadata() got:\n%v\n\nwant:\n%v\n", got, tt.want)
			}
		})
	}
}

func Test_normalizeText(t *testing.T) {
	tests := []struct {
		name   string
		input  string
		output string
	}{
		{"without uncommon whitespaces", "some text", "some text"},
		{"with TAB", "some\ttext", "some    text"},
		{"with CR", "some\rtext", "some text"},
		{"with NBSP", "some\u00A0text", "some text"},
		{"with NEL", "some\u0085text", "some\ntext"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := normalizeXmlText(tt.input); got != tt.output {
				t.Errorf("normalizeXmlText() = %v, want %v", got, tt.output)
			}

			if got := normalizeXmlTextPtr(u.StrPtr(tt.input)); *got != tt.output {
				t.Errorf("normalizeXmlTextPtr() = %v, want %v", *got, tt.output)
			}
		})
	}
}

func Test_normalizeTextPtr(t *testing.T) {
	a := assert.New(t)
	a.Nil(normalizeXmlTextPtr(nil))
}
