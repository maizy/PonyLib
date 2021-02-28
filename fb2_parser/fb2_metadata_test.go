package fb2_parser

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"

	"dev.maizy.ru/ponylib/internal/u"
)

func TestAuthor_String(t *testing.T) {
	authorWithNickname := Author{Nickname: u.StrPtr("Ivan"), FirstName: u.StrPtr("John")}
	assert.Equal(t, authorWithNickname.String(), "Ivan")

	authorWithoutNickname := Author{FirstName: u.StrPtr("John"), LastName: u.StrPtr("Seed")}
	assert.Equal(t, "John Seed", authorWithoutNickname.String())
}

func TestFb2Metadata_String(t *testing.T) {
	metadata := Fb2Metadata{
		Book: &Book{Title: "Best Book"},
		Authors: &[]Author{
			{Nickname: u.StrPtr("Ivan")},
			{Nickname: u.StrPtr("Navi")},
		},
	}

	assert.Equal(t, "«Best Book» by Ivan, Navi", metadata.String())
}

func Test(t *testing.T) {
	tests := []struct {
		name     string
		metadata Fb2Metadata
	}{
		{
			"full",
			Fb2Metadata{
				Book: &Book{
					Title:         "Compulsory",
					Lang:          u.StrPtr("en"),
					FormattedDate: u.StrPtr("2018"),
					Date:          u.TimePtr(time.Date(2018, 12, 16, 0, 0, 0, 0, time.UTC)),
				},
				PubInfo: &PubInfo{
					Publisher: u.StrPtr("Wired Magazine"),
					PubYear:   u.IntPtr(2018),
					ISBN:      u.StrPtr("978-1-250-22986-1"),
				},
				Authors: &[]Author{
					{FirstName: u.StrPtr("Martha"), LastName: u.StrPtr("Wells")},
					{
						FirstName:  u.StrPtr("Some"),
						MiddleName: u.StrPtr("Co"),
						LastName:   u.StrPtr("Author"),
						Nickname:   u.StrPtr("Nagib@T0R"),
					},
				},
				Genres: &[]GenreIndexEntity{
					GenreIndexByCode["sf"],
					GenreIndexByCode["sf_cyberpunk"],
				},
				Sequences: &[]Sequence{
					{"The Murderbot Diaries", u.IntPtr(0)},
					{"Best Of The Best", nil},
				},
				Annotation: u.StrPtr("line\nline2"),
			},
		},
		{
			"minimal",
			Fb2Metadata{
				Book: &Book{
					Title: "Compulsory",
					Lang:  u.StrPtr("en"),
				},
				Authors: &[]Author{{LastName: u.StrPtr("Wells")}},
				Genres:  &[]GenreIndexEntity{GenreIndexByCode["sf"]},
			},
		},
		{
			"super minimal",
			Fb2Metadata{
				Book: &Book{
					Title: "Compulsory",
				},
			},
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			a := assert.New(t)
			bytes, err := json.Marshal(test.metadata)
			if err != nil {
				t.Errorf("unable to marshal %v", test.metadata)
			} else {
				var unmarshalled Fb2Metadata
				if err := json.Unmarshal(bytes, &unmarshalled); err != nil {
					t.Errorf("unable to unmarshal %v for %v", bytes, test.metadata)
				}
				a.Equal(unmarshalled, test.metadata)
			}
		})
	}
}
