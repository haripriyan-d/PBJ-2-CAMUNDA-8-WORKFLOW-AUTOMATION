# REST Connector Specification - Lab 1: Credit Assessment API

## 1. Overview
The **Camunda 8 Out-of-the-Box REST Connector (`io.camunda:http-json:1`)** is configured within `loan-approval-process.bpmn` to invoke a credit assessment microservice endpoint. This enables asynchronous retrieval of creditworthiness scores, risk tiers, and bureau tracking references without requiring custom Java networking code inside the core orchestration layer.

---

## 2. Camunda 8 Connector Configuration

### Task Definition
- **Type**: `io.camunda:http-json:1`
- **Retries**: `3`
- **Activity ID**: `Task_CreditAssessment`
- **Activity Name**: `Call Credit Assessment REST API`

### Input Mappings
| Property Key | Type | Camunda 8 FEEL Expression | Description |
| :--- | :--- | :--- | :--- |
| `method` | String | `"POST"` | HTTP invocation method |
| `url` | String | `"http://localhost:8081/api/v1/credit-assessment"` | Mock Credit Assessment REST endpoint |
| `headers` | Map | `{"Content-Type": "application/json", "Accept": "application/json"}` | Standard JSON payload headers |
| `body` | Context/FEEL | `={ applicantId: applicantId, requestedAmount: requestedAmount, monthlyIncome: monthlyIncome }` | Dynamic request payload constructed from process variables |

### Output Mappings
| Target Variable | Source Expression (FEEL) | Purpose |
| :--- | :--- | :--- |
| `creditScore` | `=response.body.creditScore` | Ingests numeric score (300–850) into process scope |
| `creditTier` | `=response.body.creditTier` | Risk classification tier (`EXCELLENT`, `PRIME`, `MODERATE`, `SUBPRIME`) |
| `assessmentStatus` | `=response.body.assessmentStatus` | Confirms credit assessment status (`COMPLETED`) |

---

## 3. Sample API Payloads

### A. HTTP Request Example
```http
POST /api/v1/credit-assessment HTTP/1.1
Host: localhost:8081
Content-Type: application/json
Accept: application/json

{
  "applicantId": "APP-001",
  "requestedAmount": 15000.0,
  "monthlyIncome": 7500.0
}
```

### B. HTTP Success Response (200 OK)
```json
{
  "applicantId": "APP-001",
  "creditScore": 785,
  "creditTier": "EXCELLENT",
  "assessmentStatus": "COMPLETED",
  "bureauReference": "BUR-EQX-847291",
  "timestamp": "2026-11-10T09:15:32.418Z"
}
```

### C. Simulated Error Response (503 Service Unavailable)
Triggered when `applicantId == "SIMULATE_ERROR"`:
```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json

{
  "error": "SERVICE_UNAVAILABLE",
  "message": "Credit Bureau Gateway is temporarily unreachable (Simulated Outage)."
}
```
**Operate Behavior**: When the REST Connector encounters a non-2xx status code and exhausts retries, Camunda Zeebe raises an incident with error reason `HTTP 503: Service Unavailable`. The operator can diagnose the issue, verify connectivity, and trigger a retry directly in Operate.
