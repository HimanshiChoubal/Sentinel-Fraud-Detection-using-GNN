package com.frauddetection.backend.entity;

import jakarta.persistence.*;
import lombok.Data;

@Entity
@Table(name = "devices")
@Data
public class Device {

    @Id
    @Column(name = "device_id")
    private String deviceId;

    @Column(name = "browser")
    private String browser;

    @Column(name = "os")
    private String os;
}