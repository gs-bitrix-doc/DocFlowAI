# Get deal by Id crm.deal.get

> Scope: [`crm`](../../scopes/permissions.md)

> Who can execute the method: any user with “read” permission for deals

{% note warning "Развитие метода остановлено" %}

The method `crm.deal.get` continues to work, but it has a more up‑to‑date counterpart [crm.item.get](../universal/crm-item-get.md).

{% endnote %}

The method `crm.deal.get` returns a deal by identifier.

## Method parameters

{% include [Сноска о параметрах](../../../_includes/required.md) %}

#|
|| **Name**
`тип` | **Description** || 
|| **id***
[`integer`](../../data-types.md) | Deal identifier.

The identifier can be obtained using methods [crm.deal.list](./crm-deal-list.md) or [crm.deal.add](./crm-deal-add.md) ||
|#

{% note tip "Связанные методы и темы" %}

[{#T}](./recurring-deals/crm-deal-recurring-get.md)

{% endnote %}

## Code examples

{% include [Сноска о примерах](../../../_includes/examples.md) %}

{% list tabs %}

- cURL (Webhook)

    ```bash
    curl -X POST \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d '{"ID":410}' \
    https://**put_your_bitrix24_address**/rest/**put_your_user_id_here**/**put_your_webhook_here**/crm.deal.get
    ```

- cURL (OAuth)

    ```bash
    curl -X POST \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d '{"ID":410,"auth":"**put_access_token_here**"}' \
    https://**put_your_bitrix24_address**/rest/crm.deal.get
    ```

- JS

    ```js
    try
    {
    	const response = await $b24.callMethod(
    		'crm.deal.get',
    		{
    			id: 410,
    		}
    	);
    	
    	const result = response.getData().result;
    	result.error()
    		? console.error(result.error())
    		: console.info(result)
    	;
    }
    catch( error )
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
                'crm.deal.get',
                [
                    'id' => 410,
                ]
            );
    
        $result = $response
            ->getResponseData()
            ->getResult();
    
        if ($result->error()) {
            echo 'Error: ' . $result->error();
        } else {
            echo 'Deal data: ' . print_r($result->data(), true);
        }
    
    } catch (Throwable $e) {
        error_log($e->getMessage());
        echo 'Error getting deal: ' . $e->getMessage();
    }
    ```

- BX24.js

    ```js
    BX24.callMethod(
        'crm.deal.get',
        {
            id: 410,
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
        'crm.deal.get',
        [
            'ID' => 410
        ]
    );

    echo '<PRE>';
    print_r($result);
    echo '</PRE>';
    ```

{% endlist %}

## Response handling

HTTP status: **200**

```json
{
    "result": {
        "ID": "410",
        "TITLE": "Новая сделка #1",
        "TYPE_ID": "COMPLEX",
        "STAGE_ID": "PREPARATION",
        "PROBABILITY": "99",
        "CURRENCY_ID": "EUR",
        "OPPORTUNITY": "1000000.00",
        "IS_MANUAL_OPPORTUNITY": "Y",
        "TAX_VALUE": "0.00",
        "LEAD_ID": null,
        "COMPANY_ID": "9",
        "CONTACT_ID": "84",
        "QUOTE_ID": null,
        "BEGINDATE": "2024-08-30T02:00:00+02:00",
        "CLOSEDATE": "2024-09-09T02:00:00+02:00",
        "ASSIGNED_BY_ID": "1",
        "CREATED_BY_ID": "1",
        "MODIFY_BY_ID": "1",
        "DATE_CREATE": "2024-08-30T14:29:00+02:00",
        "DATE_MODIFY": "2024-08-30T14:29:00+02:00",
        "OPENED": "Y",
        "CLOSED": "N",
        "COMMENTS": "[B]Пример комментария[\/B]",
        "ADDITIONAL_INFO": "Дополнительная информация",
        "LOCATION_ID": null,
        "CATEGORY_ID": "0",
        "STAGE_SEMANTIC_ID": "P",
        "IS_NEW": "N",
        "IS_RECURRING": "N",
        "IS_RETURN_CUSTOMER": "N",
        "IS_REPEATED_APPROACH": "N",
        "SOURCE_ID": "CALLBACK",
        "SOURCE_DESCRIPTION": "Дополнительно об источнике",
        "ORIGINATOR_ID": null,
        "ORIGIN_ID": null,
        "MOVED_BY_ID": "1",
        "MOVED_TIME": "2024-08-30T14:29:00+02:00",
        "LAST_ACTIVITY_TIME": "2024-08-30T14:29:00+02:00",
        "UTM_SOURCE": "google",
        "UTM_MEDIUM": "CPC",
        "UTM_CAMPAIGN": null,
        "UTM_CONTENT": null,
        "UTM_TERM": null,
        "PARENT_ID_1220": "22",
        "LAST_ACTIVITY_BY": "1",
        "UF_CRM_1721244482250": "Привет мир!"
    },
    "time": {
        "start": 1725020945.541275,
        "finish": 1725020946.179076,
        "duration": 0.637800931930542,
        "processing": 0.21427488327026367,
        "date_start": "2024-08-30T14:29:05+02:00",
        "date_finish": "2024-08-30T14:29:06+02:00",
        "operating": 0
    }
}
```

### Returned data

#|
|| **Name**
`тип` | **Description** ||
|| **result**
[`deal`](#deal) | Root element of the response. Contains information about deal fields. Structure described [ниже](#deal) ||
|| **time**
[`time`](../../data-types.md#time) | Information about request execution time ||
|#

#### Deal type {#deal}

#|
|| **Name**
`тип` | **Description** ||
|| **ID**
[`integer`](../../data-types.md) | Deal identifier ||
|| **TITLE**
[`string`](../../data-types.md) | Name ||
|| **TYPE_ID**
[`crm_status`](../data-types.md) | String identifier of the deal type. 

More details about the obtained deal type can be retrieved with method [crm.status.list](../status/crm-status-list.md) by passing in a filter:

```
{
    ENTITY_ID: 'DEAL_TYPE',
    STATUS_ID: TYPE_ID,
}
```
||
|| **CATEGORY_ID**
[`crm_category`](../data-types.md) | Pipeline. More details about this pipeline can be retrieved with method [crm.category.get](../universal/category/crm-category-get.md) by passing `entityTypeId = 2` and `id = CATEGORY_ID` ||
|| **STAGE_ID**
[`crm_status`](../data-types.md) | String identifier of the deal stage. 

More details about the obtained stage can be retrieved with method [crm.status.list](../status/crm-status-list.md) by passing in a filter:

```
{
    ENTITY_ID: entityId,
    STATUS_ID: statusId,
}
```

where:
- `entityId` equals:
    - `DEAL_STAGE` when the deal is in a common pipeline (`CATEGORY_ID = 0`)
    - `DEAL_STAGE_{categoryId}`, where `categoryId = CATEGORY_ID`
- `statusId` equals `STAGE_ID`
||
|| **STAGE_SEMANTIC_ID**
[`string`](../../data-types.md) | Stage group. Possible values:
- `P` — in progress
- `S` — successful
- `F` — unsuccessful
||
|| **IS_NEW**
[`char`](../../data-types.md) | Whether the deal is new. Possible values:
- `Y` — yes
- `N` — no ||
|| **IS_RECURRING**
[`char`](../../data-types.md) | Whether the deal is regular. Possible values:
- `Y` — yes
- `N` — no ||
|| **IS_RETURN_CUSTOMER**
[`char`](../../data-types.md) | Whether the deal is repeated. Possible values:
- `Y` — yes
- `N` — no ||
|| **IS_REPEATED_APPROACH**
[`char`](../../data-types.md) | Whether the request is repeated. Possible values:
- `Y` — yes
- `N` — no ||
|| **PROBABILITY**
[`integer`](../../data-types.md) | Probability, % ||
|| **CURRENCY_ID**
[`crm_currency`](../data-types.md#crm_currency) | Currency ||
|| **OPPORTUNITY**
[`double`](../../data-types.md) | Amount ||
|| **IS_MANUAL_OPPORTUNITY**
[`char`](../../data-types.md) | Manual sum calculation mode enabled. Possible values:
- `Y` — yes
- `N` — no ||
|| **TAX_VALUE**
[`double`](../../data-types.md) | Tax rate ||
|| **COMPANY_ID**
[`crm_company`](../data-types.md) | Company identifier. 

More details about the company can be retrieved with method [crm.item.get](../universal/crm-item-get.md) by passing `entityTypeId = 4` and `id = COMPANY_ID`
||
|| **CONTACT_ID**
[`crm_contact`](../data-types.md) | Contact identifier. Deprecated. 

To get the list of all contacts of the deal, use method [crm.deal.contact.items.get](./contacts/crm-deal-contact-items-get.md) or the universal method [crm.item.get](../universal/crm-item-get.md) ||
|| **QUOTE_ID**
[`crm_quote`](../data-types.md) | Quote identifier on which the deal was created. 

More details about the quote can be retrieved with method [crm.item.get](../universal/crm-item-get.md) by passing `entityTypeId = 7` and `id = QUOTE_ID`
||
|| **BEGINDATE**
[`date`](../../data-types.md) | Start date ||
|| **CLOSEDATE**
[`date`](../../data-types.md) | End date ||
|| **OPENED**
[`char`](../../data-types.md) | Whether the deal is accessible to all. Possible values:
- `Y` — yes
- `N` — no ||
|| **CLOSED**
[`char`](../../data-types.md) | Whether the deal is closed. Possible values:
- `Y` — yes
- `N` — no ||
|| **COMMENTS**
[`string`](../../data-types.md) | Comment ||
|| **ASSIGNED_BY_ID**
[`user`](../../data-types.md) | Assigned user ||
|| **CREATED_BY_ID**
[`user`](../../data-types.md) | Created by ||
|| **MODIFY_BY_ID**
[`user`](../../data-types.md) | Modified by ||
|| **MOVED_BY_ID**
[`user`](../../data-types.md) | Identifier of the user who last changed the stage ||
|| **DATE_CREATE**
[`datetime`](../../data-types.md) | Creation date ||
|| **DATE_MODIFY**
[`datetime`](../../data-types.md) | Modification date ||
|| **MOVED_TIME**
[`datetime`](../../data-types.md) | Date of last stage change ||
|| **SOURCE_ID**
[`crm_status`](../data-types.md) | Source. 

More details about the obtained source can be retrieved with method [crm.status.list](../status/crm-status-list.md) by passing in a filter:

```
{
    ENTITY_ID: 'SOURCE',
    STATUS_ID: SOURCE_ID,
}
```
||
|| **SOURCE_DESCRIPTION**
[`string`](../../data-types.md) | Additional source information ||
|| **LEAD_ID**
[`crm_lead`](../data-types.md) | Lead identifier from which the deal was created. 

More details about the lead can be retrieved with method [crm.item.get](../universal/crm-item-get.md) by passing `entityTypeId = 1` and `id = LEAD_ID`
||
|| **ADDITIONAL_INFO**
[`string`](../../data-types.md) | Additional information ||
|| **LOCATION_ID**
[`location`](../../data-types.md) | Location. System field ||
|| **ORIGINATOR_ID**
[`string`](../../data-types.md) | External source ||
|| **ORIGIN_ID**
[`string`](../../data-types.md) | Identifier of the element in the external source ||
|| **UTM_SOURCE**
[`string`](../../data-types.md) | Advertising system ||
|| **UTM_MEDIUM**
[`string`](../../data-types.md) | Traffic type ||
|| **UTM_CAMPAIGN**
[`string`](../../data-types.md) | Advertising campaign designation ||
|| **UTM_CONTENT**
[`string`](../../data-types.md) | Campaign content ||
|| **UTM_TERM**
[`string`](../../data-types.md) | Campaign search condition ||
|| **LAST_ACTIVITY_TIME**
[`datetime`](../../data-types.md) | Date of last activity in timeline ||
|| **LAST_ACTIVITY_BY**
[`user`](../../data-types.md) | Author of last activity in timeline ||
|| **UF_CRM_...**
[`any`](../../data-types.md) | Custom fields. For example, `UF_CRM_25534736`. 

Depending on portal settings, deals may have a set of custom fields of various types. See more in section [о пользовательских полях](./user-defined-fields/index.md) ||
|| **PARENT_ID_...**
[`crm_entity`](../data-types.md) | Relation fields. 

If the portal has smart processes linked to deals, each such smart process has a field that stores the link between that smart process and the deal. The field holds the element identifier of that smart process. 

For example, field `PARENT_ID_153` – link to smart process `entityTypeId=153`, stores the element identifier of this smart process linked to the current deal ||
|#

## Error handling

HTTP status: **400**

```json
{
    "error": "",
    "error_description": "Parameter 'fields' must be array."
}
```

{% include notitle [обработка ошибок](../../../_includes/error-info.md) %}

### Possible error codes

#|
|| **Code** | **Description** | **Value** ||
|| `-` | `ID is not defined or invalid` | The parameter `id` is either missing or is not a positive integer ||
|| `-` | `Access denied` | The user does not have “read” rights for this deal ||
|| `-` | `Not found` | Deals with the provided `id` do not exist ||
|#

{% include [системные ошибки](./../../../_includes/system-errors.md) %}

## Continue learning

- [{#T}](./crm-deal-add.md)
- [{#T}](./crm-deal-update.md)
- [{#T}](./crm-deal-list.md)
- [{#T}](./crm-deal-delete.md)
- [{#T}](./crm-deal-fields.md)