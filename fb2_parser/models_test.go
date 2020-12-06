package fb2_parser

import (
	"testing"

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
		Book: &Book{Title: u.StrPtr("Best Book")},
		Authors: &[]Author{
			{Nickname: u.StrPtr("Ivan")},
			{Nickname: u.StrPtr("Navi")},
		},
	}

	assert.Equal(t, "Fb2(«Best Book» by Ivan, Navi)", metadata.String())
}
