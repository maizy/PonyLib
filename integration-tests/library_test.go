//go:build integration

package integration_test

import (
	"archive/zip"
	"context"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/http/cookiejar"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"dev.maizy.ru/ponylib/fb2_parser"
	"dev.maizy.ru/ponylib/fb2_scanner/resource"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/stretchr/testify/require"
	"golang.org/x/net/html"
)

type fixture struct{ name, title, author, last string }

var books = []fixture{
	{"Лермонтов - Герой нашего времени.fb2", "Герой нашего времени", "Александр Сергеевич Пушкин", "Пушкин"},
	{"Чехов. Дама с собачкой.fb2", "Дама с собачкой", "Александр Сергеевич Пушкин", "Пушкин"},
	{"Пушкин. Пиковая дама.fb2", "Пиковая дама", "Александр Сергеевич Пушкин", "Пушкин"},
	{"Brief an den Vater - Franz Kafka.fb2", "Brief an den Vater", "Franz Kafka", "Kafka"},
	{"Das Schloss - Franz Kafka.fb2", "Das Schloss", "Franz Kafka", "Kafka"},
	{"Das Urteil - Franz Kafka.fb2", "Das Urteil", "Franz Kafka", "Kafka"},
	{"Doyle Arthur - The Adventure of the Copper Beeches.fb2", "The Adventure of the Copper Beeches", "Arthur Conan Doyle", "Doyle"},
	{"La Sainte Courtisane - Oscar Wilde.fb2", "La Sainte Courtisane", "Oscar Wilde", "Wilde"},
	{"The Ballad of Reading Gaol - Oscar Wilde.fb2", "The Ballad of Reading Gaol", "Oscar Wilde", "Wilde"},
	{"The Importance of Being Earnest - Oscar Wilde.fb2", "The Importance of Being Earnest: A Trivial Comedy for Serious People", "Oscar Wilde", "Wilde"},
	{"The Soul of Man under Socialism - Oscar Wilde.fb2", "The Soul of Man under Socialism", "Oscar Wilde", "Wilde"},
}

