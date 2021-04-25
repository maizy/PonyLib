package web

import (
	"embed"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v4/pgxpool"
)

const staticPrefix = "/static/"

//go:embed static/*
var staticFS embed.FS

func AppendRouters(engine *gin.Engine, conn *pgxpool.Pool) {

	engine.GET(staticPrefix+"*filepath", func(c *gin.Context) {
		path := c.Request.URL.Path
		if strings.HasPrefix(path, staticPrefix) {
			c.FileFromFS(path, http.FS(staticFS))
		} else {
			c.AbortWithStatus(http.StatusNotFound)
		}
	})

	engine.GET("/", func(c *gin.Context) {
		c.HTML(http.StatusOK, "index.tmpl", WithCommonVars(c, gin.H{
			"show_examples": true,
		}))
	})

	engine.GET("/auth", func(c *gin.Context) {
		c.HTML(http.StatusOK, "auth.tmpl", WithCommonVars(c, gin.H{}))
	})

	engine.POST("/unlock", func(c *gin.Context) {
		c.Redirect(http.StatusFound, "/")
	})

	engine.GET("/version", BuildVersionHandler())

	engine.GET("/books", BuildBooksHandler(conn))
}
