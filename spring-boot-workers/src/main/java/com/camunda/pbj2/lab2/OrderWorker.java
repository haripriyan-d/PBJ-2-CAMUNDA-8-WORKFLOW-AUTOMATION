package com.camunda.pbj2.lab2;

import io.camunda.zeebe.client.api.response.ActivatedJob;
import io.camunda.zeebe.spring.client.annotation.JobWorker;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Lab 2: End-to-End E-Commerce Order Processing and Fulfilment
 * External Job Workers for Order Validation, Inventory Checking, and Dispatch.
 */
@Component
public class OrderWorker {

    private static final Logger log = LoggerFactory.getLogger(OrderWorker.class);

    // Simulated Product Catalog & Real-time Inventory Store
    private static final Map<String, Integer> INVENTORY_STORE = new ConcurrentHashMap<>();
    private static final Map<String, Double> PRICE_CATALOG = new ConcurrentHashMap<>();

    static {
        INVENTORY_STORE.put("LAPTOP-X1", 45);
        INVENTORY_STORE.put("SMARTPHONE-12", 80);
        INVENTORY_STORE.put("HEADSET-PRO", 120);
        INVENTORY_STORE.put("WORKSTATION-ULTRA", 15);
        INVENTORY_STORE.put("GPU-SERVER", 0); // Out of stock to demonstrate inventory exception path
        INVENTORY_STORE.put("FAULTY_ITEM", 10);

        PRICE_CATALOG.put("LAPTOP-X1", 1200.0);
        PRICE_CATALOG.put("SMARTPHONE-12", 850.0);
        PRICE_CATALOG.put("HEADSET-PRO", 180.0);
        PRICE_CATALOG.put("WORKSTATION-ULTRA", 2200.0);
        PRICE_CATALOG.put("GPU-SERVER", 4500.0);
        PRICE_CATALOG.put("FAULTY_ITEM", 100.0);
    }

    /**
     * Job Worker: order-validator-inventory
     * Validates product SKU, verifies live warehouse stock availability, and calculates order total.
     */
    @JobWorker(type = "order-validator-inventory", autoComplete = true)
    public Map<String, Object> handleOrderAndInventory(final ActivatedJob job) {
        log.info("[Lab 2 Worker] Received Job [order-validator-inventory] - Key: {}", job.getKey());
        Map<String, Object> variables = job.getVariablesAsMap();

        String orderId = (String) variables.getOrDefault("orderId", "ORD-UNKNOWN");
        String productId = (String) variables.getOrDefault("productId", "LAPTOP-X1");
        Number quantityNum = (Number) variables.getOrDefault("quantity", 1);
        Boolean simulateFailure = (Boolean) variables.getOrDefault("simulateWorkerFailure", false);

        int quantity = Math.max(1, quantityNum.intValue());

        // Intentional incident simulation for Operate incident diagnostic & retry scenario
        if (Boolean.TRUE.equals(simulateFailure) || "FAULTY_SKU".equalsIgnoreCase(productId)) {
            log.error("[Lab 2 Worker] INCIDENT TRIGGERED: Inventory database connection exception for SKU: {}", productId);
            throw new IllegalStateException("Inventory Service Lock Exception: Database connection deadlock while querying warehouse rack for SKU [" 
                    + productId + "]. Inspect incident in Camunda Operate and retry once resolved.");
        }

        Map<String, Object> result = new HashMap<>();

        if (!PRICE_CATALOG.containsKey(productId)) {
            result.put("stockAvailable", false);
            result.put("availableStock", 0);
            result.put("orderTotal", 0.0);
            result.put("validationStatus", "UNKNOWN_SKU");
            log.warn("[Lab 2 Worker] Unknown SKU {} for order {}", productId, orderId);
            return result;
        }

        int currentStock = INVENTORY_STORE.getOrDefault(productId, 0);
        double unitPrice = PRICE_CATALOG.get(productId);
        double orderTotal = unitPrice * quantity;

        result.put("unitPrice", unitPrice);
        result.put("orderTotal", orderTotal);

        if (currentStock >= quantity) {
            result.put("stockAvailable", true);
            result.put("availableStock", currentStock);
            result.put("validationStatus", "IN_STOCK");
            log.info("[Lab 2 Worker] Order {}: SKU {} in stock (Required: {}, Available: {}). Total: ${}",
                    orderId, productId, quantity, currentStock, orderTotal);
        } else {
            result.put("stockAvailable", false);
            result.put("availableStock", currentStock);
            result.put("validationStatus", "OUT_OF_STOCK");
            log.warn("[Lab 2 Worker] Order {}: Insufficient stock for SKU {} (Required: {}, Available: {})",
                    orderId, productId, quantity, currentStock);
        }

        return result;
    }

    /**
     * Job Worker: fulfilment-dispatcher
     * Generates warehouse packing slip and shipping tracking reference.
     */
    @JobWorker(type = "fulfilment-dispatcher", autoComplete = true)
    public Map<String, Object> handleFulfilment(final ActivatedJob job) {
        log.info("[Lab 2 Worker] Dispatching order fulfilment for job key: {}", job.getKey());
        Map<String, Object> variables = job.getVariablesAsMap();
        String orderId = (String) variables.getOrDefault("orderId", "ORD-UNKNOWN");

        Map<String, Object> result = new HashMap<>();
        result.put("trackingNumber", "TRK-FEDEX-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase());
        result.put("warehouseLocation", "WH-CENTRAL-BAY-4");
        result.put("fulfilmentStatus", "DISPATCHED");
        result.put("dispatchedAt", java.time.Instant.now().toString());

        log.info("[Lab 2 Worker] Order {} dispatched successfully. Tracking: {}", orderId, result.get("trackingNumber"));
        return result;
    }
}
