package com.example.backend.controller;

import com.example.backend.dto.ImageRequest;
import com.example.backend.dto.TextRequest;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@RestController
@RequestMapping("/api")
public class DetectionController {

  private final RestTemplate rest = new RestTemplate();
  private final String AI = "http://localhost:8001"; // Python service

  @PostMapping("/detect/{type}")
  public ResponseEntity<?> detect(@PathVariable String type, @RequestBody ImageRequest req) {
    if (!type.equals("weapon") && !type.equals("violence")) {
      return ResponseEntity.badRequest().body(Map.of("error", "Invalid type"));
    }
    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_JSON);
    HttpEntity<ImageRequest> entity = new HttpEntity<>(req, headers);

    ResponseEntity<String> aiResp = rest.postForEntity(AI + "/detect/" + type, entity, String.class);
    return ResponseEntity.status(aiResp.getStatusCode()).body(aiResp.getBody());
  }

  @PostMapping("/text/analyze")
  public ResponseEntity<?> analyzeText(@RequestBody TextRequest req) {
    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_JSON);
    HttpEntity<TextRequest> entity = new HttpEntity<>(req, headers);

    ResponseEntity<String> aiResp = rest.postForEntity(AI + "/text/analyze", entity, String.class);
    return ResponseEntity.status(aiResp.getStatusCode()).body(aiResp.getBody());
  }
}