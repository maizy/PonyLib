package resource

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

type args struct {
	scheme string
	path   string
	query  []Q
}

var tests = []struct {
	name     string
	args     args
	full     string
	baseName string
}{
	{
		"full",
		args{"file", "/path/to/book.fb2", []Q{{"reload", "true"}}},
		"file:///path/to/book.fb2?reload=true",
		"book.fb2",
	},
	{
		"only scheme",
		args{scheme: "special"},
		"special:",
		"",
	},
	{
		"scheme and path",
		args{scheme: "dir", path: "/path/to/dir"},
		"dir:///path/to/dir",
		"dir",
	},
	{
		"with space in path",
		args{scheme: "dir", path: "/path/to/dir with spaces"},
		"dir:///path/to/dir%20with%20spaces",
		"dir with spaces",
	},
	{
		"with unicode in path",
		args{scheme: "dir", path: "/unicode/path/привет"},
		"dir:///unicode/path/%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82",
		"привет",
	},
	{
		"repeated args",
		args{scheme: "special", query: []Q{{"k", "z"}, {"k", "a"}}},
		"special:?k=z&k=a",
		"",
	},
	{
		"with subpath",
		args{scheme: "zip", path: "/path/to/archive.zip", query: []Q{{SubPathKey, "path/to/file.fb2"}}},
		"zip:///path/to/archive.zip?p=path%2Fto%2Ffile.fb2",
		"file.fb2",
	},
}

func TestEncodeRId(t *testing.T) {

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := EncodeRId(tt.args.scheme, tt.args.path, tt.args.query)
			assert.Equal(t, tt.full, got)
		})
	}
}

func TestRId_String(t *testing.T) {
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := (&RId{tt.args.scheme, tt.args.path, tt.args.query}).String()
			assert.Equal(t, tt.full, got)
		})
	}
}

func TestRId_BaseName(t *testing.T) {
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := (&RId{tt.args.scheme, tt.args.path, tt.args.query}).ResourceBaseName()
			assert.Equal(t, tt.baseName, got)
		})
	}
}

func TestDecodeRId(t *testing.T) {
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := DecodeRId(tt.full)
			want := &RId{tt.args.scheme, tt.args.path, tt.args.query}
			assert.Nil(t, err)
			assert.Equal(t, want, got)
		})
	}
}
