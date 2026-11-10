package com.camunda.pbj2.lab2;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Lab 2: Mock Payment Gateway REST API
 * Simulates card authorizations, token verification, payment decline, and gateway timeout incidents.
 */
@RestController
@RequestMapping("/api/v1/payments")
public class MockPaymentGatewayController {

    private static final Logger log = LoggerFactory.getLogger(MockPaymentGatewayController.class);

    @PostMapping("/process")
    public ResponseEntity<Map<String, Object>> processPayment(@RequestBody Map<String, Object> request) {
        String orderId = (String) request.getOrDefault("orderId", "ORD-TEST");
        String customerRef = (String) request.getOrDefault("customerRef", "CUST-DEFAULT");
        String paymentToken = (String) request.getOrDefault("paymentToken", "tok_visa_valid");
        Number amountNum = (Number) request.getOrDefault("amount", 100.0);
        double amount = amountNum.doubleValue();

        log.info("[Mock Payment Gateway] Processing charge for Order: {}, Customer: {}, Amount: ${}, Token: {}",
                orderId, customerRef, amount, paymentToken);

        // Incident Simulation: Simulated 504 Gateway Timeout / Payment Service Outage
        if ("tok_gateway_timeout_simulate".equalsIgnoreCase(paymentToken) || "FAIL_PAYMENT_SERVICE".equalsIgnoreCase(orderId)) {
            log.error("[Mock Payment Gateway] Simulating HTTP 504 Gateway Timeout for token {}", paymentToken);
            Map<String, Object> err = new HashMap<>();
            err.put("error", "GATEWAY_TIMEOUT");
            err.put("message", "Payment Gateway upstream acquirer timed out. Incident recorded in Camunda Operate.");
            return ResponseEntity.status(HttpStatus.GATEWAY_TIMEOUT).body(err);
        }

        Map<String, Object> response = new HashMap<>();
        response.put("orderId", orderId);
        response.put("amount", amount);
        response.put("currency", "USD");
        response.put("timestamp", java.time.Instant.now().toString());

        // Declined Payment Simulation
        if ("tok_declined_nsf".equalsIgnoreCase(paymentToken) || paymentToken.contains("declined")) {
            log.warn("[Mock Payment Gateway] Card declined for order {}: Insufficient Funds", orderId);
            response.put("paymentStatus", "DECLINED");
            response.put("declineReason", "INSUFFICIENT_FUNDS");
            response.put("transactionId", "TXN-DECLINED-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase());
            return ResponseEntity.ok(response);
        }

        // Successful Payment Authorization
        String txnId = "TXN-AUTH-" + UUID.randomUUID().toString().substring(0, 10).toUpperCase();
        String authCode = "AUTH" + (int)(Math.random() * 900000 + 100000);

        response.put("paymentStatus", "SUCCESS");
        response.put("transactionId", txnId);
        response.put("authCode", authCode);
        response.put("cardNetwork", "VISA_SYNTHETIC");

        log.info("[Mock Payment Gateway] Payment authorized successfully for order {}. Txn: {}", orderId, txnId);
        return ResponseEntity.ok(response);
    }
}
