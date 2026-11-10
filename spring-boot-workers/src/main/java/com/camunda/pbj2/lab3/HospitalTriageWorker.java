package com.camunda.pbj2.lab3;

import io.camunda.zeebe.client.api.response.ActivatedJob;
import io.camunda.zeebe.spring.client.annotation.JobWorker;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Lab 3: End-to-End Hospital Appointment and Patient Triage Management
 * External Job Workers for Patient Registration Validation and Slot Booking.
 */
@Component
public class HospitalTriageWorker {

    private static final Logger log = LoggerFactory.getLogger(HospitalTriageWorker.class);

    /**
     * Job Worker: patient-registration-validator
     * Validates synthetic patient registration fields, sanitizes symptom summaries,
     * and supports incident triggering for Operate demonstration.
     */
    @JobWorker(type = "patient-registration-validator", autoComplete = true)
    public Map<String, Object> handleRegistrationValidation(final ActivatedJob job) {
        log.info("[Lab 3 Worker] Received Job [patient-registration-validator] - Key: {}", job.getKey());
        Map<String, Object> variables = job.getVariablesAsMap();

        String patientId = (String) variables.getOrDefault("patientId", "PAT-UNKNOWN");
        String patientName = (String) variables.getOrDefault("patientName", "");
        String symptomsSummary = (String) variables.getOrDefault("symptomsSummary", "");
        Boolean simulateWorkerFailure = (Boolean) variables.getOrDefault("simulateWorkerFailure", false);

        // Incident induction for Operate incident diagnostic & retry
        if (Boolean.TRUE.equals(simulateWorkerFailure) || "SIMULATE_WORKER_FAULT".equalsIgnoreCase(patientId)) {
            log.error("[Lab 3 Worker] INCIDENT TRIGGERED: Patient Master Index (MPI) connection failure for ID: {}", patientId);
            throw new RuntimeException("Hospital Master Patient Index (MPI) Connection Timeout: Unable to query national health identifier for ["
                    + patientId + "]. Inspect incident in Operate, verify MPI status, and retry job.");
        }

        Map<String, Object> result = new HashMap<>();

        if (patientName == null || patientName.trim().isEmpty() || symptomsSummary == null || symptomsSummary.trim().isEmpty()) {
            result.put("registrationValid", false);
            result.put("validationNotes", "Registration rejected: Patient name and symptoms description are mandatory fields.");
            log.warn("[Lab 3 Worker] Registration {} invalid: missing clinical details", patientId);
            return result;
        }

        result.put("registrationValid", true);
        result.put("validationNotes", "Patient intake valid. Record linked to EHR.");
        result.put("intakeTimestamp", java.time.Instant.now().toString());

        log.info("[Lab 3 Worker] Patient intake validation successful for {}", patientId);
        return result;
    }

    /**
     * Job Worker: appointment-booking-worker
     * Finalizes slot reservation in the hospital EHR scheduling database.
     */
    @JobWorker(type = "appointment-booking-worker", autoComplete = true)
    public Map<String, Object> handleAppointmentBooking(final ActivatedJob job) {
        log.info("[Lab 3 Worker] Finalizing appointment booking for job key: {}", job.getKey());
        Map<String, Object> variables = job.getVariablesAsMap();
        String patientId = (String) variables.getOrDefault("patientId", "PAT-UNKNOWN");

        Map<String, Object> result = new HashMap<>();
        result.put("bookingReference", "APPT-HOSP-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase());
        result.put("bookingStatus", "CONFIRMED");
        result.put("bookingTimestamp", java.time.Instant.now().toString());

        log.info("[Lab 3 Worker] Appointment confirmed for {}. Ref: {}", patientId, result.get("bookingReference"));
        return result;
    }
}
