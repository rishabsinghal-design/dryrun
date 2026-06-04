/**
 * Message queue event contracts — HLD §2 (async flows)
 * Published by Application Module; consumed by Notification, Audit, DeptAdapter.
 */

import type { ApplicationStatus, NotificationChannel } from './types';

export type QueueEventType =
  | 'OTP_REQUESTED'
  | 'APPLICATION_SUBMITTED'
  | 'STATUS_CHANGED'
  | 'DOCUMENT_SCANNED'
  | 'CSAT_TRIGGERED';

export interface BaseEvent {
  eventId: string; // UUID
  eventType: QueueEventType;
  occurredAt: string; // ISO timestamp
  traceId: string;
}

export interface OtpRequestedEvent extends BaseEvent {
  eventType: 'OTP_REQUESTED';
  citizenId: string;
  channel: NotificationChannel;
  destination: string; // email or phone
  otp: string; // short-lived; consumed once
}

export interface ApplicationSubmittedEvent extends BaseEvent {
  eventType: 'APPLICATION_SUBMITTED';
  applicationId: string;
  referenceNumber: string;
  citizenId: string;
  serviceId: string;
  departmentId: string;
}

export interface StatusChangedEvent extends BaseEvent {
  eventType: 'STATUS_CHANGED';
  applicationId: string;
  referenceNumber: string;
  citizenId: string;
  fromStatus: ApplicationStatus;
  toStatus: ApplicationStatus;
  reason: string;
  changedByAdminId?: string;
  citizenEmail: string; // pre-fetched to avoid PII read in notification svc
  citizenPhone?: string;
}

export interface DocumentScannedEvent extends BaseEvent {
  eventType: 'DOCUMENT_SCANNED';
  documentId: string;
  applicationId: string;
  scanResult: 'clean' | 'infected';
}

export interface CsatTriggeredEvent extends BaseEvent {
  eventType: 'CSAT_TRIGGERED';
  applicationId: string;
  citizenId: string;
  terminalStatus: 'approved' | 'rejected';
}

export type QueueEvent =
  | OtpRequestedEvent
  | ApplicationSubmittedEvent
  | StatusChangedEvent
  | DocumentScannedEvent
  | CsatTriggeredEvent;
