package com.camunda.pbj2.lab3;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/**
 * Lab 3: Mock Hospital Scheduling REST API
 * Provides slot queries, specialist routing, no-slot waitlist conditions, and 500 error simulations.
 */
@RestController
@RequestMapping("/api/v1/scheduling")
public class MockHospitalSchedulingController {

    private static final Logger log = LoggerFactory.getLogger(MockHospitalSchedulingController.class);

    @PostMapping("/available-slots")
    public ResponseEntity<Map<String, Object>> getAvailableSlots(@RequestBody Map<String, Object> request) {
        String patientId = (String) request.getOrDefault("patientId", "PAT-TEST");
        String appointmentPreference = (String) request.getOrDefault("appointmentPreference", "General Practice");
        String triageCategory = (String) request.getOrDefault("triageCategory", "Routine");

        log.info("[Mock Scheduling API] Slot query - Patient: {}, Preference: {}, Triage: {}",
                patientId, appointmentPreference, triageCategory);

        // Incident Simulation: Simulated 500 / 503 Internal Server Error
        if ("SIMULATE_500".equalsIgnoreCase(appointmentPreference) || "FAIL_SCHEDULING".equalsIgnoreCase(patientId)) {
            log.error("[Mock Scheduling API] Simulating HTTP 500 Internal Server Error for scheduling database query");
            Map<String, Object> err = new HashMap<>();
            err.put("error", "INTERNAL_SERVER_ERROR");
            err.put("message", "Hospital Scheduling Database deadlocked. Zeebe incident triggered for Operate diagnosis.");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(err);
        }

        Map<String, Object> response = new HashMap<>();
        response.put("patientId", patientId);
        response.put("triageCategory", triageCategory);
        response.put("appointmentPreference", appointmentPreference);
        response.put("queryTimestamp", java.time.Instant.now().toString());

        // Scenario 4: No Appointment Slots Available (Waitlist Path)
        if ("Radiology MRI".equalsIgnoreCase(appointmentPreference) || "NO_SLOTS".equalsIgnoreCase(patientId)) {
            log.warn("[Mock Scheduling API] Zero available slots for preference: {}. Routing to staff waitlist.", appointmentPreference);
            response.put("slotsAvailable", false);
            response.put("slotCount", 0);
            response.put("availableSlots", Collections.emptyList());
            response.put("recommendedDoctor", "None (Department at 100% capacity)");
            response.put("statusMessage", "All clinical slots allocated. Manual staff override required.");
            return ResponseEntity.ok(response);
        }

        // Available Slots Available Scenario
        List<String> slots = Arrays.asList(
                "Tomorrow at 09:30 AM (Consultation Room 3B)",
                "Tomorrow at 02:00 PM (Consultation Room 1A)",
                "Day After Tomorrow at 11:15 AM (Consultation Room 2C)"
        );

        String doctor = "General Practice".equalsIgnoreCase(appointmentPreference) ?
                "Dr. Emily Watson (Lead General Physician)" :
                "Dr. Marcus Vance (Chief of Internal Medicine)";

        response.put("slotsAvailable", true);
        response.put("slotCount", slots.size());
        response.put("availableSlots", slots);
        response.put("recommendedDoctor", doctor);
        response.put("statusMessage", "Slots successfully retrieved from Hospital EHR.");

        log.info("[Mock Scheduling API] Returned {} available slots for patient {}", slots.size(), patientId);
        return ResponseEntity.ok(response);
    }
}
