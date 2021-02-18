package metadata

import (
	"fmt"
	"os"

	"dev.maizy.ru/ponylib/fb2_parser"
	"dev.maizy.ru/ponylib/internal/fb2"
)

func ParseMetadata(source *os.File) (*fb2_parser.Fb2Metadata, error) {
	metadata, infoErr := fb2.ScanBookMetadata(source)
	if infoErr != nil {
		return nil, fmt.Errorf("unable to parse metadata: %s", infoErr)
	}
	return metadata, nil
}
