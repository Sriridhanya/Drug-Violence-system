package com.example.backend.dto;
import lombok.Data;

@Data
public class ImageRequest {
  private String imageDataUrl; // "data:image/jpeg;base64,...."
}