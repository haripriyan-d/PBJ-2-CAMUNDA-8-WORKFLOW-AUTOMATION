package com.camunda.pbj2.lab1;

import io.camunda.zeebe.client.api.response.ActivatedJob;
import io.camunda.zeebe.spring.client.annotation.JobWorker;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Lab 1: End-to-End Loan Approval Automation
 * External Job Workers for Applicant Validation, Disbursement & Notifications.
 */
@Component
public class LoanWorker {

    private static final Logger log = LoggerFactory.getLogger(LoanWorker.class);

    /**
     * Job Worker: applicant-validator
     * Validates applicant inputs, checks bounds, calculates Debt-To-Income (DTI) ratio,
     * and supports intentional incident induction for Operate monitoring and recovery.
     */
    @JobWorker(type = "applicant-validator", autoComplete = true)
    public Map<String, Object> handleApplicantValidation(final ActivatedJob job) {
        log.info("[Lab 1 Worker] Received Job [applicant-validator] - Key: {}", job.getKey());
        Map<String, Object> variables = job.getVariablesAsMap();

        String applicantId = (String) variables.getOrDefault("applicantId", "APP-UNKNOWN");
        String applicantName = (String) variables.getOrDefault("applicantName", "");
        Number requestedAmountNum = (Number) variables.getOrDefault("requestedAmount", 0);
        Number monthlyIncomeNum = (Number) variables.getOrDefault("monthlyIncome", 0);
        Number employmentYearsNum = (Number) variables.getOrDefault("employmentYears", 0);
        Boolean simulateWorkerFailure = (Boolean) variables.getOrDefault("simulateWorkerFailure", false);

        double requestedAmount = requestedAmountNum.doubleValue();
        double monthlyIncome = monthlyIncomeNum.doubleValue();
        int employmentYears = employmentYearsNum.intValue();

        // Intentional incident simulation for Operate incident diagnostic & retry scenario
        if (Boolean.TRUE.equals(simulateWorkerFailure) || monthlyIncome < 0) {
            log.error("[Lab 1 Worker] INCIDENT TRIGGERED: Invalid negative income or intentional worker exception. Key: {}", job.getKey());
            throw new IllegalArgumentException("Worker Validation Fault: Monthly income cannot be negative ($" + monthlyIncome + "). Inspect and correct variable in Camunda Operate to retry.");
        }

        Map<String, Object> result = new HashMap<>();

        if (applicantName == null || applicantName.trim().isEmpty() || requestedAmount <= 0 || monthlyIncome <= 0) {
            result.put("isValid", false);
            result.put("debtToIncomeRatio", 0.0);
            result.put("validationMessage", "Validation Failed: Name, requested amount (>0), and monthly income (>0) are required.");
            log.warn("[Lab 1 Worker] Application {} rejected at validation stage: Missing/invalid core fields.", applicantId);
            return result;
        }

        // Calculate estimated monthly repayment (36 months term at 8% APR) & DTI ratio
        double estimatedMonthlyEmi = (requestedAmount * 1.08) / 36.0;
        double dtiRatio = Math.round((estimatedMonthlyEmi / monthlyIncome) * 10000.0) / 100.0;

        result.put("isValid", true);
        result.put("debtToIncomeRatio", dtiRatio);
        result.put("estimatedMonthlyEmi", Math.round(estimatedMonthlyEmi * 100.0) / 100.0);
        result.put("validationMessage", "Applicant profile structurally valid. DTI computed: " + dtiRatio + "%");

        log.info("[Lab 1 Worker] Application {} validation successful. Computed DTI: {}%", applicantId, dtiRatio);
        return result;
    }

    /**
     * Job Worker: loan-disbursement
     * Prepares loan agreement documents, creates account, and initiates automated disbursement.
     */
    @JobWorker(type = "loan-disbursement", autoComplete = true)
    public Map<String, Object> handleLoanDisbursement(final ActivatedJob job) {
        log.info("[Lab 1 Worker] Processing loan disbursement for job key: {}", job.getKey());
        Map<String, Object> variables = job.getVariablesAsMap();
        String applicantId = (String) variables.getOrDefault("applicantId", "APP-UNKNOWN");

        Map<String, Object> result = new HashMap<>();
        result.put("disbursementReference", "SANCTION-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase());
        result.put("disbursementStatus", "DISBURSED");
        result.put("disbursedAt", java.time.Instant.now().toString());

        log.info("[Lab 1 Worker] Loan disbursed for applicant {}. Ref: {}", applicantId, result.get("disbursementReference"));
        return result;
    }

    /**
     * Job Worker: notification-service
     * Common notification dispatcher across labs (approval, rejection, or order status).
     */
    @JobWorker(type = "notification-service", autoComplete = true)
    public Map<String, Object> handleNotification(final ActivatedJob job) {
        Map<String, Object> variables = job.getVariablesAsMap();
        String channel = (String) variables.getOrDefault("notificationChannel", "EMAIL_SMS");
        log.info("[Notification Service] Dispatched notification for job key {} via {}", job.getKey(), channel);

        Map<String, Object> result = new HashMap<>();
        result.put("notificationDispatched", true);
        result.put("dispatchedTimestamp", java.time.Instant.now().toString());
        return result;
    }
}
