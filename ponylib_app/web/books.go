package web

import (
	"fmt"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/vfaronov/httpheader"

	"dev.maizy.ru/ponylib/fb2_scanner"
	"dev.maizy.ru/ponylib/internal/fb2"
	"dev.maizy.ru/ponylib/internal/pagination"
	"dev.maizy.ru/ponylib/ponylib_app/db"
	"dev.maizy.ru/ponylib/ponylib_app/search"
)

func BuildBooksHandler(conn *pgxpool.Pool) func(c *gin.Context) {

	return func(c *gin.Context) {
		query := c.Query("query")

		var results *search.BookSearchResult
		var totalFound int

		// pages count from 1
		var currentPage int
		var searchPagination pagination.Pagination

		if query != "" {
			pageQuery := c.DefaultQuery("page", "1")
			if pageI, err := strconv.Atoi(pageQuery); err == nil {
				currentPage = max(pageI, 1)
			}
			limit := 40

			queryStruct := search.BookSearchQuery{TextMatch: query}

			if found, err := search.CountBooks(conn, &queryStruct); err != nil {
				c.AbortWithError(http.StatusInternalServerError, fmt.Errorf("unable to count matched books: %w", err))
				return
			} else {
				totalFound = found
			}

			offset := (currentPage - 1) * limit
			searchPagination = pagination.CountSlidePagination(8, currentPage, limit, totalFound)

			if totalFound > 0 && offset < totalFound {
				if res, err := search.SearchBooks(conn, &queryStruct, offset, limit); err != nil {
					c.AbortWithError(
						http.StatusInternalServerError,
						fmt.Errorf("unable to get matched books: %w", err),
					)
					return
				} else {
					results = res
				}
			}
		}

		titleQuery := query
		if len(titleQuery) >= 32 {
			titleQuery = query[:30] + "…"
		}
		c.HTML(http.StatusOK, "search.tmpl", WithCommonVars(c, gin.H{
			"subtitle":    "Books · " + query,
			"query":       query,
			"totalFound":  totalFound,
			"results":     results,
			"currentPage": currentPage,
			"pagination":  searchPagination,
		}))
	}
}

func BuildDownloadBookHandler(conn *pgxpool.Pool) func(c *gin.Context) {
	return func(c *gin.Context) {
		uuid := c.Param("uuid")
		book, err := db.GetBook(conn, uuid)
		if err != nil {
			returnError(c, "Book not found", http.StatusNotFound)
			return
		}

		reader, size, closeF, err := fb2_scanner.OpenResource(book.RId)
		if closeF != nil {
			defer closeF()
		}
		if err != nil {
			returnError(c, "Book is missing", http.StatusNotFound)
			return
		}

		filename := fb2.BuildFileName(book.RId, book.Metadata)
		header := http.Header{}
		httpheader.SetContentDisposition(header, "attachment", filename, nil)
		c.Header("Content-Disposition", header.Get("Content-Disposition"))

		c.DataFromReader(http.StatusOK, size, "application/x-fictionbook; charset=utf-8", *reader, nil)
	}
}
