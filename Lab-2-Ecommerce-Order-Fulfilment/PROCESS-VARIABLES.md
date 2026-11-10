# Process Variable Dictionary - Lab 2: E-Commerce Order Processing and Fulfilment

This dictionary specifies all process variables exchanged across inventory services, DMN decision engines, payment gateway REST Connectors, and Tasklist manual review tasks.

| Variable Name | Type | Scope | Originating Activity | Description & Business Purpose | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `orderId` | String | Global | `StartEvent_OrderReceived` | Unique business identifier for the e-commerce purchase order. | `"ORD-2026-001"` |
| `customerRef` | String | Global | `StartEvent_OrderReceived` | Account reference of the purchasing customer. | `"CUST-VIP-881"` |
| `customerCategory` | String | Global | `StartEvent_OrderReceived` | Customer loyalty tier (`"VIP"`, `"REGULAR"`, or `"NEW"`). Feeds into DMN priority rules. | `"VIP"` |
| `productId` | String | Global | `StartEvent_OrderReceived` | Catalog SKU identifier for ordered item (`"LAPTOP-X1"`, `"GPU-SERVER"`, etc.). | `"LAPTOP-X1"` |
| `quantity` | Integer | Global | `StartEvent_OrderReceived` | Number of units ordered by the customer. | `2` |
| `deliveryPreference` | String | Global | `StartEvent_OrderReceived` | Requested delivery speed (`"OVERNIGHT"`, `"EXPRESS"`, `"STANDARD"`). | `"OVERNIGHT"` |
| `paymentToken` | String | Global | `StartEvent_OrderReceived` | Synthetic payment authorization token passed to the Payment Gateway REST Connector. | `"tok_visa_valid"` |
| `stockAvailable` | Boolean | Process | `Task_ValidateAndCheckStock` | Boolean flag indicating whether sufficient units exist in warehouse inventory. | `true` |
| `availableStock` | Integer | Process | `Task_ValidateAndCheckStock` | Real-time warehouse quantity available for the requested SKU. | `45` |
| `unitPrice` | Double | Process | `Task_ValidateAndCheckStock` | Catalog unit price per item in USD. | `1200.0` |
| `orderTotal` | Double | Process | `Task_ValidateAndCheckStock` | Calculated gross total (`unitPrice * quantity`). | `2400.0` |
| `validationStatus` | String | Process | `Task_ValidateAndCheckStock` | Inventory status code (`"IN_STOCK"`, `"OUT_OF_STOCK"`, `"UNKNOWN_SKU"`). | `"IN_STOCK"` |
| `priorityResult` | Object / Map | Activity | `Task_DetermineOrderPriority` | Raw DMN output containing classification and justification. | `{"orderPriority": "Critical", ...}` |
| `orderPriority` | String | Process | `Task_DetermineOrderPriority` | Operational priority assigned by DMN (`"Critical"`, `"High"`, `"Medium"`, `"Standard"`). | `"Critical"` |
| `priorityReason` | String | Process | `Task_DetermineOrderPriority` | Business rationale for assigned order priority. | `"VIP customer with guaranteed overnight delivery SLA"` |
| `verificationStatus` | String | Process | `Task_ManualOrderVerification` | Decision recorded by human risk officer in Tasklist (`"Approved"` or `"Rejected"`). | `"Approved"` |
| `paymentStatus` | String | Process | `Task_ProcessPaymentGateway` | Acquirer status returned by REST Connector (`"SUCCESS"`, `"DECLINED"`, `"ERROR"`). | `"SUCCESS"` |
| `transactionId` | String | Process | `Task_ProcessPaymentGateway` | Acquirer reference ID for settlement tracking. | `"TXN-AUTH-8F12B9A471"` |
| `authCode` | String | Process | `Task_ProcessPaymentGateway` | Authorization approval code from card network. | `"AUTH492817"` |
| `trackingNumber` | String | Process | `Task_DispatchFulfilment` | Logistics courier tracking number generated upon warehouse pack & dispatch. | `"TRK-FEDEX-91A4B8C2"` |
| `fulfilmentStatus` | String | Process | `Task_DispatchFulfilment` | Terminal operational state (`"DISPATCHED"`). | `"DISPATCHED"` |
