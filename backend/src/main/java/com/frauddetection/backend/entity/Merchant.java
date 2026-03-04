package com.frauddetection.backend.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Entity
@Table(name = "merchants")
@Data
public class Merchant {

    @Id
    @Column(name = "merchant_id")
    private String merchantId;

    @Column(name = "merchant_category")
    private String merchantCategory;

    @Column(name = "merchant_avg_fraud_rate")
    private Double merchantAvgFraudRate;

    @Column(name = "created_at")
    private LocalDateTime createdAt;
}