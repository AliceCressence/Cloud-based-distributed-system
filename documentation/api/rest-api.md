# REST API Reference (Summary)

Base URL: `/api/v1`

## Auth
- POST `/auth/login` (form-data: username, password)
- POST `/auth/register`
- GET `/auth/me`

## Files
- POST `/files/upload` multipart(file, course_id?, folder_path)
- GET `/files` (course_id?, folder_path?, skip?, limit?)
- GET `/files/{file_id}`
- GET `/files/{file_id}/download`
- DELETE `/files/{file_id}`
- GET `/files/{file_id}/chunks`

## Nodes (admin)
- POST `/nodes`
- GET `/nodes`
- GET `/nodes/available`
- GET `/nodes/health`
- GET `/nodes/overview`
- GET `/nodes/{node_id}`
- GET `/nodes/{node_id}/health`
- GET `/nodes/{node_id}/statistics`
- DELETE `/nodes/{node_id}`
