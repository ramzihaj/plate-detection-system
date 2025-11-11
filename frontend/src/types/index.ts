export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface Detection {
  id: string;
  detected_plate?: string;
  confidence?: number;
  bounding_box?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  detection_time: number;
  status: string;
  image_url: string;
  created_at: string;
}

export interface DetectionHistory {
  detections: Detection[];
  total: number;
  page: number;
  page_size: number;
}

export interface UserStats {
  total_detections: number;
  successful_detections: number;
  failed_detections: number;
  last_detection?: string;
}
