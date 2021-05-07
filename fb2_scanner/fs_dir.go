package fb2_scanner

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"

	"dev.maizy.ru/ponylib/fb2_scanner/resource"
	"dev.maizy.ru/ponylib/internal/sympath"
	"dev.maizy.ru/ponylib/internal/u"
)

type DirectoryTarget struct {
	Path string
	UUID *string
}

func (d *DirectoryTarget) RId() resource.RId {
	return resource.RId{"dir", d.Path, []resource.Q{{"ext", "fb2"}, {"symlink", "1"}}}
}

func (d *DirectoryTarget) Type() TargetType {
	return FsDirTargetType
}

func (d *DirectoryTarget) GetUUID() *string {
	return d.UUID
}

func (d *DirectoryTarget) Scan(ctx ScannerContext) <-chan ScannerResult {
	resultChan := make(chan ScannerResult, 8)
	wg := sync.WaitGroup{}

	walkFunc := func(path string, info os.FileInfo, err error) error {
		if err != nil {
			resultChan <- ScannerResult{
				Source:     &FileSource{path},
				Error:      u.ErrPtr(fmt.Errorf("unable to scan file or symlink %s: %w", path, err)),
				FromTarget: d,
			}
			return filepath.SkipDir
		}
		if info.Mode().IsRegular() && strings.HasSuffix(info.Name(), ".fb2") && !strings.HasPrefix(info.Name(), ".") {
			wg.Add(1)
			scanRegularFile(ctx, path, resultChan, &wg, d)
		}
		return nil
	}

	go func() {
		err := sympath.Walk(d.Path, walkFunc)
		if err != nil {
			resultChan <- ScannerResult{
				Source:     &FileSource{d.Path},
				Error:      u.ErrPtr(fmt.Errorf("unable to scan %s: %w", d.Path, err)),
				FromTarget: d,
			}
		}
		wg.Wait()
		close(resultChan)
	}()

	return resultChan
}
