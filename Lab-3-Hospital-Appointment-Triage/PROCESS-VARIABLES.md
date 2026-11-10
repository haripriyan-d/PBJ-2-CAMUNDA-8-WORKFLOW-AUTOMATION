# Process Variable Dictionary - Lab 3: Hospital Appointment and Patient Triage Management

This dictionary documents all synthetic clinical variables exchanged across registration intake, predefined educational DMN triage tables, scheduling REST Connectors, and clinical Tasklist human tasks.

| Variable Name | Type | Scope | Originating Activity | Description & Business Purpose | Sample Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `patientId` | String | Global | `StartEvent_AppointmentRequested` | Synthetic unique patient master index identifier (EHR ID). | `"PAT-SYNTH-101"` |
| `patientName` | String | Global | `StartEvent_AppointmentRequested` | Synthetic full name of the patient. | `"Alex Morgan"` |
| `appointmentPreference` | String | Global | `StartEvent_AppointmentRequested` | Desired medical department or specialty (`"General Practice"`, `"Specialist"`, `"Radiology MRI"`, `"Emergency"`). | `"General Practice"` |
| `symptomsSummary` | String | Global | `StartEvent_AppointmentRequested` | Chief complaint narrative used for clinical intake and triage classification. | `"Annual routine physical and preventive blood panel review"` |
| `urgencyScore` | Integer | Global | `StartEvent_AppointmentRequested` | Predefined clinical acuity score on a 1-to-10 scale (1 = minimal, 10 = life threatening). | `2` |
| `symptomsSeverity` | String | Global | `StartEvent_AppointmentRequested` | Clinical severity indicator (`"CRITICAL"`, `"MODERATE"`, `"MILD"`). | `"MILD"` |
| `registrationValid` | Boolean | Process | `Task_ValidatePatientRegistration` | Worker validation boolean confirming presence of synthetic identity and symptoms data. | `true` |
| `validationNotes` | String | Process | `Task_ValidatePatientRegistration` | Audit log note from registration validator worker. | `"Patient intake valid. Record linked to EHR."` |
| `triageOutcome` | Object / Map | Activity | `Task_EvaluatePatientTriageDmn` | Raw decision output from Camunda DMN Table `Decision_PatientTriage`. | `{"triageCategory": "Routine", ...}` |
| `triageCategory` | String | Process | `Task_EvaluatePatientTriageDmn` | Derived triage band (`"Urgent Assessment"`, `"Priority Review"`, `"Routine"`). Controls gateway routing. | `"Routine"` |
| `targetResponseMinutes` | Integer | Process | `Task_EvaluatePatientTriageDmn` | Clinical SLA response window (`15` min for Urgent, `240` min for Priority, `2880` min for Routine). | `2880` |
| `clinicalProtocol` | String | Process | `Task_EvaluatePatientTriageDmn` | Educational medical guideline protocol code associated with triage band. | `"Code Green: Routine outpatient consultation queue within 48 hours"` |
| `slotsAvailable` | Boolean | Process | `Task_QueryAvailableSlotsRest` | Response boolean from scheduling REST API indicating if slots exist. | `true` |
| `slotCount` | Integer | Process | `Task_QueryAvailableSlotsRest` | Total number of eligible slots returned by the scheduling engine. | `3` |
| `availableSlots` | Array/List | Process | `Task_QueryAvailableSlotsRest` | List of formatted date/time strings available for booking. | `["Tomorrow at 09:30 AM", ...]` |
| `recommendedDoctor` | String | Process | `Task_QueryAvailableSlotsRest` | Assigned attending physician name and department. | `"Dr. Emily Watson (Lead General Physician)"` |
| `bookingReference` | String | Process | `Task_AutoBookAppointment` | Unique appointment booking confirmation code. | `"APPT-HOSP-C2E81A05"` |
| `bookingStatus` | String | Process | `Task_AutoBookAppointment` | Terminal scheduling state (`"CONFIRMED"` or `"WAITLISTED"`). | `"CONFIRMED"` |
| `staffDecision` | String | Process | `Task_PriorityStaffReview` / `Override` | Action recorded by triage nurse/staff in Tasklist (`"Approved"`, `"Slot Assigned"`, `"Waitlisted"`). | `"Slot Assigned"` |
