package fb2_scanner

import (
	"archive/zip"
	"bufio"
	"fmt"
	"io"
	"os"

	"dev.maizy.ru/ponylib/fb2_scanner/resource"
)

type FileSource struct {
	Path string
}

const (
	FileSourceType = "file"
	ZipSourceType  = "zip"
)

var nop = func() {}

func (s *FileSource) RId() resource.RId {
	return resource.RId{Scheme: FileSourceType, Path: s.Path}
}

type ZipArchiveFileSource struct {
	Path     string
	FilePath string
}

func (z *ZipArchiveFileSource) RId() resource.RId {
	return resource.RId{Scheme: ZipSourceType, Path: z.Path, Query: []resource.Q{{resource.SubPathKey, z.FilePath}}}
}

func OpenResource(RId resource.RId) (*io.Reader, int64, func(), error) {
	switch RId.Scheme {
	case FileSourceType:
		file, err := os.Open(RId.Path)
		if err != nil {
			return nil, 0, nop, fmt.Errorf("unable to read file for %s: %w", RId, err)
		}
		stat, err := file.Stat()
		if err != nil {
			return nil, 0, nop, fmt.Errorf("unable to get file size for %s: %w", RId, err)
		}
		var reader io.Reader = bufio.NewReader(file)
		closeF := func() {
			_ = file.Close()
		}
		return &reader, stat.Size(), closeF, nil

	case ZipSourceType:
		zipFile, err := zip.OpenReader(RId.Path)
		if err != nil {
			return nil, 0, nop, fmt.Errorf("unable to open zip archive for %s: %w", RId, err)
		}
		subPath := RId.SubPath()
		file, err := zipFile.Open(subPath)
		if err != nil {
			_ = zipFile.Close()
			return nil, 0, nop, fmt.Errorf("unable to open file %s in zip archive for %s: %w", subPath, RId, err)
		}
		stat, err := file.Stat()
		if err != nil {
			return nil, 0, nop,
				fmt.Errorf("unable to get file size for %s in zip archive for %s: %w", subPath, RId, err)
		}
		var reader io.Reader = file
		closeF := func() {
			_ = file.Close()
			_ = zipFile.Close()
		}
		return &reader, stat.Size(), closeF, nil

	default:
		return nil, 0, nop, fmt.Errorf("unexpected resource type %s for %s", RId.Scheme, RId)
	}

}
