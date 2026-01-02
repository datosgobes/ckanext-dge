# ckanext-dge

`ckanext-dge` es una extensión para CKAN utilizada en la plataforma datos.gob.es. Incluye adaptaciones específicas (funcionales y de interfaz) y utilidades de soporte.

> [!TIP]
> Guía base y contexto del proyecto: https://github.com/datosgobes/datos.gob.es

## Descripción

En términos de funcionalidades de CKAN, esta extensión aporta:

- Personalizaciones específicas del portal [datos.gob.es](https://datos.gob.es).
- Plantillas, recursos estáticos y *helpers* asociados.
- Un comando de administración vía *paster*.

## Requisitos

- Una instancia de CKAN.

## Instalación

Instalación en modo desarrollo:

```sh
pip install -e .
```

## Configuración

Activa el plugin en tu configuración de CKAN (por ejemplo, `development.ini`):

```ini
ckan.plugins = … dge
```

### Plugins

- `dge`


## Tests

Para ejecutar la suite de tests:

```sh
pytest --ckan-ini=test.ini ckanext/dge/tests
```

## Licencia

Este proyecto se distribuye bajo licencia **GNU Affero General Public License (AGPL) v3.0 o posterior**. Consulta el fichero [`LICENSE`](LICENSE).