func TestLibrary(t *testing.T) {
	databaseURL := isolatedDatabase(t)
	ctx, cancel := context.WithTimeout(t.Context(), 3*time.Minute)
	defer cancel()
	binary := filepath.Join(t.TempDir(), "ponylib")
	runStep(t, "build-cli", func(t *testing.T) {
		build := exec.CommandContext(ctx, "go", "build", "-race", "-o", binary, "./cmd/ponylib")
		build.Dir = ".."
		output, err := build.CombinedOutput()
		require.NoError(t, err, "%s", output)
	})
	env := append(os.Environ(), "DATABASE_URL="+databaseURL, "FTS_LANGUAGE=english", "DB_SKIP_MIGRATIONS=1", "PASSWORD=integration-secret")
	run := func(t *testing.T, args ...string) {
		t.Helper()
		t.Logf("Run CLI: ponylib %s", strings.Join(args, " "))
		command := exec.CommandContext(ctx, binary, args...)
		command.Env = env
		output, err := command.CombinedOutput()
		require.NoError(t, err, "%s", output)
	}
	pool, err := pgxpool.New(ctx, databaseURL)
	require.NoError(t, err)
	t.Cleanup(pool.Close)
	migrations := func(t *testing.T) []string {
		rows, err := pool.Query(ctx, "select id || ':' || applied_at::text from app_migrations order by id")
		require.NoError(t, err)
		values, err := pgx.CollectRows(rows, pgx.RowTo[string])
		require.NoError(t, err)
		return values
	}
	var before []string
	runStep(t, "migrate-database", func(t *testing.T) {
		run(t, "migrate")
		before = migrations(t)
		require.NotEmpty(t, before)
	})
	runStep(t, "migrate-database-again", func(t *testing.T) {
		run(t, "migrate")
		require.Equal(t, before, migrations(t))
	})
	archive, err := filepath.Abs("test-fb2.zip")
	require.NoError(t, err)
	originals := map[string][]byte{}
	runStep(t, "read-fixture-archive", func(t *testing.T) {
		zipReader, err := zip.OpenReader(archive)
		require.NoError(t, err)
		defer zipReader.Close()
		for _, entry := range zipReader.File {
			reader, err := entry.Open()
			require.NoError(t, err)
			data, err := io.ReadAll(reader)
			require.NoError(t, err)
			require.NoError(t, reader.Close())
			originals[entry.Name] = data
		}
		require.Len(t, originals, len(books))
	})
	runStep(t, "scan-books", func(t *testing.T) {
		run(t, "scan", archive)
	})
	ids := map[string]fixture{}
	runStep(t, "verify-database", func(t *testing.T) {
		var targets, count int
		require.NoError(t, pool.QueryRow(ctx, "select count(*) from target").Scan(&targets))
		require.Equal(t, 1, targets)
		var targetID, targetRID string
		var scannedAt time.Time
		require.NoError(t, pool.QueryRow(ctx, "select id, rid, scanned_at from target").Scan(&targetID, &targetRID, &scannedAt))
		require.False(t, scannedAt.IsZero())
		expectedRoot := resource.RId{Scheme: "zip", Path: archive, Query: []resource.Q{{Key: "ext", Value: "fb2"}}}
		require.Equal(t, expectedRoot.String(), targetRID)
		require.NoError(t, pool.QueryRow(ctx, "select count(*) from book").Scan(&count))
		require.Equal(t, len(books), count)
		for _, book := range books {
			t.Logf("Verify database book: %s", book.title)
			require.Contains(t, originals, book.name)
			var id, rid, parent string
			var metadata fb2_parser.Fb2Metadata
			require.NoError(t, pool.QueryRow(ctx, "select id, target_id, rid, metadata from book where metadata #>> '{book,title}' = $1", book.title).Scan(&id, &parent, &rid, &metadata))
			require.Equal(t, targetID, parent)
			require.Equal(t, book.title, metadata.Book.Title)
			require.Equal(t, book.author, metadata.AuthorsString())
			decoded, err := resource.DecodeRId(rid)
			require.NoError(t, err)
			require.Equal(t, "zip", decoded.Scheme)
			require.Equal(t, archive, decoded.Path)
			require.Equal(t, book.name, decoded.SubPath())
			ids[id] = book
		}
	})
	parent := t
	var base string
	var browser *http.Client
	runStep(t, "start-webui", func(t *testing.T) {
		listener, err := net.Listen("tcp", "127.0.0.1:0")
		require.NoError(t, err)
		port := listener.Addr().(*net.TCPAddr).Port
		require.NoError(t, listener.Close())
		base = fmt.Sprintf("http://127.0.0.1:%d", port)
		log, err := os.CreateTemp(parent.TempDir(), "web-*.log")
		require.NoError(t, err)
		server := exec.CommandContext(ctx, binary, "web-ui", "--port", fmt.Sprint(port))
		server.Env, server.Stdout, server.Stderr = env, log, log
		require.NoError(t, server.Start())
		parent.Cleanup(func() {
			_ = server.Process.Kill()
			_ = server.Wait()
			_ = log.Close()
			if parent.Failed() {
				data, _ := os.ReadFile(log.Name())
				parent.Logf("WebUI output:\n%s", data)
			}
		})
		jar, err := cookiejar.New(nil)
		require.NoError(t, err)
		browser = &http.Client{Jar: jar, Timeout: 3 * time.Second}
		require.Eventually(t, func() bool {
			response, err := browser.Get(base)
			if err != nil {
				return false
			}
			defer response.Body.Close()
			return response.StatusCode == http.StatusOK && response.Request.URL.Path == "/auth"
		}, 15*time.Second, 100*time.Millisecond)
	})
	runStep(t, "authenticate-webui", func(t *testing.T) {
		response, err := browser.Get(base)
		require.NoError(t, err)
		document, err := html.Parse(response.Body)
		require.NoError(t, response.Body.Close())
		require.NoError(t, err)
		authAction := formAction(document, "password")
		require.Equal(t, "/auth", authAction)
		response, err = browser.PostForm(base+authAction, url.Values{"password": {"integration-secret"}})
		require.NoError(t, err)
		require.NoError(t, response.Body.Close())
		require.Equal(t, http.StatusOK, response.StatusCode)
		require.Equal(t, "/", response.Request.URL.Path)
		address, err := url.Parse(base)
		require.NoError(t, err)
		require.NotEmpty(t, browser.Jar.Cookies(address))
	})
	type scenario struct {
		name, query string
		expected    []string
	}
	var scenarios []scenario
	for _, book := range books {
		scenarios = append(scenarios, scenario{"title/" + book.title, book.title, []string{book.title}}, scenario{"author-title/" + book.title, book.last + " " + book.title, []string{book.title}})
	}
	scenarios = append(scenarios,
		scenario{"annotation", "deduction", []string{books[6].title}},
		scenario{"phrase", `"Copper Beeches"`, []string{books[6].title}},
		scenario{"before-exclusion", "дама", []string{books[1].title, books[2].title}},
		scenario{"exclusion", "дама -собачкой", []string{books[2].title}},
	)
	for _, test := range scenarios {
		t.Run(test.name, func(t *testing.T) {
			t.Logf("Search query: %s", test.query)
			response, err := browser.Get(base)
			require.NoError(t, err)
			document, err := html.Parse(response.Body)
			require.NoError(t, response.Body.Close())
			require.NoError(t, err)
			action := formAction(document, "query")
			require.Equal(t, "/books", action)
			response, err = browser.Get(base + action + "?" + url.Values{"query": {test.query}}.Encode())
			require.NoError(t, err)
			require.Equal(t, http.StatusOK, response.StatusCode)
			document, err = html.Parse(response.Body)
			require.NoError(t, response.Body.Close())
			require.NoError(t, err)
			var found []string
			walk(document, func(node *html.Node) {
				if node.Type != html.ElementNode || node.Data != "a" {
					return
				}
				href := attribute(node, "href")
				if !strings.HasPrefix(href, "/books/") || !strings.Contains(href, "/download/") {
					return
				}
				parts := strings.Split(href, "/")
				book, ok := ids[parts[2]]
				require.True(t, ok, "unknown download: %s", href)
				require.Contains(t, nodeText(node), book.title)
				found = append(found, book.title)
				t.Logf("Download and compare: %s", book.name)
				download, err := browser.Get(base + href)
				require.NoError(t, err)
				data, err := io.ReadAll(download.Body)
				require.NoError(t, download.Body.Close())
				require.NoError(t, err)
				require.Equal(t, http.StatusOK, download.StatusCode)
				require.Contains(t, download.Header.Get("Content-Disposition"), "attachment")
				require.Equal(t, originals[book.name], data, "download: %s", book.name)
			})
			require.ElementsMatch(t, test.expected, found)
		})
	}
}

// Later steps depend on earlier ones; stop the parent test after a failed step.
func runStep(t *testing.T, name string, step func(*testing.T)) {
	t.Helper()
	if !t.Run(name, step) {
		t.FailNow()
	}
}

func walk(node *html.Node, visit func(*html.Node)) {
	visit(node)
	for child := node.FirstChild; child != nil; child = child.NextSibling {
		walk(child, visit)
	}
}
func attribute(node *html.Node, name string) string {
	for _, attr := range node.Attr {
		if attr.Key == name {
			return attr.Val
		}
	}
	return ""
}
func formAction(document *html.Node, input string) string {
	var action string
	walk(document, func(node *html.Node) {
		if node.Type == html.ElementNode && node.Data == "form" {
			walk(node, func(child *html.Node) {
				if child.Data == "input" && attribute(child, "name") == input {
					action = attribute(node, "action")
				}
			})
		}
	})
	return action
}
func nodeText(node *html.Node) string {
	var text strings.Builder
	walk(node, func(child *html.Node) {
		if child.Type == html.TextNode {
			text.WriteString(child.Data)
		}
	})
	return text.String()
}
