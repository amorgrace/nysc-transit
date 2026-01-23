# Pull Request Title
Enhance Authentication System: OTP, Password Management, and User Endpoints

## Description
This PR implements a comprehensive overhaul of the authentication system, including OTP verification, password management, and user-related endpoints. All endpoints now have proper validation, error handling, and test coverage. Key improvements include:

### 1. OTP Management
- **POST `/api/auth/verify-otp`**
  - Verifies OTP for a given email
  - Activates the user if OTP is valid
  - Returns appropriate errors:
    - 404 if user not found
    - 400 if OTP is invalid
- **POST `/api/auth/resend-otp`**
  - Allows users to request a new OTP
  - Ensures OTP is regenerated and sent correctly
  - Handles rate limiting and error responses gracefully
- Unit tests added:
  - Success, failure, and edge cases for both endpoints

### 2. Password Management
- **POST `/api/auth/forgot-password`**
  - Initiates password reset flow
  - Sends password reset email/link
- **POST `/api/auth/reset-password`**
  - Resets user password
  - Enforces strong password rules:
    - Must start with a capital letter
    - Must contain at least one special character
- Unit tests added:
  - Password validation success/failure
  - Forgot-password email sending
  - Reset-password endpoint behavior

### 3. User Endpoint
- **GET `/api/auth/user/me`**
  - Returns details of the currently authenticated user
  - Handles unauthenticated requests appropriately
- Unit tests added:
  - Authenticated user retrieval
  - Unauthorized access

### 4. Test Coverage
- All endpoints are covered by **pytest tests**:
  - OTP endpoints (`verify-otp`, `resend-otp`) with mocks to isolate OTP logic
  - Password endpoints (`forgot-password`, `reset-password`) including validation
  - Current user retrieval (`user/me`)
- Tests ensure deterministic behavior and proper error handling

### 5. Additional Improvements
- Regex-based password validation: `^[A-Z].*[^A-Za-z0-9]`
- Refined error messages for better UX
- Ensured all tests pass on CI/CD
- Code formatted and linted according to project standards

### Related Issues
- Closes #<insert-related-issue-number> (if applicable)

## Checklist
- [x] Code is formatted & linted
- [x] All endpoints implemented and tested
- [x] OTP logic is covered with mocks in tests
- [x] Password validation enforced and tested
- [x] All unit tests pass
- [x] Documentation updated for all endpoints
- [x] Peer-reviewed

## Type of Change
- [x] Bug fix
- [x] New feature
- [x] Refactor
- [x] Test update
- [x] Documentation update

## How Has This Been Tested?
- Unit tests using `pytest` for all endpoints
- Manual testing with Django/Ninja test client:
  - OTP verification/resend
  - Password reset/forgot-password
  - Current user retrieval
- Test users with **password-compliant credentials** (start with capital + special char)
- OTP verification logic mocked to ensure deterministic tests

## Notes / Additional Info
- Reviewer attention points:
  - OTP edge cases and resending behavior
  - Password validation enforcement and regex correctness
  - Test coverage completeness for all auth flows
- Branch protection rules enforced:
  - Require review before merge
  - Require passing tests
