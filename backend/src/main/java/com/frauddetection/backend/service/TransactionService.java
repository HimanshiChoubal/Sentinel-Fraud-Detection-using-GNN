package com.frauddetection.backend.service;

import com.frauddetection.backend.client.FraudDetectionClient;
import com.frauddetection.backend.dto.FraudPredictionRequest;
import com.frauddetection.backend.dto.FraudPredictionResponse;
import com.frauddetection.backend.entity.Transaction;
import com.frauddetection.backend.repository.TransactionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class TransactionService {

    private final TransactionRepository transactionRepository;
    private final FraudDetectionClient fraudDetectionClient;

    public List<Transaction> getAllTransactions() {
        return transactionRepository.findAll();
    }

    public Optional<Transaction> getTransactionById(String id) {
        return transactionRepository.findById(id);
    }

    public List<Transaction> getFraudulentTransactions() {
        return transactionRepository.findByIsFraud(true);
    }

    public List<Transaction> getTransactionsByUser(String userId) {
        return transactionRepository.findByUserId(userId);
    }

    public Transaction saveTransaction(Transaction transaction) {
        return transactionRepository.save(transaction);
    }

    public FraudPredictionResponse checkFraud(String transactionId) {
        Optional<Transaction> txOpt = transactionRepository.findById(transactionId);

        if (txOpt.isEmpty()) {
            FraudPredictionResponse notFound = new FraudPredictionResponse();
            notFound.setTransactionId(transactionId);
            notFound.setLabel("NOT_FOUND");
            notFound.setFraudProbability(0.0);
            notFound.setPrediction(0);
            return notFound;
        }

        Transaction tx = txOpt.get();

        double amount       = tx.getAmount() != null ? tx.getAmount() : 0.0;
        int userEnc         = Math.abs(tx.getUserId() != null ? tx.getUserId().hashCode() % 1000 : 0);
        int merchantEnc     = Math.abs(tx.getMerchantId() != null ? tx.getMerchantId().hashCode() % 500 : 0);
        int deviceEnc       = Math.abs(tx.getDeviceId() != null ? tx.getDeviceId().hashCode() % 300 : 0);
        double userTxCount  = tx.getTxnFreq24h() != null ? tx.getTxnFreq24h() : 1.0;
        double distFromHome = tx.getDistanceFromHomeKm() != null ? tx.getDistanceFromHomeKm() : 0.0;

        double riskScore = 0.0;
        if (Boolean.TRUE.equals(tx.getIsHighRiskCountry())) riskScore += 0.4;
        if (Boolean.TRUE.equals(tx.getIsNewDevice()))        riskScore += 0.3;
        if (Boolean.TRUE.equals(tx.getIsForeignTxn()))       riskScore += 0.2;
        if (tx.getHourOfDay() != null &&
                (tx.getHourOfDay() < 6 || tx.getHourOfDay() > 22)) riskScore += 0.1;

        FraudPredictionRequest req = new FraudPredictionRequest(
                tx.getTransactionId(),
                amount,
                userEnc,
                merchantEnc,
                deviceEnc,
                userTxCount,
                amount,        // user_avg_amount
                distFromHome,  // merch_tx_count
                riskScore      // merch_fraud_rate proxy
        );

        return fraudDetectionClient.predict(req);
    }
}