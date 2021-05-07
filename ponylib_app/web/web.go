package web

import (
	"embed"
	"html/template"
	"net/http"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"

	"dev.maizy.ru/ponylib/ponylib_app"
)

func serverHeader(c *gin.Context) {
	c.Header("Server", "Ponylib/"+ponylib_app.GetVersion())
}

func SetupMiddlewares(engine *gin.Engine) {
	engine.Use(serverHeader)
}

//go:embed templates/*
var templates embed.FS

func SetupTemplates(engine *gin.Engine, devMode bool) {
	engine.SetFuncMap(template.FuncMap{
		"split": func(sep string, string *string) []string {
			if string == nil {
				return nil
			}
			return strings.Split(*string, sep)
		},
	})
	if devMode {
		engine.LoadHTMLGlob("ponylib_app/web/templates/*.tmpl")
	} else {
		embedTemplate := template.Must(template.New("").ParseFS(templates, "templates/*.tmpl"))
		engine.SetHTMLTemplate(embedTemplate)
	}
}

func StaticsHandler(devMode bool) func(c *gin.Context) {
	return func(c *gin.Context) {
		path := c.Request.URL.Path
		if !devMode {
			c.Header("Cache-Control", "public, max-age="+strconv.Itoa(staticCacheMaxAge))
		}
		if strings.HasPrefix(path, staticPrefix) {
			c.FileFromFS(path, http.FS(staticFS))
		} else {
			c.AbortWithStatus(http.StatusNotFound)
		}
	}
}

func IndexHandler() func(c *gin.Context) {
	return func(c *gin.Context) {
		c.HTML(http.StatusOK, "index.tmpl", WithCommonVars(c, gin.H{
			"show_examples": true,
		}))
	}
}

func returnError(c *gin.Context, error string, errorCode int) {
	c.HTML(errorCode, "error.tmpl", WithCommonVars(c, gin.H{
		"error": error,
	}))
}
