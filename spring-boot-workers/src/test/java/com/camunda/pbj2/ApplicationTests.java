package com.camunda.pbj2;

import com.camunda.pbj2.lab1.MockCreditApiController;
import com.camunda.pbj2.lab2.MockPaymentGatewayController;
import com.camunda.pbj2.lab3.MockHospitalSchedulingController;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
public class ApplicationTests {

    @Autowired
    private MockCreditApiController creditApiController;

    @Autowired
    private MockPaymentGatewayController paymentGatewayController;

    @Autowired
    private MockHospitalSchedulingController schedulingController;

    @Test
    @DisplayName("Context Loads Successfully")
    void contextLoads() {
        assertNotNull(creditApiController);
        assertNotNull(paymentGatewayController);
        assertNotNull(schedulingController);
    }

    @Test
    @DisplayName("Lab 1: Credit Assessment API - Prime Approval Case")
    void testCreditAssessmentApproved() throws InterruptedException {
        Map<String, Object> req = new HashMap<>();
        req.put("applicantId", "APP-001");
        req.put("requestedAmount", 15000);
        req.put("monthlyIncome", 7500);

        ResponseEntity<Map<String, Object>> response = creditApiController.assessCredit(req);
        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals(785, response.getBody().get("creditScore"));
        assertEquals("EXCELLENT", response.getBody().get("creditTier"));
    }

    @Test
    @DisplayName("Lab 1: Credit Assessment API - Service Outage Simulation")
    void testCreditAssessmentServiceOutage() throws InterruptedException {
        Map<String, Object> req = new HashMap<>();
        req.put("applicantId", "SIMULATE_ERROR");
        req.put("requestedAmount", 10000);
        req.put("monthlyIncome", 4000);

        ResponseEntity<Map<String, Object>> response = creditApiController.assessCredit(req);
        assertEquals(HttpStatus.SERVICE_UNAVAILABLE, response.getStatusCode());
    }

    @Test
    @DisplayName("Lab 2: Payment Gateway - Successful Authorization")
    void testPaymentSuccessful() {
        Map<String, Object> req = new HashMap<>();
        req.put("orderId", "ORD-101");
        req.put("customerRef", "CUST-VIP");
        req.put("amount", 2400.0);
        req.put("paymentToken", "tok_visa_valid");

        ResponseEntity<Map<String, Object>> response = paymentGatewayController.processPayment(req);
        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals("SUCCESS", response.getBody().get("paymentStatus"));
        assertNotNull(response.getBody().get("transactionId"));
    }

    @Test
    @DisplayName("Lab 2: Payment Gateway - Decline Simulation")
    void testPaymentDeclined() {
        Map<String, Object> req = new HashMap<>();
        req.put("orderId", "ORD-102");
        req.put("customerRef", "CUST-REGULAR");
        req.put("amount", 180.0);
        req.put("paymentToken", "tok_declined_nsf");

        ResponseEntity<Map<String, Object>> response = paymentGatewayController.processPayment(req);
        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals("DECLINED", response.getBody().get("paymentStatus"));
    }

    @Test
    @DisplayName("Lab 2: Payment Gateway - Gateway Timeout Incident Simulation")
    void testPaymentTimeout() {
        Map<String, Object> req = new HashMap<>();
        req.put("orderId", "ORD-103");
        req.put("customerRef", "CUST-NEW");
        req.put("amount", 500.0);
        req.put("paymentToken", "tok_gateway_timeout_simulate");

        ResponseEntity<Map<String, Object>> response = paymentGatewayController.processPayment(req);
        assertEquals(HttpStatus.GATEWAY_TIMEOUT, response.getStatusCode());
    }

    @Test
    @DisplayName("Lab 3: Hospital Scheduling API - Available Slots Found")
    void testSchedulingAvailableSlots() {
        Map<String, Object> req = new HashMap<>();
        req.put("patientId", "PAT-101");
        req.put("appointmentPreference", "General Practice");
        req.put("triageCategory", "Routine");

        ResponseEntity<Map<String, Object>> response = schedulingController.getAvailableSlots(req);
        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals(true, response.getBody().get("slotsAvailable"));
        assertTrue((int) response.getBody().get("slotCount") > 0);
    }

    @Test
    @DisplayName("Lab 3: Hospital Scheduling API - Zero Slots Available (Waitlist Path)")
    void testSchedulingZeroSlots() {
        Map<String, Object> req = new HashMap<>();
        req.put("patientId", "PAT-104");
        req.put("appointmentPreference", "Radiology MRI");
        req.put("triageCategory", "Routine");

        ResponseEntity<Map<String, Object>> response = schedulingController.getAvailableSlots(req);
        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals(false, response.getBody().get("slotsAvailable"));
        assertEquals(0, response.getBody().get("slotCount"));
    }

    @Test
    @DisplayName("Lab 3: Hospital Scheduling API - 500 Service Error Simulation")
    void testSchedulingServiceError() {
        Map<String, Object> req = new HashMap<>();
        req.put("patientId", "PAT-105");
        req.put("appointmentPreference", "SIMULATE_500");
        req.put("triageCategory", "Priority Review");

        ResponseEntity<Map<String, Object>> response = schedulingController.getAvailableSlots(req);
        assertEquals(HttpStatus.INTERNAL_SERVER_ERROR, response.getStatusCode());
    }
}
