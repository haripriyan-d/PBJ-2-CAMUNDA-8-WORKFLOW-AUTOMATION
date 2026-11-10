package com.camunda.pbj2.lab1;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * Lab 1: Mock Credit Assessment REST API
 * Provides credit evaluation scoring and simulates timeout / service error modes for incident testing.
 */
@RestController
@RequestMapping("/api/v1/credit-assessment")
public class MockCreditApiController {

    private static final Logger log = LoggerFactory.getLogger(MockCreditApiController.class);

    @PostMapping
    public ResponseEntity<Map<String, Object>> assessCredit(@RequestBody Map<String, Object> request) throws InterruptedException {
        String applicantId = (String) request.getOrDefault("applicantId", "APP-TEST");
        Number requestedAmountNum = (Number) request.getOrDefault("requestedAmount", 10000);
        Number monthlyIncomeNum = (Number) request.getOrDefault("monthlyIncome", 5000);

        double requestedAmount = requestedAmountNum.doubleValue();
        double monthlyIncome = monthlyIncomeNum.doubleValue();

        log.info("[Mock Credit API] Received credit pull request for applicantId: {}, Amount: ${}, Income: ${}",
                applicantId, requestedAmount, monthlyIncome);

        // Simulation Scenario 4: Credit assessment API error / 503 outage
        if ("SIMULATE_ERROR".equalsIgnoreCase(applicantId) || requestedAmount > 1000000) {
            log.warn("[Mock Credit API] Simulating Credit Bureau 503 Service Unavailable for {}", applicantId);
            Map<String, Object> err = new HashMap<>();
            err.put("error", "SERVICE_UNAVAILABLE");
            err.put("message", "Credit Bureau Gateway is temporarily unreachable (Simulated Outage).");
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(err);
        }

        // Simulation Scenario: Timeout simulation (delayed response)
        if ("SIMULATE_TIMEOUT".equalsIgnoreCase(applicantId)) {
            log.warn("[Mock Credit API] Simulating 6-second API Timeout for {}", applicantId);
            Thread.sleep(6000);
        }

        // Deterministic synthetic scoring based on synthetic applicant profiles
        int creditScore;
        String creditTier;

        if ("APP-001".equalsIgnoreCase(applicantId) || (monthlyIncome >= 6000 && requestedAmount <= 25000)) {
            creditScore = 785;
            creditTier = "EXCELLENT";
        } else if ("APP-002".equalsIgnoreCase(applicantId) || monthlyIncome < 2200 || requestedAmount >= 45000) {
            creditScore = 540;
            creditTier = "SUBPRIME";
        } else if ("APP-003".equalsIgnoreCase(applicantId) || (monthlyIncome >= 3500 && monthlyIncome < 6000)) {
            creditScore = 675;
            creditTier = "MODERATE";
        } else {
            // General synthetic score computation
            double ratio = requestedAmount / (monthlyIncome * 12.0);
            if (ratio < 0.25) {
                creditScore = 760;
                creditTier = "PRIME";
            } else if (ratio < 0.50) {
                creditScore = 660;
                creditTier = "FAIR";
            } else {
                creditScore = 570;
                creditTier = "POOR";
            }
        }

        Map<String, Object> response = new HashMap<>();
        response.put("applicantId", applicantId);
        response.put("creditScore", creditScore);
        response.put("creditTier", creditTier);
        response.put("assessmentStatus", "COMPLETED");
        response.put("bureauReference", "BUR-EQX-" + System.currentTimeMillis() % 1000000);
        response.put("timestamp", java.time.Instant.now().toString());

        log.info("[Mock Credit API] Assessment completed for {}: Score={}, Tier={}", applicantId, creditScore, creditTier);
        return ResponseEntity.ok(response);
    }
}
