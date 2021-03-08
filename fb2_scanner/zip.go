package fb2_scanner

import (
	"archive/zip"
	"fmt"
	"path"
	"strings"
	"sync"
	"time"

	"dev.maizy.ru/ponylib/fb2_parser/metadata"
	"dev.maizy.ru/ponylib/fb2_scanner/resource"
	"dev.maizy.ru/ponylib/internal/u"
)

type ZipArchiveTarget struct {
	Path string
	UUID *string
}

func (z *ZipArchiveTarget) RId() resource.RId {
	return resource.RId{"zip", z.Path, []resource.Q{{"ext", "fb2"}}}
}

func (z *ZipArchiveTarget) Type() TargetType {
	return ZipArchive
}

func (z *ZipArchiveTarget) GetUUID() *string {
	return z.UUID
}

func (z *ZipArchiveTarget) Scan(ctx ScannerContext) <-chan ScannerResult {
	resultChan := make(chan ScannerResult, 8)
	wg := sync.WaitGroup{}

	go func() {
		ctx.AcquireFileSemaphore()
		zipFile, err := zip.OpenReader(z.Path)
		defer func() {
			_ = zipFile.Close()
			ctx.ReleaseFileSemaphore()
		}()
		if err != nil {
			resultChan <- ScannerResult{
				Source:     &FileSource{z.Path},
				Error:      u.ErrPtr(fmt.Errorf("unable to open zip archive %s: %w", z.Path, err)),
				FromTarget: z,
			}
			return
		}

		for _, file := range zipFile.File {
			filePath := file.Name
			baseName := path.Base(filePath)
			if strings.HasSuffix(baseName, ".fb2") && !strings.HasPrefix(baseName, ".") {
				wg.Add(1)
				source := ZipArchiveFileSource{Path: z.Path, FilePath: filePath}

				timers := ParseTimers{}
				extractStart := time.Now()
				fp, err := file.Open()
				timers.ExtractTimeNs = time.Since(extractStart).Nanoseconds()

				if err != nil {
					resultChan <- ScannerResult{
						Source:   &source,
						Metadata: nil,
						Error: u.ErrPtr(
							fmt.Errorf("unable to open file %s in zip archive %s: %w", filePath, z.Path, err)),
						Timers:     timers,
						FromTarget: z,
					}
					wg.Done()
					continue
				}

				parseStart := time.Now()
				parseMetadata, err := metadata.ParseMetadata(fp)
				timers.ParseTimeNs = time.Since(parseStart).Nanoseconds()

				if err != nil {
					resultChan <- ScannerResult{
						Source:   &source,
						Metadata: nil,
						Error: u.ErrPtr(
							fmt.Errorf("unable to parse metadata for %s in zip archive %s: %w", filePath, z.Path, err)),
						Timers:     timers,
						FromTarget: z,
					}
				} else {
					resultChan <- ScannerResult{
						Source:     &source,
						Metadata:   parseMetadata,
						Error:      nil,
						Timers:     timers,
						FromTarget: z,
					}
				}
				_ = fp.Close()
				wg.Done()
			}
		}
		wg.Wait()
		close(resultChan)
	}()
	return resultChan
}
