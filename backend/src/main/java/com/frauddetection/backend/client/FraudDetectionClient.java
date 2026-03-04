package com.frauddetection.backend.client;

import com.frauddetection.backend.dto.FraudPredictionRequest;
import com.frauddetection.backend.dto.FraudPredictionResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Component
public class FraudDetectionClient {

    private static final Logger log = LoggerFactory.getLogger(FraudDetectionClient.class);
    private static final String FASTAPI_URL = "http://localhost:8000/predict";

    private final RestTemplate restTemplate = new RestTemplate();

    public FraudPredictionResponse predict(FraudPredictionRequest request) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<FraudPredictionRequest> entity = new HttpEntity<>(request, headers);

            ResponseEntity<FraudPredictionResponse> response = restTemplate.exchange(
                    FASTAPI_URL,
                    HttpMethod.POST,
                    entity,
                    FraudPredictionResponse.class
            );

            log.info("Fraud prediction for {}: {} (prob: {})",
                    request.getTransactionId(),
                    response.getBody().getLabel(),
                    response.getBody().getFraudProbability()
            );

            return response.getBody();

        } catch (Exception e) {
            log.error("FastAPI call failed for {}: {}", request.getTransactionId(), e.getMessage());
            // Return safe default — don't block transaction if ML service is down
            FraudPredictionResponse fallback = new FraudPredictionResponse();
            fallback.setTransactionId(request.getTransactionId());
            fallback.setFraudProbability(0.0);
            fallback.setPrediction(0);
            fallback.setLabel("UNKNOWN");
            return fallback;
        }
    }
}