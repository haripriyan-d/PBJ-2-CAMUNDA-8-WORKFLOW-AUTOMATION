# Camunda 8 External Job Workers & Mock REST Microservices

This directory contains the production-grade **Java 17+ / Spring Boot 3** external job worker implementation and embedded mock REST APIs powering Labs 1, 2, and 3.

---

## 1. Technologies & Dependencies
- **Java**: 17 or higher (tested on OpenJDK / Oracle JDK 24)
- **Spring Boot**: 3.3.3
- **Camunda 8 Starter**: `io.camunda:spring-boot-starter-camunda:8.5.3` (Zeebe Spring Client)
- **Spring Web & Actuator**: Exposing embedded mock REST endpoints, metrics, and health checks on port `8081`.

---

## 2. Worker Inventory & Job Types

| Lab | Job Worker Type | Class | Responsibility |
| :--- | :--- | :--- | :--- |
| **Lab 1** | `applicant-validator` | `LoanWorker.java` | Validates loan applicant inputs, computes Debt-to-Income (DTI), checks threshold rules, and handles intentional incident recovery test modes. |
| **Lab 1** | `loan-disbursement` | `LoanWorker.java` | Generates loan sanction documentation and disbursement reference tokens. |
| **Lab 1, 2, 3** | `notification-service` | `LoanWorker.java` | Dispatches simulated applicant/customer notifications via email/SMS. |
| **Lab 2** | `order-validator-inventory`| `OrderWorker.java` | Validates product SKU catalog, queries live inventory quantities, and calculates item prices and gross totals. |
| **Lab 2** | `fulfilment-dispatcher` | `OrderWorker.java` | Generates warehouse packing slips and courier tracking numbers. |
| **Lab 3** | `patient-registration-validator` | `HospitalTriageWorker.java` | Validates synthetic patient intake data, contact fields, and symptom descriptions. |
| **Lab 3** | `appointment-booking-worker` | `HospitalTriageWorker.java` | Reserves confirmed slots in the electronic hospital scheduling database. |

---

## 3. Mock REST Services Inventory

| Endpoint | Method | Class | Description |
| :--- | :---: | :--- | :--- |
| `/api/v1/credit-assessment` | `POST` | `MockCreditApiController` | Credit scoring API returning creditScore (300–850), creditTier, and bureau tracking references. Simulates 503 errors and timeouts. |
| `/api/v1/payments/process` | `POST` | `MockPaymentGatewayController` | Payment processing gateway returning transaction IDs, approval codes, or simulated declines and 504 timeouts. |
| `/api/v1/scheduling/available-slots` | `POST` | `MockHospitalSchedulingController`| Hospital scheduling service returning available appointment slots, specialist names, or zero-slot waitlist conditions. |

---

## 4. Setup and Execution Instructions

### Prerequisites
- JDK 17 or higher installed (`java -version`)
- Maven installed (`mvn -version`) or use bundled scripts

### Running the Worker Application
```powershell
# Navigate to workers directory
cd spring-boot-workers

# Build and execute with Maven
mvn clean spring-boot:run
```

The application will start on `http://localhost:8081`.

### Connecting to Camunda 8 (Zeebe)
To connect the workers to a live Camunda 8 cluster:
1. Open `src/main/resources/application.yml`
2. Set `camunda.client.zeebe.enabled: true`
3. Provide your Zeebe broker address (e.g., `127.0.0.1:26500` for Camunda 8 Self-Managed, or Zeebe cluster client credentials for Camunda 8 SaaS).
