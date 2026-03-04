package com.frauddetection.backend.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Entity
@Table(name = "transactions")
@Data
public class Transaction {

    @Id
    @Column(name = "transaction_id")
    private String transactionId;

    @Column(name = "user_id")
    private String userId;

    @Column(name = "merchant_id")
    private String merchantId;

    @Column(name = "device_id")
    private String deviceId;

    @Column(name = "ip_address")
    private String ipAddress;

    @Column(name = "timestamp")
    private LocalDateTime timestamp;

    @Column(name = "amount")
    private Double amount;

    @Column(name = "currency")
    private String currency;

    @Column(name = "card_type")
    private String cardType;

    @Column(name = "hour_of_day")
    private Integer hourOfDay;

    @Column(name = "day_of_week")
    private Integer dayOfWeek;

    @Column(name = "txn_freq_24h")
    private Integer txnFreq24h;

    @Column(name = "is_foreign_txn")
    private Boolean isForeignTxn;

    @Column(name = "is_new_device")
    private Boolean isNewDevice;

    @Column(name = "is_high_risk_country")
    private Boolean isHighRiskCountry;

    @Column(name = "distance_from_home_km")
    private Double distanceFromHomeKm;

    @Column(name = "is_fraud")
    private Boolean isFraud;
}