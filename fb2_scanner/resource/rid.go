package resource

import (
	"errors"
	"net/url"
	"path"
)

type Q struct {
	Key   string
	Value string
}

// Resource Identifier
// Limited URI implementation
type RId struct {
	Scheme string
	Path   string
	Query  []Q
}

const SubPathKey = "p"

func (u *RId) String() string {
	return EncodeRId(u.Scheme, u.Path, u.Query)
}

func (u *RId) SubPath() string {
	if u.Query != nil {
		for _, pair := range u.Query {
			if pair.Key == SubPathKey {
				return pair.Value
			}
		}
	}
	return ""
}

func (u *RId) ResourceBaseName() string {
	objectPath := u.Path
	if subPath := u.SubPath(); subPath != "" {
		objectPath = subPath
	}
	if objectPath != "" {
		return path.Base(objectPath)
	}
	return ""
}

func EncodeRId(scheme, path string, query []Q) string {
	internalUrl := url.URL{Scheme: scheme, Path: path}
	urlQ := url.Values{}
	for _, q := range query {
		urlQ.Add(q.Key, q.Value)
	}
	internalUrl.RawQuery = urlQ.Encode()
	return internalUrl.String()
}

func DecodeRId(rid string) (*RId, error) {
	parsedUrl, err := url.Parse(rid)
	if err != nil {
		return nil, errors.New("unable to parse resource identifier")
	}
	if urlQ := parsedUrl.Query(); len(urlQ) > 0 {
		q := make([]Q, 0, len(urlQ))
		for key, values := range urlQ {
			for _, v := range values {
				q = append(q, Q{key, v})
			}
		}
		return &RId{Scheme: parsedUrl.Scheme, Path: parsedUrl.Path, Query: q}, nil
	}
	return &RId{Scheme: parsedUrl.Scheme, Path: parsedUrl.Path}, nil

}
