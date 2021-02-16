package fb2_scanner

import (
	"dev.maizy.ru/ponylib/fb2_scanner/resource"
)

type FileSource struct {
	Path string
}

func (s *FileSource) RId() resource.RId {
	return resource.RId{Scheme: "file", Path: s.Path}
}

type ZipArchiveFileSource struct {
	Path     string
	FilePath string
}

func (z *ZipArchiveFileSource) RId() resource.RId {
	return resource.RId{Scheme: "zip", Path: z.Path, Query: []resource.Q{{"p", z.FilePath}}}
}
