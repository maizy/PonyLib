package binary

import (
	"strings"
	"unicode"
)

func CleanBase64String(value string) string {
	var sb strings.Builder
	sb.Grow(len(value))
	for _, ch := range value {
		if !unicode.IsSpace(ch) {
			sb.WriteRune(ch)
		}
	}
	return sb.String()
}
