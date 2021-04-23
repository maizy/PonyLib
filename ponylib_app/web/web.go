package web

import (
	"embed"
	"html/template"

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
	if devMode {
		engine.LoadHTMLGlob("ponylib_app/web/templates/*.tmpl")
	} else {
		embedTemplate := template.Must(template.New("").ParseFS(templates, "templates/*.tmpl"))
		engine.SetHTMLTemplate(embedTemplate)
	}
}
