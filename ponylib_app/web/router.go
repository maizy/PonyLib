package web

import (
	"embed"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"

	"dev.maizy.ru/ponylib/ponylib_app"
)

func AppendWebUiRouters(engine *gin.Engine) {
	engine.GET("/", func(c *gin.Context) {
		c.HTML(http.StatusOK, "index.tmpl", gin.H{
			"subtitle": "Search",
			"lang":     "en",
			"version":  ponylib_app.GetVersion(),
		})
	})
}

func AppendApiRouters(engine *gin.Engine) {
	apiGroup := engine.Group("/api/v1")
	apiGroup.GET("/version", BuildVersionHandler())
}

const staticPrefix = "/static/"

//go:embed static/*
var staticFS embed.FS

func AppendRouters(engine *gin.Engine) {

	engine.GET(staticPrefix+"*filepath", func(c *gin.Context) {
		path := c.Request.URL.Path
		if strings.HasPrefix(path, staticPrefix) {
			c.FileFromFS(path, http.FS(staticFS))
		} else {
			c.AbortWithStatus(http.StatusNotFound)
		}
	})

	AppendApiRouters(engine)
	AppendWebUiRouters(engine)
}
