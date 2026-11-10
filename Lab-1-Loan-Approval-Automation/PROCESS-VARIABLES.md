# Process Variable Dictionary - Lab 1: Loan Approval Automation

This dictionary documents all process variables exchanged across activities, external job workers, DMN decision tables, REST Connectors, and Tasklist human user tasks.

| Variable Name | Type | Scope | Originating Activity | Description & Business Purpose | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `applicantId` | String | Global | `StartEvent_LoanApplied` | Unique synthetic identifier for the loan applicant. Used across audit logs and external credit bureau calls. | `"APP-001"` |
| `applicantName` | String | Global | `StartEvent_LoanApplied` | Full legal name of the synthetic applicant. Displayed in underwriter Tasklist form. | `"Alexander Wright"` |
| `requestedAmount` | Double / Number | Global | `StartEvent_LoanApplied` | Total principal amount requested by the applicant in USD. | `15000.0` |
| `monthlyIncome` | Double / Number | Global | `StartEvent_LoanApplied` | Verified monthly gross income in USD. Must be strictly positive (> 0). | `7500.0` |
| `employmentYears` | Integer | Global | `StartEvent_LoanApplied` | Continuous years of verifiable employment history. | `6` |
| `email` | String | Global | `StartEvent_LoanApplied` | Synthetic email address for applicant notifications. | `"alex.wright@corporate.example.com"` |
| `simulateWorkerFailure` | Boolean | Global | `StartEvent_LoanApplied` | Test instrumentation flag used to intentionally trigger worker incidents for Operate diagnosis. | `false` |
| `isValid` | Boolean | Process | `Task_ValidateApplicant` | Output of the Java worker indicating whether the application schema and parameters are valid. | `true` |
| `debtToIncomeRatio` | Double / Number | Process | `Task_ValidateApplicant` | Estimated monthly debt service repayment as a percentage of monthly income (`(EMI / Income) * 100`). | `6.0` |
| `validationMessage` | String | Process | `Task_ValidateApplicant` | Diagnostic text describing validation checks and outcome. | `"Applicant profile structurally valid. DTI computed: 6.0%"` |
| `creditScore` | Integer | Process | `Task_CreditAssessment` | Bureau credit rating (FICO / Vantage score, 300 to 850) retrieved via REST Connector. | `785` |
| `creditTier` | String | Process | `Task_CreditAssessment` | Risk classification band returned by credit bureau API (`EXCELLENT`, `PRIME`, `MODERATE`, `SUBPRIME`). | `"EXCELLENT"` |
| `assessmentStatus` | String | Process | `Task_CreditAssessment` | HTTP REST Connector status indicating whether the credit assessment was verified. | `"COMPLETED"` |
| `dmnDecisionResult` | Object / Map | Activity | `Task_EvaluateLoanDmn` | Raw output payload emitted by Camunda 8 DMN Decision Table `Decision_LoanEligibility`. | `{"decision": "Approved", "reason": "Prime applicant..."}` |
| `dmnDecision` | String | Process | `Task_EvaluateLoanDmn` | Extracted classification outcome used by Exclusive Gateway: `"Approved"`, `"Rejected"`, or `"Manual Review"`. | `"Approved"` |
| `decisionReason` | String | Process | `Task_EvaluateLoanDmn` | Documented regulatory or educational rule rationale explaining the DMN classification. | `"Prime applicant: High credit score and healthy debt-to-income ratio"` |
| `reviewDecision` | String | Process | `Task_ManualUnderwriterReview` | Human verdict entered by the loan underwriter in Tasklist (`"Approved"` or `"Rejected"`). | `"Approved"` |
| `reviewNotes` | String | Process | `Task_ManualUnderwriterReview` | Qualitative underwriter comments justifying manual approval or rejection. | `"Applicant has stable tenure and high liquid assets; approved."` |
| `disbursementReference` | String | Process | `Task_PrepareDisbursement` | Unique transaction ID generated upon successful loan sanction and disbursement execution. | `"SANCTION-E3A9F112"` |
| `disbursementStatus` | String | Process | `Task_PrepareDisbursement` | Final financial state of the loan contract (`"DISBURSED"`). | `"DISBURSED"` |
| `notificationDispatched` | Boolean | Process | `Task_NotifyApproved` / `Rejected` | Flag confirming external customer communication was delivered. | `true` |
