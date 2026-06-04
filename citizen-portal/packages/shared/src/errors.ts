/**
 * Canonical error codes — HLD §4 Error Model
 * All services MUST use these constants; never raw strings.
 */

export const ErrorCodes = {
  // Auth / Identity (FR-1, FR-2)
  ID_VERIFY_FAILED: 'ID_VERIFY_FAILED',
  REGISTRY_UNAVAILABLE: 'REGISTRY_UNAVAILABLE',
  INVALID_CREDENTIALS: 'INVALID_CREDENTIALS',
  INVALID_OTP: 'INVALID_OTP',
  OTP_EXPIRED: 'OTP_EXPIRED',
  SESSION_EXPIRED: 'SESSION_EXPIRED',
  MFA_REQUIRED: 'MFA_REQUIRED',

  // Authorisation
  FORBIDDEN: 'FORBIDDEN',
  UNAUTHORIZED: 'UNAUTHORIZED',

  // Application (FR-4)
  APPLICATION_NOT_FOUND: 'APPLICATION_NOT_FOUND',
  DRAFT_EXPIRED: 'DRAFT_EXPIRED',
  INVALID_STATUS_TRANSITION: 'INVALID_STATUS_TRANSITION',
  BULK_LIMIT_EXCEEDED: 'BULK_LIMIT_EXCEEDED',

  // Documents (FR-5)
  FILE_INFECTED: 'FILE_INFECTED',
  FILE_TOO_LARGE: 'FILE_TOO_LARGE',
  FILE_TYPE_NOT_ALLOWED: 'FILE_TYPE_NOT_ALLOWED',
  MAX_FILES_EXCEEDED: 'MAX_FILES_EXCEEDED',
  SCAN_PENDING: 'SCAN_PENDING',

  // General
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  IDEMPOTENCY_CONFLICT: 'IDEMPOTENCY_CONFLICT',
} as const;

export type ErrorCode = (typeof ErrorCodes)[keyof typeof ErrorCodes];

export class AppError extends Error {
  constructor(
    public readonly code: ErrorCode,
    public readonly message: string,
    public readonly httpStatus: number,
    public readonly traceId?: string,
  ) {
    super(message);
    this.name = 'AppError';
  }

  toJSON() {
    return {
      error: {
        code: this.code,
        message: this.message,
        traceId: this.traceId ?? 'unknown',
      },
    };
  }
}
