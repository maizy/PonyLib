package fb2_parser

import (
	"encoding/json"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestAuthor_String(t *testing.T) {
	authorWithNickname := Author{Nickname: new("Ivan"), FirstName: new("John")}
	assert.Equal(t, authorWithNickname.String(), "Ivan")

	authorWithoutNickname := Author{FirstName: new("John"), LastName: new("Seed")}
	assert.Equal(t, "John Seed", authorWithoutNickname.String())
}

func TestFb2Metadata_String(t *testing.T) {
	metadata := Fb2Metadata{
		Book: &Book{Title: "Best Book"},
		Authors: &[]Author{
			{Nickname: new("Ivan")},
			{Nickname: new("Navi")},
		},
	}

	assert.Equal(t, "«Best Book» by Ivan, Navi", metadata.String())
}

func TestFb2Metadata_JsonRoundTrip(t *testing.T) {
	tests := []struct {
		name     string
		metadata Fb2Metadata
	}{
		{
			"full",
			Fb2Metadata{
				Book: &Book{
					Title:         "Compulsory",
					Lang:          new("en"),
					FormattedDate: new("2018"),
					Date:          new(time.Date(2018, 12, 16, 0, 0, 0, 0, time.UTC)),
				},
				PubInfo: &PubInfo{
					Publisher: new("Wired Magazine"),
					PubYear:   new(2018),
					ISBN:      new("978-1-250-22986-1"),
				},
				Authors: &[]Author{
					{FirstName: new("Martha"), LastName: new("Wells")},
					{
						FirstName:  new("Some"),
						MiddleName: new("Co"),
						LastName:   new("Author"),
						Nickname:   new("Nagib@T0R"),
					},
				},
				Genres: &[]GenreIndexEntity{
					GenreIndexByCode["sf"],
					GenreIndexByCode["sf_cyberpunk"],
				},
				Sequences: &[]Sequence{
					{"The Murderbot Diaries", new(0)},
					{"Best Of The Best", nil},
				},
				Annotation: new("line\nline2"),
			},
		},
		{
			"minimal",
			Fb2Metadata{
				Book: &Book{
					Title: "Compulsory",
					Lang:  new("en"),
				},
				Authors: &[]Author{{LastName: new("Wells")}},
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
