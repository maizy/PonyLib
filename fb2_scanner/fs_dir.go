package fb2_scanner

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"

	"dev.maizy.ru/ponylib/internal/sympath"
	"dev.maizy.ru/ponylib/internal/u"
)

type DirectoryTarget struct {
	Path string
}

func (f *DirectoryTarget) Spec() string {
	return fmt.Sprintf("dir:%s", f.Path)
}

func (f *DirectoryTarget) Type() TargetType {
	return FsDir
}

func (f *DirectoryTarget) Scan(ctx ScannerContext) <-chan ScannerResult {
	resultChan := make(chan ScannerResult, 8)
	wg := sync.WaitGroup{}

	walkFunc := func(path string, info os.FileInfo, err error) error {
		if err != nil {
			resultChan <- ScannerResult{
				Source: &FileSource{path},
				Error:  u.ErrPtr(fmt.Errorf("unable to scan file or symlink %s: %w", path, err)),
			}
			return filepath.SkipDir
		}
		if info.Mode().IsRegular() && strings.HasSuffix(info.Name(), ".fb2") && !strings.HasPrefix(info.Name(), ".") {
			wg.Add(1)
			scanRegularFile(ctx, path, resultChan, &wg)
		}
		return nil
	}

	go func() {
		err := sympath.Walk(f.Path, walkFunc)
		if err != nil {
			resultChan <- ScannerResult{
				Source: &FileSource{f.Path},
				Error:  u.ErrPtr(fmt.Errorf("unable to scan %s: %w", f.Path, err)),
			}
		}
		wg.Wait()
		close(resultChan)
	}()

	return resultChan
}
