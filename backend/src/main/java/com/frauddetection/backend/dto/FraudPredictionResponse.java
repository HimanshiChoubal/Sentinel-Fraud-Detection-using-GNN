package com.frauddetection.backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class FraudPredictionResponse {

    @JsonProperty("transaction_id")
    private String transactionId;

    @JsonProperty("fraud_probability")
    private double fraudProbability;

    @JsonProperty("prediction")
    private int prediction;

    @JsonProperty("label")
    private String label;

    @JsonProperty("threshold_used")
    private double thresholdUsed;

    // Getters and Setters
    public String getTransactionId() { return transactionId; }
    public void setTransactionId(String transactionId) { this.transactionId = transactionId; }

    public double getFraudProbability() { return fraudProbability; }
    public void setFraudProbability(double fraudProbability) { this.fraudProbability = fraudProbability; }

    public int getPrediction() { return prediction; }
    public void setPrediction(int prediction) { this.prediction = prediction; }

    public String getLabel() { return label; }
    public void setLabel(String label) { this.label = label; }

    public double getThresholdUsed() { return thresholdUsed; }
    public void setThresholdUsed(double thresholdUsed) { this.thresholdUsed = thresholdUsed; }
}