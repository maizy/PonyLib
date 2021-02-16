package targets

import (
	"dev.maizy.ru/ponylib/internal/u"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"

	"dev.maizy.ru/ponylib/fb2_scanner"
	"dev.maizy.ru/ponylib/internal/sympath"
)

type DirectoryTarget struct {
	Path              string
	AllowedExtensions []string
}

func (f *DirectoryTarget) Spec() string {
	return fmt.Sprintf("dir:%s", f.Path)
}

func (f *DirectoryTarget) Type() fb2_scanner.TargetType {
	return fb2_scanner.FsDir
}

func (f *DirectoryTarget) Scan(ctx fb2_scanner.ScannerContext) <-chan fb2_scanner.ScannerResult {
	resultChan := make(chan fb2_scanner.ScannerResult)
	wg := sync.WaitGroup{}

	walkFunc := func(path string, info os.FileInfo, err error) error {
		if err != nil {
			resultChan <- fb2_scanner.ScannerResult{
				Source: &fb2_scanner.FileSource{path},
				Error:  u.ErrPtr(fmt.Errorf("unable to scan file or symlink %s: %w", path, err)),
			}
			return filepath.SkipDir
		}
		if info.Mode().IsRegular() && strings.HasSuffix(info.Name(), ".fb2") {
			scanRegularFile(ctx, path, resultChan, &wg)
		}
		return nil
	}

	go func() {
		err := sympath.Walk(f.Path, walkFunc)
		if err != nil {
			resultChan <- fb2_scanner.ScannerResult{
				Source: &fb2_scanner.FileSource{f.Path},
				Error:  u.ErrPtr(fmt.Errorf("unable to scan %s: %w", f.Path, err)),
			}
		}
		wg.Wait()
		close(resultChan)
	}()

	return resultChan
}
