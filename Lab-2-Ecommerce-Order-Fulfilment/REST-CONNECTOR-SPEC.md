# REST Connector Specification - Lab 2: Payment Gateway REST API

## 1. Overview
In `ecommerce-order-process.bpmn`, payment execution is delegated to the **Camunda 8 Out-of-the-Box REST Outbound Connector (`io.camunda:http-json:1` with template `io.camunda.connectors.HttpJson.v1`)**. This connector submits order payment credentials and transaction totals to a simulated acquirer payment service, consuming JSON responses and propagating status codes to downstream BPMN routing gateways.

---

## 2. Camunda 8 Connector Configuration

### Task Definition & Modeler Template
- **Modeler Template**: `io.camunda.connectors.HttpJson.v1` (Camunda 8 REST Outbound Connector)
- **Modeler Version**: `1`
- **Job Worker Type**: `io.camunda:http-json:1`
- **Retries**: `3`
- **Activity ID**: `Task_ProcessPaymentGateway`
- **Activity Name**: `Invoke Payment Gateway (REST Outbound Connector)`

### Task Headers
| Header Key | Header Value | Description |
| :--- | :--- | :--- |
| `resultVariable` | `response` | Ingests full HTTP response object into workflow variables |
| `errorExpression` | `""` | Evaluates HTTP status code into Zeebe Error Events |
| `resultExpression` | `""` | Result extraction expression |

### Input Mappings
| Property Key | Type | Camunda 8 FEEL Expression | Description |
| :--- | :--- | :--- | :--- |
| `method` | String | `"post"` | HTTP verb |
| `url` | String | `"http://localhost:8081/api/v1/payments/process"` | Payment Gateway endpoint |
| `headers` | Map | `{"Content-Type": "application/json", "Accept": "application/json"}` | Request headers |
| `body` | Context/FEEL | `={ orderId: orderId, customerRef: customerRef, amount: orderTotal, paymentToken: paymentToken }` | Dynamic request payload constructed from order variables |
| `connectionTimeoutInSeconds` | Number | `20` | Timeout threshold |
| `authentication.type` | String | `"noAuth"` | Acquirer authentication method |

### Output Mappings
| Target Variable | Source Expression (FEEL) | Purpose |
| :--- | :--- | :--- |
| `paymentStatus` | `=response.body.paymentStatus` | Acquirer outcome (`"SUCCESS"`, `"DECLINED"`, `"ERROR"`) |
| `transactionId` | `=response.body.transactionId` | Unique acquirer transaction reference |
| `authCode` | `=response.body.authCode` | Card network authorization code |

---

## 3. Sample API Payloads

### A. HTTP Request Example
```http
POST /api/v1/payments/process HTTP/1.1
Host: localhost:8081
Content-Type: application/json
Accept: application/json

{
  "orderId": "ORD-2026-001",
  "customerRef": "CUST-VIP-881",
  "amount": 2400.0,
  "paymentToken": "tok_visa_valid"
}
```

### B. HTTP Success Response (200 OK)
```json
{
  "orderId": "ORD-2026-001",
  "amount": 2400.0,
  "currency": "USD",
  "paymentStatus": "SUCCESS",
  "transactionId": "TXN-AUTH-8F12B9A471",
  "authCode": "AUTH492817",
  "cardNetwork": "VISA_SYNTHETIC",
  "timestamp": "2026-11-10T10:18:42.102Z"
}
```

### C. HTTP Declined Response (200 OK with DECLINED status)
```json
{
  "orderId": "ORD-2026-003",
  "amount": 180.0,
  "currency": "USD",
  "paymentStatus": "DECLINED",
  "declineReason": "INSUFFICIENT_FUNDS",
  "transactionId": "TXN-DECLINED-4D9A1E02",
  "timestamp": "2026-11-10T10:22:15.311Z"
}
```

### D. Simulated Gateway Timeout Incident (504 Gateway Timeout)
Triggered when `paymentToken == "tok_gateway_timeout_simulate"`:
```http
HTTP/1.1 504 Gateway Timeout
Content-Type: application/json

{
  "error": "GATEWAY_TIMEOUT",
  "message": "Payment Gateway upstream acquirer timed out. Incident recorded in Camunda Operate."
}
```
**Operate Behavior**: Camunda Zeebe raises an incident with message `HTTP 504 Gateway Timeout`. The operations engineer diagnoses the incident in Operate, replaces `paymentToken` with a valid backup token, and triggers **Retry Incident** to finish fulfilment.
