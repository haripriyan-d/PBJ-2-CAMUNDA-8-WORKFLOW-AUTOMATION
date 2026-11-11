# Presentation Guide: Camunda 8 Workflow Automation (Lab 1 & Lab 3)

**Author:** haripriyan-d  
**Course / Assignment:** PBJ-2 Practical Assignment: Camunda 8 End-to-End Workflow Automation  
**Repository:** [github.com/haripriyan-d/PBJ-2-CAMUNDA-8-WORKFLOW-AUTOMATION](https://github.com/haripriyan-d/PBJ-2-CAMUNDA-8-WORKFLOW-AUTOMATION)  

---

## Slide 1: Title & Executive Architecture

### Slide Content:
- **Title**: Camunda 8 End-to-End Workflow Automation: Architecture & Technical Defense
- **Focus Areas**: 
  - Lab 1: End-to-End Loan Approval Automation
  - Lab 3: End-to-End Hospital Appointment & Patient Triage Management
- **Key Architectural Pillars**:
  1. **BPMN 2.0 State Machine Orchestration**: Zeebe broker managing distributed, scalable workflow execution.
  2. **DMN 1.3 Decision Engines**: Decoupled, auditable business logic using FIRST hit policy tables.
  3. **Camunda 8 REST Outbound Connectors**: Declarative, codeless HTTP service integrations (`io.camunda.connectors.HttpJson.v1`).
  4. **Spring Boot External Job Workers**: Asynchronous, long-polling distributed microservice task handlers.
  5. **Camunda Tasklist**: Human-in-the-loop task routing with role-based candidate groups and forms.
  6. **Camunda Operate**: Real-time instance telemetry, incident diagnosis, variable payload mutation, and zero-downtime retry.

### Speaker Script:
> "Good morning/afternoon. Today I am presenting our implementation of the PBJ-2 Practical Assignment on Camunda 8 End-to-End Workflow Automation, focusing in depth on Lab 1: Loan Approval Automation and Lab 3: Hospital Appointment and Patient Triage Management.
>
> In modern enterprise software, workflow engines cannot rely on tightly-coupled monolithic code. Camunda 8 provides a cloud-native, distributed event-driven architecture powered by the Zeebe broker. We combine BPMN orchestration with external Java Spring Boot job workers, out-of-the-box REST Outbound Connectors, DMN decision tables, Tasklist human reviews, and Operate incident recovery. Let us dive directly into Lab 1."

---

## Slide 2: Lab 1 — Process Architecture & BPMN Element Breakdown

### Visual Layout:
- Pool: `Participant_LoanSystem` ("Camunda 8 End-to-End Loan Approval Platform")
- Two Horizontal Swimlanes:
  1. `Lane_AutomatedServices` (System & Automated Decisioning)
  2. `Lane_UnderwriterReview` (Credit Underwriter Tasklist Human Review)

### Element-by-Element Breakdown:

1. **Start Event (`StartEvent_LoanApplied`)**:
   - **Type**: Plain Start Event.
   - **Label**: "Loan Application Submitted".
   - **Role**: Ingests the initial loan application payload containing `applicantId`, `applicantName`, `requestedAmount`, `monthlyIncome`, `employmentYears`, and `email`.

2. **Service Task 1 (`Task_ValidateApplicant`)**:
   - **Type**: External Job Worker (`applicant-validator`).
   - **Label**: "Validate Applicant Information".
   - **Implementation**: Handled by Java/Spring Boot `LoanWorker.java`. Validates mandatory fields, checks for negative numbers, and computes initial Debt-to-Income (DTI) ratio based on estimated 36-month EMI.
   - **Zeebe Extension**: `<zeebe:taskDefinition type="applicant-validator" retries="3" />`.

3. **Exclusive Gateway 1 (`Gateway_Validation`)**:
   - **Type**: XOR Exclusive Gateway.
   - **Condition Flow 1 (`Flow_Val_Valid`)**: Default path when `isValid == true` $\to$ advances to Credit Assessment.
   - **Condition Flow 2 (`Flow_Val_Invalid`)**: Expression `=isValid = false` $\to$ routes to rejection.

4. **Service Task 2 (`Task_CreditAssessment`) — REST Outbound Connector**:
   - **Type**: Camunda 8 REST Outbound Connector (`io.camunda:http-json:1` with template `io.camunda.connectors.HttpJson.v1`).
   - **Label**: "Call Credit Assessment REST API (REST Outbound Connector)".
   - **Role**: Asynchronously queries the credit assessment REST API on port 8081, returning bureau credit rating, credit tier, and verification status.

5. **Business Rule Task (`Task_EvaluateLoanDmn`)**:
   - **Type**: Camunda 8 DMN Decision Task.
   - **Called Decision ID**: `Decision_LoanEligibility`.
   - **Result Variable**: `dmnDecisionResult`.
   - **Role**: Evaluates Credit Score, DTI %, and Monthly Income to return `"Approved"`, `"Rejected"`, or `"Manual Review"`.

6. **Exclusive Gateway 2 (`Gateway_DmnOutcome`)**:
   - **Type**: XOR Gateway routing the process into three distinct business paths:
     - Path A: `=dmnDecision = "Approved"` $\to$ Straight-through automated disbursement.
     - Path B: `=dmnDecision = "Rejected"` $\to$ Adverse action rejection notice.
     - Path C: Default (`dmnDecision = "Manual Review"`) $\to$ Escalates across swimlanes into Tasklist.

7. **User Task (`Task_ManualUnderwriterReview`)**:
   - **Type**: Camunda 8 Human User Task (`io.camunda.zeebe:userTask`).
   - **Candidate Groups**: `loan-officers, underwriters`.
   - **Form ID**: `Form_ManualLoanReview`.
   - **Role**: Presents the underwriter with applicant metrics (Income, DTI, Credit Score) in Tasklist to record a human verdict (`Approved` / `Rejected`) and commentary.

8. **Exclusive Gateway 3 (`Gateway_UnderwriterDecision`)**:
   - **Type**: XOR Gateway evaluating human review outcome:
     - `=reviewDecision = "Approved"` $\to$ Disbursement.
     - Default $\to$ Rejection.

9. **Terminal Activities & End Events**:
   - `Task_PrepareDisbursement` (Worker: `loan-disbursement`) $\to$ `Task_NotifyApproved` (Send Task) $\to$ `EndEvent_Approved` ("Loan Sanctioned & Disbursed").
   - `Task_NotifyRejected` (Send Task) $\to$ `EndEvent_Rejected` ("Loan Rejected").
   - `Task_SendValidationFailure` (Send Task) $\to$ `EndEvent_ValidationFailed` ("Rejected - Data Validation Error").

### Speaker Script:
> "In Lab 1, the BPMN diagram is strictly partitioned into two swimlanes: Automated Services and Credit Underwriter.
> Every element serves an explicit architectural purpose. Notice that straight-through processing is guaranteed for prime applicants—they flow from the start event, through worker validation, the REST outbound connector, and DMN decisioning straight to automated disbursement without human delay.
> However, borderline cases automatically traverse into the Underwriter swimlane, instantiating a user task in Camunda Tasklist. This demonstrates how Camunda 8 unifies human workflows with microservice automation."

---

## Slide 3: Lab 1 — REST Outbound Connector Deep Dive

### Slide Content:
- **Connector Identity**: Camunda 8 Official HTTP JSON Connector (`io.camunda:http-json:1`)
- **Modeler Template**: `io.camunda.connectors.HttpJson.v1`
- **Connector Protocol**: Outbound REST over HTTP/1.1 or HTTP/2
- **Endpoint Invoked**: `POST http://localhost:8081/api/v1/credit-assessment`

### Technical XML Configuration:
```xml
<bpmn:serviceTask id="Task_CreditAssessment" 
                  name="Call Credit Assessment REST API (REST Outbound Connector)"
                  zeebe:modelerTemplate="io.camunda.connectors.HttpJson.v1"
                  zeebe:modelerTemplateVersion="1"
                  zeebe:modelerTemplateIcon="data:image/svg+xml;utf8,...">
  <bpmn:extensionElements>
    <!-- Zeebe Job Type for Connector Runtime -->
    <zeebe:taskDefinition type="io.camunda:http-json:1" retries="3" />
    
    <!-- Connector Headers -->
    <zeebe:taskHeaders>
      <zeebe:header key="resultVariable" value="response" />
      <zeebe:header key="errorExpression" value="" />
      <zeebe:header key="resultExpression" value="" />
    </zeebe:taskHeaders>
    
    <!-- Input & Output FEEL Mappings -->
    <zeebe:ioMapping>
      <zeebe:input source="http://localhost:8081/api/v1/credit-assessment" target="url" />
      <zeebe:input source="post" target="method" />
      <zeebe:input source="={applicantId: applicantId, requestedAmount: requestedAmount, monthlyIncome: monthlyIncome}" target="body" />
      <zeebe:input source="20" target="connectionTimeoutInSeconds" />
      <zeebe:input source="noAuth" target="authentication.type" />
      
      <!-- Extract response body fields directly into process variables -->
      <zeebe:output source="=response.body.creditScore" target="creditScore" />
      <zeebe:output source="=response.body.creditTier" target="creditTier" />
      <zeebe:output source="=response.body.assessmentStatus" target="assessmentStatus" />
    </zeebe:ioMapping>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

### Key Advantages of Camunda 8 REST Outbound Connector:
1. **Zero Glue Code**: Eliminates boilerplate Java HTTP client classes, connection pool management, and manual serialization.
2. **FEEL Expression Mapping**: Dynamic payload assembly directly from process variables (`={applicantId: applicantId, ...}`).
3. **Resilience & Timeouts**: Built-in retry policies (`retries="3"`) and connection timeout enforcement (`connectionTimeoutInSeconds="20"`).
4. **Declarative Output Extraction**: Directly maps nested JSON keys (`response.body.creditScore`) to process variables without writing custom deserializers.

### Speaker Script:
> "Now let us examine the REST Outbound Connector in detail. Instead of writing custom Java networking code using `RestTemplate` or `HttpClient`, we leverage Camunda 8's native REST Outbound Connector with template ID `io.camunda.connectors.HttpJson.v1`.
> Under the hood, Zeebe delegates this task to the Camunda Connector Runtime using job type `io.camunda:http-json:1`. Using FEEL expressions, we dynamically construct the JSON request body directly from process variables. When the HTTP 200 response returns, the connector automatically extracts `response.body.creditScore` and `creditTier` into the process instance context, ready for immediate ingestion by the DMN engine."

---

## Slide 4: Lab 1 — DMN Decision Rules & Failure Modes Analysis

### DMN Decision Table: `Decision_LoanEligibility` (Hit Policy: FIRST)
| Rule | Credit Score | DTI Ratio (%) | Monthly Income ($) | Output: Decision | Output: Reason |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **R1** | `>= 740` | `<= 35` | `>= 3500` | `"Approved"` | Prime applicant: High credit score and healthy debt-to-income ratio |
| **R2** | `< 600` | `-` | `-` | `"Rejected"` | Credit score below minimum lending threshold (600) |
| **R3** | `-` | `> 50` | `-` | `"Rejected"` | Debt-to-income ratio exceeds statutory maximum threshold (50%) |
| **R4** | `-` | `-` | `< 2000` | `"Rejected"` | Monthly verifiable income below minimum qualification bar ($2,000) |
| **R5** | `[600..739]` | `<= 45` | `>= 2500` | `"Manual Review"` | Borderline risk parameters require human underwriter discretionary assessment |
| **R6** | `-` | `-` | `-` | `"Manual Review"` | Non-standard risk tier requires underwriter policy override |

### Complete Failure Modes & Incident Recovery Table:

| Failure Mode | Trigger / Scenario | BPMN / Engine Handling | Operate Diagnostics | Remediation & Recovery |
| :--- | :--- | :--- | :--- | :--- |
| **F1: Data Validation Failure** | Missing name or negative loan amount ($0) | Worker returns `isValid = false` $\to$ Exclusive Gateway routes to `Flow_Val_Invalid` | No incident (graceful business rejection path) | Generates validation rejection email; process terminates at `EndEvent_ValidationFailed`. |
| **F2: Regulatory Rejection** | Score 540, Income $1,800, DTI 65% (TC-02) | DMN rule R2/R3 triggers `"Rejected"` $\to$ Gateway routes to `Task_NotifyRejected` | Execution path highlighted in Operate; terminal state recorded | Adverse action notice dispatched to applicant; terminates at `EndEvent_Rejected`. |
| **F3: REST Connector 503 Outage** | External Credit Bureau endpoint unreachable (`SIMULATE_ERROR`, TC-04) | Connector exhausts 3 retries $\to$ Zeebe raises an **Incident** on `Task_CreditAssessment` | Red incident badge in Operate: `HTTP 503 Service Unavailable: Credit Bureau Gateway unreachable` | Bureau service restored. Operator clicks **"Retry Incident"** in Operate. Job re-activates and succeeds without dropping instance. |
| **F4: Worker Crash (Negative Income)** | `monthlyIncome = -500`, flag `simulateWorkerFailure=true` (TC-05) | Worker throws unhandled `IllegalArgumentException` $\to$ Zeebe creates an **Incident** (`JOB_NO_RETRIES`) | Red incident on `Task_ValidateApplicant` with complete stack trace | In Operate, operator edits `monthlyIncome` to `4800.0`, flips flag to `false`, and clicks **"Retry Incident"**. Worker succeeds. |

### Speaker Script:
> "A robust workflow must handle both business rejections and technical infrastructure incidents.
> In our DMN table, notice the FIRST hit policy. Rule 1 captures prime borrowers, while Rules 2 through 4 act as regulatory guardrails, rejecting subprime scores or excessive debt burdens.
> On the technical side, we simulated two critical failure modes in Camunda Operate. In Scenario 4, when the credit bureau simulated a 503 outage, Zeebe preserved process state and raised an incident. Once the service was restored, we retried the incident in Operate without any data loss.
> In Scenario 5, an invalid negative income caused our Java worker to throw an exception. We diagnosed the incident in Operate, mutated `monthlyIncome` to $4,800 directly in the Operate variable inspector, and clicked Retry. The worker completed successfully and disbursed the loan."

---

## Slide 5: Lab 3 — Hospital Triage & Patient Journey BPMN Breakdown

### Visual Layout:
- Pool: `Participant_HospitalPlatform` ("Camunda 8 Hospital Appointment & Patient Triage Platform")
- Two Horizontal Swimlanes:
  1. `Lane_AutomatedTriage` (Automated Registration, Triage & Scheduling Engine)
  2. `Lane_ClinicalStaff` (Authorised Clinical Staff & Emergency Team - Tasklist)

### Element-by-Element Breakdown:

1. **Start Event (`StartEvent_AppointmentRequested`)**:
   - Ingests synthetic clinical data: `patientId`, `patientName`, `appointmentPreference`, `symptomsSummary`, `urgencyScore` (1-10), and `symptomsSeverity`.

2. **Service Task 1 (`Task_ValidatePatientRegistration`)**:
   - **Worker Type**: `patient-registration-validator`.
   - **Role**: Validates patient identity formatting and ensures symptoms description is non-empty. Emits `registrationValid` boolean.

3. **Exclusive Gateway 1 (`Gateway_RegistrationValid`)**:
   - Checks validity. If invalid $\to$ notifies patient and terminates at `EndEvent_RegistrationRejected`. If valid $\to$ proceeds to DMN.

4. **Business Rule Task (`Task_EvaluatePatientTriageDmn`)**:
   - **Called Decision**: `Decision_PatientTriage`.
   - **Role**: Applies predefined clinical guidelines to classify acuity into `"Urgent Assessment"`, `"Priority Review"`, or `"Routine"`, attaching statutory response SLAs (15m, 4h, 48h).

5. **Exclusive Gateway 2 (`Gateway_TriageBranch`) — The Emergency Bypass**:
   - If `=triageCategory = "Urgent Assessment"` $\to$ **Immediate Emergency Bypass**: Routes directly across swimlanes into `Lane_ClinicalStaff`!
   - Default (`Routine / Priority`) $\to$ Proceeds to scheduling slot query.

6. **User Task 1 (`Task_ImmediateHumanAssessment`) — Code Red Emergency**:
   - **Candidate Groups**: `emergency-physicians, trauma-nurses`.
   - **Role**: Bypasses all outpatient scheduling queues; prompts trauma team to pre-allocate resuscitation bays.
   - **End Event**: `EndEvent_EmergencyCareAdmitted` ("Admitted for Immediate Clinical Intervention").

7. **Service Task 2 (`Task_QueryAvailableSlotsRest`) — REST Outbound Connector**:
   - **Template**: `io.camunda.connectors.HttpJson.v1`.
   - **Role**: Queries the Hospital EHR Scheduling REST API (`/api/v1/scheduling/available-slots`) to discover open consultation slots.

8. **Exclusive Gateway 3 (`Gateway_SlotAvailability`) — Three-Way Clinical Branch**:
   - **Branch 1 (No Slots)**: `=slotsAvailable = false or slotCount = 0` $\to$ Routes to `Task_StaffSlotOverrideReview` (User Task) $\to$ `EndEvent_Waitlisted`.
   - **Branch 2 (Priority Review)**: `=triageCategory = "Priority Review"` $\to$ Routes to `Task_PriorityStaffReview` (User Task) for clinical nurse chart review.
   - **Branch 3 (Routine Available)**: Default $\to$ Routes to `Task_AutoBookAppointment` (Worker: `appointment-booking-worker`).

9. **Terminal Notification & End Events**:
   - `Task_SendAppointmentConfirmation` (Send Task) dispatches SMS/email confirmation $\to$ `EndEvent_AppointmentConfirmed`.

### Speaker Script:
> "Moving to Lab 3, the clinical appointment workflow addresses acute triage acuity and scheduling resilience.
> The architectural highlight here is the Emergency Bypass Gateway. If a patient presents with an urgency score of 8 or above—such as crushing chest pain—the workflow does NOT query outpatient scheduling calendars. It instantly routes through the exclusive gateway into the Emergency Physician lane, instantiating a Code Red human assessment task.
> Conversely, stable patients proceed to the REST Outbound Connector to query live doctor calendars. If slots are open, routine cases book automatically, while priority cases prompt a triage nurse to review the clinical chart."

---

## Slide 6: Lab 3 — REST Outbound Connector & Hospital EHR Integration

### Slide Content:
- **Connector Identity**: Camunda 8 REST Outbound Connector (`io.camunda:http-json:1`)
- **Template ID**: `io.camunda.connectors.HttpJson.v1`
- **Target Endpoint**: `POST http://localhost:8081/api/v1/scheduling/available-slots`
- **Security & Timeout**: `noAuth` (synthetic sandbox), `20` seconds connection timeout

### Technical XML Implementation:
```xml
<bpmn:serviceTask id="Task_QueryAvailableSlotsRest" 
                  name="Retrieve Available Slots (REST Outbound Connector)"
                  zeebe:modelerTemplate="io.camunda.connectors.HttpJson.v1"
                  zeebe:modelerTemplateVersion="1"
                  zeebe:modelerTemplateIcon="data:image/svg+xml;utf8,...">
  <bpmn:extensionElements>
    <zeebe:taskDefinition type="io.camunda:http-json:1" retries="3" />
    <zeebe:taskHeaders>
      <zeebe:header key="resultVariable" value="response" />
      <zeebe:header key="errorExpression" value="" />
      <zeebe:header key="resultExpression" value="" />
    </zeebe:taskHeaders>
    <zeebe:ioMapping>
      <zeebe:input source="http://localhost:8081/api/v1/scheduling/available-slots" target="url" />
      <zeebe:input source="post" target="method" />
      <zeebe:input source="={patientId: patientId, appointmentPreference: appointmentPreference, triageCategory: triageCategory}" target="body" />
      <zeebe:input source="20" target="connectionTimeoutInSeconds" />
      <zeebe:input source="noAuth" target="authentication.type" />
      
      <!-- Ingest slot availability & recommended clinician into process scope -->
      <zeebe:output source="=response.body.slotsAvailable" target="slotsAvailable" />
      <zeebe:output source="=response.body.slotCount" target="slotCount" />
      <zeebe:output source="=response.body.availableSlots" target="availableSlots" />
      <zeebe:output source="=response.body.recommendedDoctor" target="recommendedDoctor" />
    </zeebe:ioMapping>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

### JSON Request & Response Exchange:
```json
// POST /api/v1/scheduling/available-slots
{
  "patientId": "PAT-SYNTH-101",
  "appointmentPreference": "General Practice",
  "triageCategory": "Routine"
}

// HTTP 200 OK Response
{
  "patientId": "PAT-SYNTH-101",
  "slotsAvailable": true,
  "slotCount": 3,
  "availableSlots": [
    "Tomorrow at 09:30 AM (Room 3B)",
    "Tomorrow at 02:00 PM (Room 1A)",
    "Day After Tomorrow at 11:15 AM (Room 2C)"
  ],
  "recommendedDoctor": "Dr. Emily Watson (Lead General Physician)",
  "statusMessage": "Slots successfully retrieved from Hospital EHR."
}
```

### Speaker Script:
> "Slide 6 illustrates our REST Outbound Connector implementation for the Hospital EHR scheduling microservice.
> The connector sends the synthetic patient identifier, requested medical department, and DMN-derived triage category to the mock EHR endpoint.
> The connector maps the returned JSON array of available appointment dates and the recommended attending physician directly into process variables `availableSlots` and `recommendedDoctor`.
> If the department is operating at 100% capacity, the API returns `slotsAvailable: false` and `slotCount: 0`, dynamically triggering downstream gateway routing to the staff waitlist override task."

---

## Slide 7: Lab 3 — Clinical Triage Rules & Incident Handling

### Predefined Educational Triage DMN: `Decision_PatientTriage` (Hit Policy: FIRST)
| Rule | Urgency Score (1-10) | Symptoms Severity | Triage Classification | Target Response | Clinical Protocol |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **R1** | `>= 8` | `-` | `"Urgent Assessment"` | `15` min | Code Red: Immediate emergency human triage and trauma bay allocation |
| **R2** | `-` | `"CRITICAL", "ACUTE"` | `"Urgent Assessment"` | `15` min | Code Red: Acute symptom profile requires direct senior clinician assessment |
| **R3** | `[5..7]` | `-` | `"Priority Review"` | `240` min | Code Yellow: Priority nursing chart review and expedited slot allocation |
| **R4** | `-` | `"MODERATE"` | `"Priority Review"` | `240` min | Code Yellow: Semi-urgent clinical condition requires same-day specialist slot |
| **R5** | `-` | `-` | `"Routine"` | `2880` min (48h) | Code Green: Routine outpatient consultation queue within 48 hours |

### Complete Failure Modes & Incident Recovery Table:

| Failure Mode | Trigger / Scenario | BPMN / Engine Handling | Operate Diagnostics | Remediation & Recovery |
| :--- | :--- | :--- | :--- | :--- |
| **F1: Malformed Patient Intake** | Missing patient name or blank chief complaint | Registration worker sets `registrationValid = false` $\to$ Gateway routes to `Flow_Reg_Invalid` | Straightforward process routing | Patient alerted to correct registration details; terminates at `EndEvent_RegistrationRejected`. |
| **F2: Capacity Saturation (No Slots)** | Specialized MRI consultation requested (`Radiology MRI`, TC-04) | Scheduling API returns `slotsAvailable = false, slotCount = 0` $\to$ Gateway routes to `Flow_Slot_None` | Visual token pauses on `Task_StaffSlotOverrideReview` | Staff accesses Tasklist, reviews clinical notes, places patient on expedited waitlist (`EndEvent_Waitlisted`). |
| **F3: Scheduling API 500 Deadlock** | Scheduling database deadlocked (`SIMULATE_500`, TC-05) | Connector encounters HTTP 500 internal server error $\to$ Zeebe raises an **Incident** | Red incident badge on `Task_QueryAvailableSlotsRest`: `HTTP 500: Hospital Scheduling Database deadlocked` | Database connection pool recycled/mock route corrected. Operator clicks **"Retry Incident"** in Operate; process completes booking. |
| **F4: Master Patient Index (MPI) Timeout** | Synthetic patient ID `SIMULATE_WORKER_FAULT` | Registration worker throws RuntimeException $\to$ Zeebe halts job | Incident visible in Operate on `Task_ValidatePatientRegistration` | Operator diagnoses network glitch, verifies MPI connectivity, and triggers **Retry Incident** in Operate. |

### Speaker Script:
> "In Lab 3, patient safety and operational resilience dictate our failure handling.
> In Scenario 4, when all MRI radiology slots were fully booked, the workflow did not crash or reject the patient. The Exclusive Gateway gracefully routed the case to `Task_StaffSlotOverrideReview`, allowing hospital staff to manage waitlist quotas in Tasklist.
> In Scenario 5, we intentionally simulated an unhandled HTTP 500 Internal Server Error in the scheduling microservice. In Camunda Operate, the incident was visibly isolated on the REST Outbound Connector task. The patient's state was preserved safely. Once the scheduling service recovered, the operator clicked 'Retry Incident' in Operate, and the appointment was immediately confirmed."

---

## Slide 8: Technical Defense Summary & Examiner Q&A Guide

### Key Questions & Answers for Technical Evaluation:

**Q1: Why use a Camunda 8 REST Outbound Connector instead of writing custom Java code in a Service Task worker?**
> *Answer*: "The Camunda 8 REST Outbound Connector provides a declarative, cloud-native integration standard. It eliminates custom networking glue code, reduces microservice maintenance, supports native FEEL expression mappings, and integrates directly with Camunda 8's connector runtime for unified monitoring, retries, and secret management."

**Q2: What is the exact difference between how Zeebe handles business rejections versus system incidents?**
> *Answer*: "Business rejections (such as an adverse DMN credit score or invalid form inputs) are normal business flow alternatives modeled explicitly with XOR Gateways and End Events. 
> System incidents (such as an unhandled Java worker exception, network timeout, or HTTP 500) halt the specific token in Zeebe, preserving all execution variables without failing the instance. This enables operators to diagnose the root cause in Camunda Operate, correct variables if necessary, and retry the job with zero downtime."

**Q3: How does the DMN Decision Table integrate with the BPMN workflow in Camunda 8?**
> *Answer*: "The Business Rule Task utilizes `<zeebe:calledDecision decisionId="..." resultVariable="..." />`. Zeebe passes workflow variables (like `creditScore`, `debtToIncomeRatio`, and `monthlyIncome`) as context into the DMN engine. The evaluated rule outcome is mapped back into process variables using `<zeebe:ioMapping>`, which subsequent BPMN sequence flow conditions evaluate using FEEL."

---

### Verification & Live Demonstration Checklist:
- [x] All 15 automated test cases passing (`python test_all_scenarios.py`)
- [x] 18 Live-captured screenshots stored in repository (`01_modeler_bpmn.png` to `06_worker_execution_logs.png`)
- [x] Spring Boot workers active on port `8081` with mock REST controllers
- [x] Web simulation platform live on port `8080` with interactive Modeler, Operate, and Tasklist panels
- [x] Clean Git commit history pushed to GitHub main branch.
