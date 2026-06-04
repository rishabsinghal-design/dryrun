/**
 * Shared TypeScript types — HLD §3 Data Model
 * Used by all backend services and frontend apps.
 */

// ─── Enums ────────────────────────────────────────────────────────────────────

export type AdminRole = 'reviewer' | 'supervisor' | 'system_admin';

export type ApplicationStatus =
  | 'draft'
  | 'submitted'
  | 'under_review'
  | 'info_required'
  | 'approved'
  | 'rejected';

export type DocumentScanStatus = 'pending' | 'clean' | 'infected';

export type NotificationChannel = 'email' | 'sms';

export type NotificationStatus = 'queued' | 'sent' | 'failed';

export type AuditActorType = 'citizen' | 'admin' | 'system';

export type AuditAction = 'create' | 'read_pii' | 'update' | 'delete';

// ─── Core Entities ────────────────────────────────────────────────────────────

export interface Citizen {
  id: string; // UUID
  full_name: string; // encrypted at rest
  date_of_birth: string; // encrypted at rest (ISO date)
  email: string; // encrypted at rest
  phone_number?: string; // encrypted at rest
  id_number_hash: string; // SHA-256 of government ID
  verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface AdminUser {
  id: string;
  saml_name_id: string;
  email: string;
  role: AdminRole;
  department_id: string;
  created_at: string;
  last_login_at?: string;
}

export interface Department {
  id: string;
  name: string;
  case_mgmt_api_base_url: string;
  case_mgmt_api_key_ref: string; // reference to secrets manager key
}

export interface Service {
  id: string;
  name: string;
  description: string;
  eligibility_criteria: string;
  required_documents: string[]; // JSONB array
  estimated_processing_days: number;
  form_schema: Record<string, unknown>; // JSON Schema definition
  department_id: string;
  published: boolean;
  created_at: string;
  updated_at: string;
}

export interface Application {
  id: string;
  reference_number: string; // SVC-YYYYMMDD-XXXXXX
  citizen_id: string;
  service_id: string;
  status: ApplicationStatus;
  form_data: Record<string, unknown>; // JSONB, encrypted at column level
  draft_expires_at?: string;
  submitted_at?: string;
  last_status_changed_at: string;
  last_status_reason?: string;
  assigned_department_id: string;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  application_id: string;
  original_filename: string;
  storage_key: string; // encrypted object store path
  mime_type: string;
  size_bytes: number;
  scan_status: DocumentScanStatus;
  uploaded_at: string;
}

export interface StatusHistory {
  id: string;
  application_id: string;
  from_status: ApplicationStatus;
  to_status: ApplicationStatus;
  changed_by_admin_id?: string;
  reason: string;
  changed_at: string;
}

export interface Notification {
  id: string;
  application_id: string;
  channel: NotificationChannel;
  status: NotificationStatus;
  sent_at?: string;
  retry_count: number;
}

export interface CsatResponse {
  id: string;
  application_id: string;
  responses: Record<string, number>; // 5 question scores
  submitted_at: string;
}

export interface AuditLog {
  id: string;
  timestamp: string;
  actor_id: string;
  actor_type: AuditActorType;
  action: AuditAction;
  entity_type: string;
  entity_id: string;
  metadata: Record<string, unknown>;
}

// ─── API Payloads ─────────────────────────────────────────────────────────────

export interface ApiError {
  error: {
    code: string;
    message: string;
    traceId: string;
  };
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export interface RegisterRequest {
  full_name: string;
  date_of_birth: string;
  email: string;
  phone_number?: string;
  id_number: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface OtpVerifyRequest {
  pre_mfa_token: string;
  otp: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  expires_in: number;
}
