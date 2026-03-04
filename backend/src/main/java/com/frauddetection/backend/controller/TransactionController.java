package com.frauddetection.backend.controller;

import com.frauddetection.backend.dto.FraudPredictionResponse;
import com.frauddetection.backend.entity.Transaction;
import com.frauddetection.backend.service.TransactionService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/transactions")
@RequiredArgsConstructor
public class TransactionController {

    private final TransactionService transactionService;

    // GET all transactions
    @GetMapping
    public List<Transaction> getAllTransactions() {
        return transactionService.getAllTransactions();
    }

    // GET transaction by ID
    @GetMapping("/{id}")
    public ResponseEntity<Transaction> getById(@PathVariable String id) {
        return transactionService.getTransactionById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // GET all fraud transactions
    @GetMapping("/fraud")
    public List<Transaction> getFraudTransactions() {
        return transactionService.getFraudulentTransactions();
    }

    // GET transactions by user
    @GetMapping("/user/{userId}")
    public List<Transaction> getByUser(@PathVariable String userId) {
        return transactionService.getTransactionsByUser(userId);
    }

    // POST create transaction
    @PostMapping
    public Transaction createTransaction(@RequestBody Transaction transaction) {
        return transactionService.saveTransaction(transaction);
    }

    // POST fraud check — calls FastAPI GNN model
    @PostMapping("/{id}/fraud-check")
    public ResponseEntity<FraudPredictionResponse> checkFraud(@PathVariable String id) {
        FraudPredictionResponse response = transactionService.checkFraud(id);
        if ("NOT_FOUND".equals(response.getLabel())) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(response);
    }
}