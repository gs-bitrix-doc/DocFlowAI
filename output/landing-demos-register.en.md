# Register a template in the site creation wizard landing.demos.register

> Scope: [`landing`](../../scopes/permissions.md)
>
> Who can execute the method: a user with View permission in the Sites section

The `landing.demos.register` method registers a custom template in the site and page creation wizard.

The method updates the template if one already exists with the same code for the current application. If it does not exist, it creates a new one.

## Method parameters
{% include [Note on parameters](../../../_includes/required.md) %}

#|
|| **Name**
`type` | **Description** ||
|| **data**^*^
[`object`](../../data-types.md) \| [`array`](../../data-types.md) | Template data.

Usually the result of the [landing.site.fullExport](../site/landing-site-full-export.md) method is passed.

The method accepts both a site export with `items` and an array of individual template items [details](#data) ||
|| **params**
[`object`](../../data-types.md) | Additional registration parameters [details](#params) ||
|#

### data type {#data}

{% include [Note on parameters](../../../_includes/required.md) %}

#|
|| **Name**
`type` | **Description** ||
|| **charset**
[`string`](../../data-types.md) | Encoding of the exported template ||
|| **code**^*^
[`string`](../../data-types.md) | External code of the template ||
|| **site_code**
[`string`](../../data-types.md) | Site code (path) ||
|| **name**
[`string`](../../data-types.md) | Template name ||
|| **description**
[`string`](../../data-types.md) \| [`null`](../../data-types.md) | Template description ||
|| **type**
[`string`](../../data-types.md) | Template type.

Possible values:
- `page` — templates for pages
- `store` — templates for stores
- `knowledge` — templates for knowledge bases
- `group` — templates for groups
- `mainpage` — templates for main pages ||
|| **tpl_type**
[`string`](../../data-types.md) | Template usage type in the wizard.

Possible values:
- `S` — site template
- `P` — page template ||
|| **fields**
[`object`](../../data-types.md) | Site fields from export [details](../site/landing-site-full-export.md#result-fields) ||
|| **folders**
[`array`](../../data-types.md) \| [`object`](../../data-types.md) | Folders from export [details](../site/landing-site-full-export.md#result) ||
|| **items**
[`object`Template pages map in format`{ "page_code": items }` [details](#data-items-element) ||
|| **layout**
[`array`](../../data-types.md) \| [`object`](../../data-types.md) | Layout data from export [details](../site/landing-site-full-export.md#result-layout) ||
|| **preview**
[`string`](../../data-types.md) | Link to preview 1x ||
|| **preview2x**
[`string`](../../data-types.md) | Link to preview 2x ||
|| **preview3x**
[`string`](../../data-types.md) | Link to preview 3x ||
|| **preview_url**
[`string`](../../data-types.md) | Link to preview ||
|| **show_in_list**
[`string`Display flag in list (`Y`/`N`) ||
|| **syspages**
[`array`](../../data-types.md) \| [`object`](../../data-types.md) | System pages from export [details](../site/landing-site-full-export.md#result) ||
|| **version**
[`integer`](../../data-types.md) | Export format version ||
|#

### item data.items type {#data-items-element}

{% include [Note on parameters](../../../_includes/required.md) %}

#|
|| **Name**
`type` | **Description** ||
|| **old_id**
[`string`](../../data-types.md) \| [`integer`](../../data-types.md) | Original page identifier ||
|| **code**^*^
[`string`](../../data-types.md) | External code of the page ||
|| **name**
[`string`](../../data-types.md) | Page name ||
|| **description**
[`string`](../../data-types.md) \| [`null`](../../data-types.md) | Page description ||
|| **type**
[`string`](../../data-types.md) | Page type.

Possible values:
- `page` — templates for pages
- `store` — templates for stores
- `knowledge` — templates for knowledge bases
- `group` — templates for groups
- `mainpage` — templates for main pages ||
|| **tpl_type**
[`string`](../../data-types.md) | Template usage type in the wizard.

Possible values:
- `S` — site template
- `P` — page template ||
|| **version**
[`integer`](../../data-types.md) | Page format version ||
|| **fields**
[`object`](../../data-types.md) | Page fields from export [details](../site/landing-site-full-export.md#page-fields).

See codes `fields.ADDITIONAL_FIELDS` in the [Additional page fields](../page/additional-fields.md) section. ||
|| **layout**
[`array`](../../data-types.md) \| [`object`](../../data-types.md) | Page layout from export [details](../site/landing-site-full-export.md#page-layout) ||
|| **items**
[`object`](../../data-types.md) \| [`array`](../../data-types.md) | Page blocks [details](#data-items-items-element) ||
|| **preview**
[`string`](../../data-types.md) | Link to preview 1x ||
|| **preview2x**
[`string`](../../data-types.md) | Link to preview 2x ||
|| **preview3x**
[`string`](../../data-types.md) | Link to preview 3x ||
|| **preview_url**
[`string`](../../data-types.md) | Link to preview ||
|| **show_in_list**
[`string`Display flag in list (`Y`/`N`) ||
|#

### item data.items.items type {#data-items-items-element}

#|
|| **Name**
`type` | **Description** ||
|| **code**
[`string`](../../data-types.md) | Block code ||
|| **access**
[`string`](../../data-types.md) | Access level for the block ||
|| **anchor**
[`string`](../../data-types.md) | Block anchor ||
|| **old_id**
[`integer`](../../data-types.md) | Original block identifier ||
|| **cards**
[`object`](../../data-types.md) | Block cards ||
|| **nodes**
[`object`](../../data-types.md) | Block nodes ||
|| **style**
[`object`](../../data-types.md) | Block styles ||
|| **attrs**
[`object`](../../data-types.md) | Block attributes ||
|#

### params parameter {#params}

#|
|| **Name**
`type` | **Description** ||
|| **site_template_id**
[`string`](../../data-types.md) | Identifier of the main module's site template. Used in on‑premise versions ||
|| **lang**
[`object`](../../data-types.md) | Localization of the template's main phrases.

Details in the article [Template localization](./localization.md) ||
|| **lang_original**
[`string`Source language code for array`lang` ||
|#

## Code examples

{% include [Note on examples](../../../_includes/examples.md) %}

Example of template registration, where:
- `data` — template structure for registration
- `data` in the examples was previously obtained with the [landing.site.fullExport](../site/landing-site-full-export.md) method

{% list tabs %}

- cURL (Webhook)

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{
        "data": {
          "charset": "UTF-8",
          "code": "ftmlt",
          "site_code": "/ftmlt/",
          "name": "Business",
          "description": null,
          "type": "page",
          "fields": {
            "TITLE": "Business",
            "LANDING_ID_INDEX": "0",
            "LANDING_ID_404": "0",
            "ADDITIONAL_FIELDS": {}
          },
          "folders": [],
          "items": {
            "ftmlt": {
              "old_id": "16",
              "code": "ftmlt",
              "name": "Business",
              "description": null,
              "preview": "",
              "preview2x": "",
              "preview3x": "",
              "preview_url": "",
              "show_in_list": "Y",
              "type": "page",
              "version": 3,
              "fields": {
                "TITLE": "Business"
              },
              "layout": [],
              "items": {}
            }
          },
          "layout": [],
          "preview": "",
          "preview2x": "",
          "preview3x": "",
          "preview_url": "",
          "show_in_list": "Y",
          "syspages": [],
          "version": 3
        }
      }' \
      "https://**put.your-domain-here**/rest/**user_id**/**webhook_code**/landing.demos.register.json"
    ```

- cURL (OAuth)

    ```bash
    curl -X POST \
      -H "Content-Type: application/json" \
      -d '{
        "data": {
          "charset": "UTF-8",
          "code": "ftmlt",
          "site_code": "/ftmlt/",
          "name": "Business",
          "description": null,
          "type": "page",
          "fields": {
            "TITLE": "Business",
            "LANDING_ID_INDEX": "0",
            "LANDING_ID_404": "0",
            "ADDITIONAL_FIELDS": {}
          },
          "folders": [],
          "items": {
            "ftmlt": {
              "old_id": "16",
              "code": "ftmlt",
              "name": "Business",
              "description": null,
              "preview": "",
              "preview2x": "",
              "preview3x": "",
              "preview_url": "",
              "show_in_list": "Y",
              "type": "page",
              "version": 3,
              "fields": {
                "TITLE": "Business"
              },
              "layout": [],
              "items": {}
            }
          },
          "layout": [],
          "preview": "",
          "preview2x": "",
          "preview3x": "",
          "preview_url": "",
          "show_in_list": "Y",
          "syspages": [],
          "version": 3
        },
        "auth": "**put_access_token_here**"
      }' \
      "https://**put.your-domain-here**/rest/landing.demos.register.json"
    ```

- JS

    ```js
    try
    {
    	const data = {
    		charset: 'UTF-8',
    		code: 'ftmlt',
    		site_code: '/ftmlt/',
    		name: 'Business',
    		description: null,
    		type: 'page',
    		fields: {
    			TITLE: 'Business',
    			LANDING_ID_INDEX: '0',
    			LANDING_ID_404: '0',
    			ADDITIONAL_FIELDS: {}
    		},
    		folders: [],
    		items: {
    			ftmlt: {
    				old_id: '16',
    				code: 'ftmlt',
    				name: 'Business',
    				description: null,
    				preview: '',
    				preview2x: '',
    				preview3x: '',
    				preview_url: '',
    				show_in_list: 'Y',
    				type: 'page',
    				version: 3,
    				fields: {
    					TITLE: 'Business'
    				},
    				layout: [],
    				items: {}
    			}
    		},
    		layout: [],
    		preview: '',
    		preview2x: '',
    		preview3x: '',
    		preview_url: '',
    		show_in_list: 'Y',
    		syspages: [],
    		version: 3
    	};

    	const response = await $b24.callMethod(
    		'landing.demos.register',
    		{
    			data
    		}
    	);

    	console.info(response.getData().result);
    }
    catch (error)
    {
    	console.error(error);
    }
    ```

- PHP

    ```php
    try {
        $data = [
            'charset' => 'UTF-8',
            'code' => 'ftmlt',
            'site_code' => '/ftmlt/',
            'name' => 'Business',
            'description' => null,
            'type' => 'page',
            'fields' => [
                'TITLE' => 'Business',
                'LANDING_ID_INDEX' => '0',
                'LANDING_ID_404' => '0',
                'ADDITIONAL_FIELDS' => [],
            ],
            'folders' => [],
            'items' => [
                'ftmlt' => [
                    'old_id' => '16',
                    'code' => 'ftmlt',
                    'name' => 'Business',
                    'description' => null,
                    'preview' => '',
                    'preview2x' => '',
                    'preview3x' => '',
                    'preview_url' => '',
                    'show_in_list' => 'Y',
                    'type' => 'page',
                    'version' => 3,
                    'fields' => [
                        'TITLE' => 'Business',
                    ],
                    'layout' => [],
                    'items' => [],
                ],
            ],
            'layout' => [],
            'preview' => '',
            'preview2x' => '',
            'preview3x' => '',
            'preview_url' => '',
            'show_in_list' => 'Y',
            'syspages' => [],
            'version' => 3,
        ];

        $response = $b24Service
            ->core
            ->call(
                'landing.demos.register',
                [
                    'data' => $data,
                ]
            );

        $result = $response
            ->getResponseData()
            ->getResult();

        echo 'Success: ' . print_r($result, true);
    } catch (Throwable $e) {
        error_log($e->getMessage());
        echo 'Error registering demo: ' . $e->getMessage();
    }
    ```

- BX24.js

    ```js
    BX24.callMethod(
        'landing.demos.register',
        {
            data: {
                charset: 'UTF-8',
                code: 'ftmlt',
                site_code: '/ftmlt/',
                name: 'Business',
                description: null,
                type: 'page',
                fields: {
                    TITLE: 'Business',
                    LANDING_ID_INDEX: '0',
                    LANDING_ID_404: '0',
                    ADDITIONAL_FIELDS: {}
                },
                folders: [],
                items: {
                    ftmlt: {
                        old_id: '16',
                        code: 'ftmlt',
                        name: 'Business',
                        description: null,
                        preview: '',
                        preview2x: '',
                        preview3x: '',
                        preview_url: '',
                        show_in_list: 'Y',
                        type: 'page',
                        version: 3,
                        fields: {
                            TITLE: 'Business'
                        },
                        layout: [],
                        items: {}
                    }
                },
                layout: [],
                preview: '',
                preview2x: '',
                preview3x: '',
                preview_url: '',
                show_in_list: 'Y',
                syspages: [],
                version: 3
            }
        },
        function(result)
        {
            if (result.error())
            {
                console.error(result.error());
            }
            else
            {
                console.info(result.data());
            }
        }
    );
    ```

- PHP CRest

    ```php
    require_once('crest.php');

    $data = [
        'charset' => 'UTF-8',
        'code' => 'ftmlt',
        'site_code' => '/ftmlt/',
        'name' => 'Business',
        'description' => null,
        'type' => 'page',
        'fields' => [
            'TITLE' => 'Business',
            'LANDING_ID_INDEX' => '0',
            'LANDING_ID_404' => '0',
            'ADDITIONAL_FIELDS' => [],
        ],
        'folders' => [],
        'items' => [
            'ftmlt' => [
                'old_id' => '16',
                'code' => 'ftmlt',
                'name' => 'Business',
                'description' => null,
                'preview' => '',
                'preview2x' => '',
                'preview3x' => '',
                'preview_url' => '',
                'show_in_list' => 'Y',
                'type' => 'page',
                'version' => 3,
                'fields' => [
                    'TITLE' => 'Business',
                ],
                'layout' => [],
                'items' => [],
            ],
        ],
        'layout' => [],
        'preview' => '',
        'preview2x' => '',
        'preview3x' => '',
        'preview_url' => '',
        'show_in_list' => 'Y',
        'syspages' => [],
        'version' => 3,
    ];

    $result = CRest::call(
        'landing.demos.register',
        [
            'data' => $data,
        ]
    );

    if (isset($result['error']))
    {
        echo 'Error:' . $result['error_description'];
    }
    else
    {
        echo '<pre>';
        print_r($result['result']);
        echo '</pre>';
    }
    ```

{% endlist %}

## Response handling

HTTP status: **200**

```json
{
    "result": [5, 7],
    "time": {
        "start": 1774611129,
        "finish": 1774611129.843163,
        "duration": 0.843163013458252,
        "processing": 0,
        "date_start": "2026-03-27T14:32:09+03:00",
        "date_finish": "2026-03-27T14:32:09+03:00",
        "operating_reset_at": 1774611729,
        "operating": 0
    }
}
```

### Returned data

#|
|| **Name**
`type` | **Description** ||
|| **result**
[`integer[]`](../../data-types.md) | Array of template identifiers that were created or updated ||
|| **time**
[`time`](../../data-types.md#time) | Information about the request execution time ||
|#

## Error handling

HTTP status: **400**

```json
{
    "error": "ERROR_ARGUMENT",
    "error_description": "The value of an argument 'data' has an invalid type",
    "argument": "data"
}
```

```json
{
    "error": "REGISTER_ERROR_DATA",
    "error_description": "Data is empty or invalid"
}
```

{% include notitle [Error handling](../../../_includes/error-info.md) %}

### Possible error codes

#|
|| **Code** | **Description** | **Value** ||
|| `ERROR_ARGUMENT`Parameter`data` passed with an incorrect type ||
|| `REGISTER_ERROR_DATA`Data is empty or invalid`data` ||
|| `CONTENT_IS_BAD`Parameter`landing.repo.checkcontent` | Unsafe content found in the submitted template ||
|| `BX_EMPTY_REQUIRED`Content is identified as unsafe. Unsafe parts can be identified via the method`data`. Required field "External code" is not filled`code` for the template/item ||
|| `ACCESS_DENIED` | `Access denied!` | Insufficient permissions to call the method ||
|#

{% include [System errors](../../../_includes/system-errors.md) %}

## Continue learning
- [{#T}](./landing-demos-get-site-list.md)
- [{#T}](./landing-demos-get-page-list.md)
- [{#T}](./landing-demos-get-list.md)
- [{#T}](./landing-demos-unregister.md)
- [{#T}](./localization.md)
- [{#T}](./index.md)