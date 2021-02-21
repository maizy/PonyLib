package fb2_scanner

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func getMatchedBookTitles(target *ScanTarget) []string {
	scanner := NewFb2Scanner()
	var titles []string
	done := make(chan struct{})
	go func(results <-chan ScannerResult) {
		for res := range results {
			if res.IsSuccess() && res.Metadata != nil {
				titles = append(titles, res.Metadata.Book.Title)
			}
		}
		done <- struct{}{}
	}(scanner.Results)

	scanner.Scan(*target)
	scanner.WaitUntilFinish()
	<-done
	return titles
}

func TestFb2Scanner(t *testing.T) {
	type testData struct {
		expectedBookTitles []string
		target             ScanTarget
	}
	tests := []struct {
		name string
		data testData
	}{
		{"plain fb2 file", testData{[]string{"Test book 1"}, &FileTarget{"test/data/fs-file/book1.fb2"}}},
		{"symlink to fb2 file", testData{[]string{"Test book 1"}, &FileTarget{"test/data/fs-file/book-symlink.fb2"}}},
		{"non exist fb2 file", testData{nil, &FileTarget{"test/data/fs-file/non-exist-book.fb2"}}},

		{
			"directory with fb2 files, symlinks to fb2 files, bad symlink",
			testData{
				[]string{"Test book 1", "Test book 2", "Test book 4", "Test book 5"},
				&DirectoryTarget{"test/data/fs-dir/dir"},
			},
		},
		{
			"directory tree with fb2 files",
			testData{
				[]string{"Test book 1", "Test book 2", "Test book 3"}, &DirectoryTarget{"test/data/fs-dir/dir-tree"},
			},
		},
		{
			"directory symlink",
			testData{
				[]string{"Test book 1", "Test book 2", "Test book 3"}, &DirectoryTarget{"test/data/fs-dir/dir-symlink"},
			},
		},
		{
			"broken dir symlink",
			testData{
				nil, &DirectoryTarget{"test/data/fs-dir/broken-dir-symlink"},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			a := assert.New(t)
			a.ElementsMatch(tt.data.expectedBookTitles, getMatchedBookTitles(&tt.data.target))
		})
	}
}
