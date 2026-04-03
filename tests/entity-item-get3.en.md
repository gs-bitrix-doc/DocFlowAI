# Retrieve a list of storage items from entity.item.get

> Scope: [`entity`](../../scopes/permissions.md)
>
> Who can call this method: a user authorized in the application

The `entity.item.get` method retrieves a list of items from the application's data storage.

{% note info "" %}

This method works only within the [application](../../../settings/app-installation/index.md) context.

{% endnote %}

## Method parameters

{% include [Note on parameters](../../../_includes/required.md) %}

#|
|| **Name**
`type` | **Description** ||
|| **ENTITY**^*^
[`string`](../../data-types.md) | Application data storage identifier. Use the value specified during storage creation.

You can retrieve the identifier using the [entity.get](../entities/entity-get.md) method ||
|| **SORT**
[`object`](../../data-types.md) | Object format:

```
{
    field_1: value_1,
    field_2: value_2,
    ...,
    field_n: value_n
}
```

where:
- `field_n` — sorting field
- `value_n` — sorting direction: `ASC` or `DESC`

For a list of available fields for sorting, see the [Item type](#item) section.

The default value is `{"ID":"ASC"}` ||
|| **FILTER**
[`object`](../../data-types.md) | Object format:

```
{
    field_1: value_1,
    field_2: value_2,
    ...,
    field_n: value_n
}
```

where:
- `field_n` — filter field
- `value_n` — filter value

For a list of available fields for filtering, see the [Item type](#item) section.

Prefixes can be added to `field_n` keys:
- `>=` — greater than or equal
- `>` — greater than
- `<=` — less than or equal
- `<` — less than
- `=` — equal (default)
- `!=` or `!` — not equal
- `><` — range
- `!><` — not in range
- `%` — LIKE
- `!%` — NOT LIKE
- `?` — check for `null`/`not null` ||
|| **start**
[`integer`](../../data-types.md) | Pagination parameter.

Page size is fixed: `50` records.

Formula to retrieve the N-th page:
`start = (N - 1) * 50`

For more details, see the article [Features of list methods](../../../settings/how-to-call-rest-api/list-methods-pecularities.md) ||
|#

## Code examples

{% include [Note on examples](../../../_includes/examples.md) %}

Example of retrieving storage items where:
- `ENTITY` — storage identifier `dish_v2`
- `SORT` — sorting by activity date and identifier
- `FILTER` — activity date range

{% list tabs %}

- cURL (OAuth)

    ```bash
    curl -X POST \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d '{"ENTITY":"dish_v2","SORT":{"DATE_ACTIVE_FROM":"ASC","ID":"ASC"},"FILTER":{">=DATE_ACTIVE_FROM":"2026-03-01T00:00:00+03:00","<DATE_ACTIVE_FROM":"2026-04-01T00:00:00+03:00"},"start":0,"auth":"**put_access_token_here**"}' \
    https://**put_your_bitrix24_address**/rest/entity.item.get
    ```

- JS

    ```js
    try
    {
    	const response = await $b24.callMethod(
    		'entity.item.get',
    		{
    			ENTITY: 'dish_v2',
    			SORT: {
    				DATE_ACTIVE_FROM: 'ASC',
    				ID: 'ASC',
    			},
    			FILTER: {
    				'>=DATE_ACTIVE_FROM': '2026-03-01T00:00:00+03:00',
    				'<DATE_ACTIVE_FROM': '2026-04-01T00:00:00+03:00',
    			},
    			start: 0,
    		}
    	);

    	const result = response.getData().result;
    	console.info(result);
    }
    catch (error)
    {
    	console.error('Error:', error);
    }
    ```

- PHP

    ```php
    try {
        $response = $b24Service
            ->core
            ->call(
                'entity.item.get',
                [
                    'ENTITY' => 'dish_v2',
                    'SORT' => [
                        'DATE_ACTIVE_FROM' => 'ASC',
                        'ID' => 'ASC',
                    ],
                    'FILTER' => [
                        '>=DATE_ACTIVE_FROM' => '2026-03-01T00:00:00+03:00',
                        '<DATE_ACTIVE_FROM' => '2026-04-01T00:00:00+03:00',
                    ],
                    'start' => 0,
                ]
            );

        $result = $response
            ->getResponseData()
            ->getResult();

        echo '<pre>';
        print_r($result);
        echo '</pre>';

    } catch (Throwable $e) {
        error_log($e->getMessage());
        echo 'Error getting entity items: ' . $e->getMessage();
    }
    ```

- BX24.js

    ```js
    BX24.callMethod(
        'entity.item.get',
        {
            ENTITY: 'dish_v2',
            SORT: {
                DATE_ACTIVE_FROM: 'ASC',
                ID: 'ASC',
            },
            FILTER: {
                '>=DATE_ACTIVE_FROM': '2026-03-01T00:00:00+03:00',
                '<DATE_ACTIVE_FROM': '2026-04-01T00:00:00+03:00',
            },
            start: 0,
        },
        (result) => {
            result.error()
                ? console.error(result.error())
                : console.info(result.data())
            ;
        },
    );
    ```

- PHP CRest

    ```php
    require_once('crest.php');

    $result = CRest::call(
        'entity.item.get',
        [
            'ENTITY' => 'dish_v2',
            'SORT' => [
                'DATE_ACTIVE_FROM' => 'ASC',
                'ID' => 'ASC',
            ],
            'FILTER' => [
                '>=DATE_ACTIVE_FROM' => '2026-03-01T00:00:00+03:00',
                '<DATE_ACTIVE_FROM' => '2026-04-01T00:00:00+03:00',
            ],
            'start' => 0,
        ]
    );

    echo '<PRE>';
    print_r($result);
    echo '</PRE>';
    ```

{% endlist %}

## Response handling

HTTP Status: **200**

```json
{
    "result": [
        {
            "ID": "2331",
            "TIMESTAMP_X": "2026-03-25T12:29:06+03:00",
            "MODIFIED_BY": "577",
            "DATE_CREATE": "2026-03-25T12:29:06+03:00",
            "CREATED_BY": "577",
            "ACTIVE": "Y",
            "DATE_ACTIVE_FROM": "",
            "DATE_ACTIVE_TO": "",
            "SORT": "500",
            "NAME": "Test item",
            "PREVIEW_PICTURE": null,
            "PREVIEW_TEXT": null,
            "DETAIL_PICTURE": null,
            "DETAIL_TEXT": null,
            "CODE": null,
            "ENTITY": "dish",
            "SECTION": null
        }
    ],
    "total": 1,
    "time": {
        "start": 1774430946,
        "finish": 1774430946.627232,
        "duration": 0.6272320747375488,
        "processing": 0,
        "date_start": "2026-03-25T12:29:06+03:00",
        "date_finish": "2026-03-25T12:29:06+03:00",
        "operating_reset_at": 1774431546,
        "operating": 0
    }
}
```

### Returned data

#|
|| **Name**
`type` | **Description** ||
|| **result**
[`item[]`](#item) | List of storage items ||
|| **total**
[`integer`](../../data-types.md) | Total number of items in the selection ||
|| **next**
[`integer`](../../data-types.md) | Offset to retrieve the next page (if available) ||
|| **time**
[`time`](../../data-types.md#time) | Request execution time information ||
|#

#### Item type {#item}

#|
|| **Name**
`type` | **Description** ||
|| **ID**
[`integer`](../../data-types.md) | Item identifier ||
|| **TIMESTAMP_X**
[`datetime`](../../data-types.md) | Date and time of the last update ||
|| **MODIFIED_BY**
[`integer`](../../data-types.md) | User identifier who modified the item ||
|| **DATE_CREATE**
[`datetime`](../../data-types.md) | Creation date and time ||
|| **CREATED_BY**
[`integer`](../../data-types.md) | User identifier who created the item ||
|| **ACTIVE**
[`string`](../../data-types.md) | Activity flag (`Y` or `N`) ||
|| **DATE_ACTIVE_FROM**
[`datetime`](../../data-types.md) \| [`string`](../../data-types.md) | Activity start date or an empty string ||
|| **DATE_ACTIVE_TO**
[`datetime`](../../data-types.md) \| [`string`](../../data-types.md) | Activity end date or an empty string ||
|| **SORT**
[`integer`](../../data-types.md) | Sorting index ||
|| **NAME**
[`string`](../../data-types.md) | Item title ||
|| **PREVIEW_PICTURE**
[`string`](../../data-types.md) \| [`null`](../../data-types.md) | URL for the preview image ||
|| **PREVIEW_TEXT**
[`string`](../../data-types.md) \| [`null`](../../data-types.md) | Preview text ||
|| **DETAIL_PICTURE**
[`string`](../../data-types.md) \| [`null`](../../data-types.md) | URL for the detailed image ||
|| **DETAIL_TEXT**
[`string`](../../data-types.md) \| [`null`](../../data-types.md) | Detailed text ||
|| **CODE**
[`string`](../../data-types.md) \| [`null`](../../data-types.md) | Item symbolic code ||
|| **ENTITY**
[`string`](../../data-types.md) | Storage identifier ||
|| **SECTION**
[`integer`](../../data-types.md) \| [`null`](../../data-types.md) | Section identifier ||
|| **PROPERTY_VALUES**
[`object`](../../data-types.md) | Properties values object in `{"CODE": value}` format. This field is present only if the storage has properties.

You can retrieve the list of available property codes using the [entity.item.property.get](./properties/entity-item-property-get.md) method ||
|#

## Error handling

HTTP Status: **400**

```json
{
    "error": "ERROR_ARGUMENT",
    "error_description": "Argument 'ENTITY' is null or empty",
    "argument": "ENTITY"
}
```

```json
{
    "error": "ERROR_ENTITY_NOT_FOUND",
    "error_description": "Entity not found"
}
```

{% include notitle [Error handling](../../../_includes/error-info.md) %}

### Possible error codes

#|
|| **Code** | **Description** | **Value** ||
|| `ERROR_ARGUMENT` | Argument 'ENTITY' is null or empty | The `ENTITY` parameter was not provided or is empty after cleaning ||
|| `ERROR_ARGUMENT` | Entity code is too long. Max length is N characters. | The `ENTITY` value is too long ||
|| `ERROR_ARGUMENT` | Filter validator errors | Invalid values were provided for the `FILTER` parameter ||
|| `ERROR_ENTITY_NOT_FOUND` | Entity not found | The storage with the provided `ENTITY` was not found ||
|| `ACCESS_DENIED` | Access denied! Application context required | No application context provided (`clientId`) ||
|#

{% include [System errors](../../../_includes/system-errors.md) %}

## Continue learning
- [{#T}](./entity-item-add.md)
- [{#T}](./entity-item-update.md)
- [{#T}](./entity-item-delete.md)
- [{#T}](./properties/index.md)