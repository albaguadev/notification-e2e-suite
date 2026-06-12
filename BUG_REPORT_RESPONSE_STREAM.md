# Bug Report: Response Stream Already Read Error

## Issue
Property-based tests for error response parsing were failing with 2 tests marked as `xfail`:
- `test_error_response_parsing_displays_message_and_description`
- `test_error_response_display`

Users were seeing a generic "An error occurred. Please try again." message instead of the specific error details from the backend.

## Root Cause

The bug was a **double JSON parse on the same Response stream** in the API client:

```typescript
// In sendNotification():
let data: unknown
try {
  data = await response.json()  // ← First read of response body
} catch (error) { ... }

// Later, for error responses:
if (!response.ok) {
  const errorResponse = await handleAPIError(response, response.status)
  // handleAPIError would then try to do:
  // const errorData = await response.json()  // ← ERROR: stream already consumed!
}
```

### Why This Happens

The Fetch API Response object has a **single-use body stream**. Once you call `.json()`, `.text()`, `.blob()`, or any other method that consumes the body, the stream is exhausted. Attempting to read it again throws:

```
TypeError: Failed to execute 'json' on 'Response': body stream already read
```

This error was being caught silently (as per Requirement 3.6), causing the error response to be treated as malformed, and the UI showed the generic fallback message.

### Browser Console Evidence

```
[handleAPIError] Malformed JSON - failing silently TypeError: Failed to execute 'json' on 'Response': body stream already read
    at handleAPIError (http://localhost:5173/src/api/client.ts:66:36)
    at sendNotification (http://localhost:5173/src/api/client.ts:160:31)
    at async handleSubmit (http://localhost:5173/src/components/NotificationForm.tsx:130:21)
```

## Solution

Changed the architecture so the response body is **parsed only once** and the parsed data is passed to error handling:

### Changes Made

**File: `frontend/src/api/client.ts`**

1. **Updated `handleAPIError` signature:**
   ```typescript
   // BEFORE
   async function handleAPIError(
     response: Response,
     httpStatus: number
   ): Promise<ErrorResponse | null>
   
   // AFTER
   async function handleAPIError(
     errorData: unknown,           // ← Now accepts pre-parsed data
     httpStatus: number
   ): Promise<ErrorResponse | null>
   ```

2. **Updated error data validation logic:**
   - Changed from trying to parse JSON to validating the already-parsed object
   - Added type checks for object structure instead of relying on `.json()` parsing
   - Validates the presence of required fields (`status` and `message`)

3. **Updated call sites:**
   ```typescript
   // In sendNotification()
   const errorResponse = await handleAPIError(data, response.status)
   // ↑ Pass the pre-parsed data, not the response object
   
   // In queryNotifications()
   const errorResponse = await handleAPIError(data, response.status)
   // ↑ Same pattern
   ```

### Code Flow After Fix

```typescript
// Single parse point
let data: unknown
try {
  data = await response.json()  // ← Only one read of the stream
} catch (error) { 
  // Malformed JSON
  return { success: false, error: undefined }
}

if (response.ok) {
  // Handle success
  return { success: true, data }
} else {
  // Pass pre-parsed data to validation function
  const errorResponse = await handleAPIError(data, response.status)
  return { success: false, error: errorResponse }
}
```

## Impact

### Before Fix
- ❌ Error response details not displayed (generic message shown)
- ❌ 2 property tests failing (marked as xfail)
- ❌ 26/28 property tests passing (92.9%)

### After Fix
- ✅ Error response details properly parsed and displayed
- ✅ All 2 previously failing tests now pass
- ✅ **28/28 property tests passing (100%)**
- ✅ No regressions in other tests

## Test Results

```
tests/property/test_error_response_parsing.py::TestErrorResponseParsing::test_error_response_parsing_displays_message_and_description[chromium] PASSED
tests/property/test_response_display.py::TestResponseDisplay::test_error_response_display[chromium] PASSED

======================= 28 passed in 255.94s =======================
```

## Key Learnings

1. **Fetch Response Streams Are Single-Use**: Once consumed, they cannot be re-read
2. **Silent Error Handling Can Hide Bugs**: The Requirement 3.6 (fail silently on malformed responses) masked this architectural issue
3. **One Parse Point Is Best Practice**: Always parse the response body once at the beginning and pass the data through the call chain

## Affected Requirements

- ✅ Requirement 3.4: Error responses with status, timestamp, message, description are now properly parsed
- ✅ Requirement 3.5: Response status field is validated against HTTP status code
- ✅ Requirement 3.6: Malformed errors still fail silently (improved handling)
- ✅ Requirement 7.5: Error details are now displayed to users

## Files Modified

- `frontend/src/api/client.ts` - Fixed API client error handling
- `tests/property/test_error_response_parsing.py` - Removed xfail markers
- `tests/property/test_response_display.py` - Removed xfail markers
