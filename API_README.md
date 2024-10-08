# Tee Time API Documentation

## Base URL

`http://your-server-address:8000`

## Interactive Documentation

- Swagger UI: `{Base URL}/docs`
- ReDoc: `{Base URL}/redoc`

## Endpoints

### Get Filtered Tee Times

`GET /api/tee-times/filtered`

Query Parameters:

- `date` (optional): Date in YYYY-MM-DD format
- `course` (optional): Course name (max length 100 characters)
- `min_price` (optional): Minimum price (must be >= 0)
- `max_price` (optional): Maximum price (must be >= 0)
- `page` (optional, default=1): Page number for pagination
- `limit` (optional, default=20, max=100): Number of items per page
- `sort_by` (optional): Field to sort by (e.g., 'datetime', 'price')
- `sort_order` (optional, default='asc'): Sort order ('asc' or 'desc')

Example Request:

`GET /api/tee-times/filtered?date=2023-05-15&course=Mayfair%20Lakes&min_price=50&max_price=100&page=1&limit=20&sort_by=datetime&sort_order=desc`

### Get All Tee Times

`GET /api/tee-times/all`

Query Parameters:

- `page` (optional, default=1): Page number for pagination
- `limit` (optional, default=20, max=100): Number of items per page
- `sort_by` (optional): Field to sort by (e.g., 'datetime', 'price')
- `sort_order` (optional, default='asc'): Sort order ('asc' or 'desc')

### Get All Available Tee Times

`GET /api/tee-times/available`

Query Parameters:

- `page` (optional, default=1): Page number for pagination
- `limit` (optional, default=20, max=100): Number of items per page
- `sort_by` (optional): Field to sort by (e.g., 'datetime', 'price')
- `sort_order` (optional, default='asc'): Sort order ('asc' or 'desc')

### Get Available Courses

`GET /available-courses`

Returns a list of all available golf courses in the system.

Example Response:

```json
["Mayfair Lakes", "Whistling Straits", "Bandon Dunes", "Pinehurst No. 2"]
```

## Response Format

All tee time endpoints return a JSON object with the following structure:

    {
    "teeTimes": [
    {
        "id": 1,
        "course": "Course Name",
        "datetime": "2023-05-15 10:00:00 UTC",
        "timezone": "America/Vancouver",
        "available_booking_sizes": [2, 3, 4],
        "price": 75.00,
        "currency": "CAD",
        "starting_hole": 1
    },
    // ... more tee times
    ],
    "pagination": {
        "currentPage": 1,
        "totalPages": 5,
        "totalItems": 100,
        "itemsPerPage": 20
    }
    }

The `pagination` object provides information for implementing pagination in the frontend:

- `currentPage`: The current page number
- `totalPages`: Total number of pages available
- `totalItems`: Total number of tee times across all pages
- `itemsPerPage`: Number of items per page

To navigate through pages, use the `page` query parameter:

`GET /api/tee-times/all?page=2&limit=20`

## Error Handling

The API uses standard HTTP status codes. In case of an error, the response will include a JSON object with an `error` field describing the issue.

Example:

```json
{
  "error": "min_price cannot be greater than max_price"
}
```
