package web

import (
	"bytes"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
)

func TestFavicon(t *testing.T) {
	// The site icon must also be available before login.
	t.Setenv("PASSWORD", "test-password")
	icon, err := staticFS.ReadFile("static/img/favicon.ico")
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.HasPrefix(icon, []byte{0, 0, 1, 0, 1, 0}) {
		t.Fatal("favicon must be an ICO image")
	}
	for _, devMode := range []bool{false, true} {
		t.Run(map[bool]string{false: "production", true: "development"}[devMode], func(t *testing.T) {
			engine := gin.New()
			AppendRouters(engine, nil, devMode)
			w := httptest.NewRecorder()
			engine.ServeHTTP(w, httptest.NewRequest(http.MethodGet, "/favicon.ico?test=1", nil))
			if w.Code != http.StatusOK {
				t.Fatalf("status = %d, want 200", w.Code)
			}
			if !bytes.Equal(w.Body.Bytes(), icon) {
				t.Fatal("response does not match embedded favicon")
			}
			if got := w.Header().Get("Content-Type"); got != "image/vnd.microsoft.icon" && got != "image/x-icon" {
				t.Fatalf("unexpected content type: %q", got)
			}
			wantCache := "public, max-age=2592000"
			if devMode {
				wantCache = ""
			}
			if got := w.Header().Get("Cache-Control"); got != wantCache {
				t.Fatalf("Cache-Control = %q, want %q", got, wantCache)
			}
			w = httptest.NewRecorder()
			engine.ServeHTTP(w, httptest.NewRequest(http.MethodGet, "/version", nil))
			if w.Code != http.StatusFound || w.Header().Get("Location") != authUrl {
				t.Fatal("other routes must still require authentication")
			}
		})
	}
}
