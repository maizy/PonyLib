package fb2_scanner

import (
	"sync"

	"dev.maizy.ru/ponylib/fb2_scanner/resource"
)

type FileTarget struct {
	Path string
	UUID *string
}

func (f *FileTarget) RId() resource.RId {
	return resource.RId{Scheme: "file", Path: f.Path}
}

func (f *FileTarget) Type() TargetType {
	return FsFile
}

func (f *FileTarget) GetUUID() *string {
	return f.UUID
}

func (f *FileTarget) Scan(ctx ScannerContext) <-chan ScannerResult {
	resultChan := make(chan ScannerResult, 1)
	wg := sync.WaitGroup{}
	wg.Add(1)
	scanRegularFile(ctx, f.Path, resultChan, &wg, f)
	go func() {
		wg.Wait()
		close(resultChan)
	}()
	return resultChan
}
