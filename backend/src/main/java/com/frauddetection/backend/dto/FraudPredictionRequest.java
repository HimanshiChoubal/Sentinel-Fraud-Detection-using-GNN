package com.frauddetection.backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class FraudPredictionRequest {

    @JsonProperty("transaction_id")
    private String transactionId;

    @JsonProperty("amount")
    private double amount;

    @JsonProperty("user_enc")
    private int userEnc;

    @JsonProperty("merchant_enc")
    private int merchantEnc;

    @JsonProperty("device_enc")
    private int deviceEnc;

    @JsonProperty("user_tx_count")
    private double userTxCount = 1.0;

    @JsonProperty("user_avg_amount")
    private double userAvgAmount = 0.0;

    @JsonProperty("merch_tx_count")
    private double merchTxCount = 1.0;

    @JsonProperty("merch_fraud_rate")
    private double merchFraudRate = 0.0;

    // Constructor
    public FraudPredictionRequest(String transactionId, double amount,
                                  int userEnc, int merchantEnc, int deviceEnc,
                                  double userTxCount, double userAvgAmount,
                                  double merchTxCount, double merchFraudRate) {
        this.transactionId = transactionId;
        this.amount = amount;
        this.userEnc = userEnc;
        this.merchantEnc = merchantEnc;
        this.deviceEnc = deviceEnc;
        this.userTxCount = userTxCount;
        this.userAvgAmount = userAvgAmount;
        this.merchTxCount = merchTxCount;
        this.merchFraudRate = merchFraudRate;
    }

    // Getters
    public String getTransactionId() { return transactionId; }
    public double getAmount() { return amount; }
    public int getUserEnc() { return userEnc; }
    public int getMerchantEnc() { return merchantEnc; }
    public int getDeviceEnc() { return deviceEnc; }
    public double getUserTxCount() { return userTxCount; }
    public double getUserAvgAmount() { return userAvgAmount; }
    public double getMerchTxCount() { return merchTxCount; }
    public double getMerchFraudRate() { return merchFraudRate; }
}