# REST Connector Specification - Lab 3: Mock Hospital Scheduling API

## 1. Overview
The hospital appointment workflow delegates slot availability discovery to the **Camunda 8 Out-of-the-Box REST Connector (`io.camunda:http-json:1`)**. The connector connects to the Hospital Electronic Health Record (EHR) Scheduling API, query available slots for the patient's preferred clinical specialty, and provides slot availability metrics to downstream BPMN routing gateways.

---

## 2. Camunda 8 Connector Configuration

### Task Definition
- **Type**: `io.camunda:http-json:1`
- **Retries**: `3`
- **Activity ID**: `Task_QueryAvailableSlotsRest`
- **Activity Name**: `Retrieve Available Slots from Scheduling REST API`

### Input Mappings
| Property Key | Type | Camunda 8 FEEL Expression | Description |
| :--- | :--- | :--- | :--- |
| `method` | String | `"POST"` | HTTP invocation method |
| `url` | String | `"http://localhost:8081/api/v1/scheduling/available-slots"` | Scheduling service URL |
| `headers` | Map | `{"Content-Type": "application/json", "Accept": "application/json"}` | Standard JSON headers |
| `body` | Context/FEEL | `={ patientId: patientId, appointmentPreference: appointmentPreference, triageCategory: triageCategory }` | Query payload containing clinical preference and triage band |

### Output Mappings
| Target Variable | Source Expression (FEEL) | Purpose |
| :--- | :--- | :--- |
| `slotsAvailable` | `=response.body.slotsAvailable` | Boolean indicating slot availability (`true` / `false`) |
| `slotCount` | `=response.body.slotCount` | Integer count of open consultation slots |
| `availableSlots` | `=response.body.availableSlots` | Array of ISO/formatted date-time strings |
| `recommendedDoctor` | `=response.body.recommendedDoctor` | Lead physician assigned to specialty |

---

## 3. Sample API Payloads

### A. HTTP Request Example
```http
POST /api/v1/scheduling/available-slots HTTP/1.1
Host: localhost:8081
Content-Type: application/json
Accept: application/json

{
  "patientId": "PAT-SYNTH-101",
  "appointmentPreference": "General Practice",
  "triageCategory": "Routine"
}
```

### B. HTTP Success Response - Available Slots Found (200 OK)
```json
{
  "patientId": "PAT-SYNTH-101",
  "appointmentPreference": "General Practice",
  "triageCategory": "Routine",
  "slotsAvailable": true,
  "slotCount": 3,
  "availableSlots": [
    "Tomorrow at 09:30 AM (Consultation Room 3B)",
    "Tomorrow at 02:00 PM (Consultation Room 1A)",
    "Day After Tomorrow at 11:15 AM (Consultation Room 2C)"
  ],
  "recommendedDoctor": "Dr. Emily Watson (Lead General Physician)",
  "statusMessage": "Slots successfully retrieved from Hospital EHR.",
  "queryTimestamp": "2026-11-10T11:04:18.902Z"
}
```

### C. HTTP Response - Zero Slots Available (200 OK)
```json
{
  "patientId": "PAT-SYNTH-412",
  "appointmentPreference": "Radiology MRI",
  "triageCategory": "Routine",
  "slotsAvailable": false,
  "slotCount": 0,
  "availableSlots": [],
  "recommendedDoctor": "None (Department at 100% capacity)",
  "statusMessage": "All clinical slots allocated. Manual staff override required.",
  "queryTimestamp": "2026-11-10T11:07:44.201Z"
}
```

### D. Simulated Server Error Incident (500 Internal Server Error)
Triggered when `appointmentPreference == "SIMULATE_500"`:
```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "error": "INTERNAL_SERVER_ERROR",
  "message": "Hospital Scheduling Database deadlocked. Zeebe incident triggered for Operate diagnosis."
}
```
**Operate Behavior**: Camunda Zeebe registers an incident on `Task_QueryAvailableSlotsRest` with `HTTP 500: Internal Server Error`. The clinician or administrator investigates the incident in Operate, fixes the mock service endpoint/restarts the service, and triggers **Retry Incident** to resume booking.
