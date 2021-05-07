package web

import (
	"embed"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v4/pgxpool"
)

const staticPrefix = "/static/"
const staticCacheMaxAge = 30 * 24 * 60 * 60

//go:embed static/*
var staticFS embed.FS

func AppendRouters(engine *gin.Engine, conn *pgxpool.Pool, devMode bool) {

	engine.GET(staticPrefix+"*filepath", StaticsHandler(devMode))

	engine.GET("/", IndexHandler())

	engine.GET("/auth", func(c *gin.Context) {
		c.HTML(http.StatusOK, "auth.tmpl", WithCommonVars(c, gin.H{}))
	})
	engine.POST("/unlock", func(c *gin.Context) {
		c.Redirect(http.StatusFound, "/")
	})

	engine.GET("/version", BuildVersionHandler())

	engine.GET("/books", BuildBooksHandler(conn))
	engine.GET("/books/:uuid/download/:file_name", BuildDownloadBookHandler(conn))
}
