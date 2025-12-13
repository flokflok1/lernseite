# LernsystemX Category API Documentation

**Version:** 1.0.0
**Standard:** ISO/IEC/IEEE 26515:2018 - API Documentation
**Last Updated:** 2025-11-16

## Overview

The Category API provides a 5-level hierarchical course categorization system. Categories can be nested up to 5 levels deep, providing granular organization for courses.

### Hierarchy Structure

```
Level 1: Main Category (e.g., "IT & Software")
  └─ Level 2: Subcategory (e.g., "Programming")
      └─ Level 3: Sub-subcategory (e.g., "Python")
          └─ Level 4: Specialization (e.g., "Web Development")
              └─ Level 5: Topic (e.g., "Flask Framework")
```

### Base URL

```
http://localhost:5000/api/v1
```

---

## Authentication

- **Public Endpoints:** GET requests (list, tree, search, breadcrumb, stats)
- **Protected Endpoints:** POST, PUT, DELETE (require admin/superadmin role)

### Headers

```http
Authorization: Bearer <JWT_TOKEN>
```

---

## Endpoints

### 1. List All Categories (Flat)

Get a flat list of all categories ordered by level and order_index.

**Endpoint:** `GET /categories`

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| active_only | boolean | No | false | Only return active categories |
| page | integer | No | 1 | Page number |
| per_page | integer | No | 100 | Items per page (max: 500) |

**Example Request:**
```http
GET /api/v1/categories?active_only=true&page=1&per_page=50
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "categories": [
    {
      "category_id": 1,
      "name": "IT & Software",
      "slug": "it-software",
      "description": "Information Technology and Software Development",
      "parent_id": null,
      "level": 1,
      "icon": "fa-laptop-code",
      "color": "#3498db",
      "order_index": 0,
      "is_active": true,
      "course_count": 245,
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-15T10:00:00Z"
    },
    {
      "category_id": 2,
      "name": "Programming",
      "slug": "programming",
      "description": "Learn programming languages and concepts",
      "parent_id": 1,
      "parent_name": "IT & Software",
      "level": 2,
      "icon": "fa-code",
      "color": "#2ecc71",
      "order_index": 0,
      "is_active": true,
      "course_count": 187,
      "created_at": "2025-01-15T10:05:00Z",
      "updated_at": "2025-01-15T10:05:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 150,
    "total_pages": 3
  }
}
```

---

### 2. Get Category Tree (Hierarchical)

Get hierarchical category tree structure with up to 5 levels of nesting.

**Endpoint:** `GET /categories/tree`

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| active_only | boolean | No | false | Only include active categories |

**Example Request:**
```http
GET /api/v1/categories/tree?active_only=true
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "tree": {
    "categories": [
      {
        "category_id": 1,
        "name": "IT & Software",
        "slug": "it-software",
        "level": 1,
        "icon": "fa-laptop-code",
        "color": "#3498db",
        "course_count": 245,
        "has_children": true,
        "total_courses": 245,
        "children": [
          {
            "category_id": 2,
            "name": "Programming",
            "slug": "programming",
            "parent_id": 1,
            "level": 2,
            "icon": "fa-code",
            "color": "#2ecc71",
            "course_count": 187,
            "has_children": true,
            "total_courses": 187,
            "children": [
              {
                "category_id": 5,
                "name": "Python",
                "slug": "python",
                "parent_id": 2,
                "level": 3,
                "icon": "fa-python",
                "color": "#3776ab",
                "course_count": 78,
                "has_children": true,
                "total_courses": 78,
                "children": [
                  {
                    "category_id": 15,
                    "name": "Web Development",
                    "slug": "web-development",
                    "parent_id": 5,
                    "level": 4,
                    "icon": "fa-globe",
                    "color": "#e74c3c",
                    "course_count": 42,
                    "has_children": true,
                    "total_courses": 42,
                    "children": [
                      {
                        "category_id": 42,
                        "name": "Flask Framework",
                        "slug": "flask-framework",
                        "parent_id": 15,
                        "level": 5,
                        "icon": "fa-flask",
                        "color": "#000000",
                        "course_count": 12,
                        "has_children": false,
                        "total_courses": 12,
                        "children": []
                      }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      }
    ],
    "total_categories": 150,
    "max_level": 5,
    "active_categories": 142
  }
}
```

---

### 3. Get Category Details

Get detailed information about a specific category.

**Endpoint:** `GET /categories/:id`

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Category ID |

**Example Request:**
```http
GET /api/v1/categories/5
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "category": {
    "category_id": 5,
    "name": "Python",
    "slug": "python",
    "description": "Learn Python programming from basics to advanced",
    "parent_id": 2,
    "parent_name": "Programming",
    "level": 3,
    "icon": "fa-python",
    "color": "#3776ab",
    "order_index": 2,
    "is_active": true,
    "course_count": 78,
    "created_at": "2025-01-15T11:00:00Z",
    "updated_at": "2025-01-15T11:00:00Z",
    "children": [
      {
        "category_id": 15,
        "name": "Web Development",
        "slug": "web-development",
        "level": 4,
        "course_count": 42
      },
      {
        "category_id": 16,
        "name": "Data Science",
        "slug": "data-science",
        "level": 4,
        "course_count": 36
      }
    ]
  }
}
```

**Error Response (404 Not Found):**
```json
{
  "success": false,
  "error": "Category not found",
  "message": "The requested category does not exist"
}
```

---

### 4. Get Category Breadcrumb

Get the full path from root category to the specified category.

**Endpoint:** `GET /categories/:id/breadcrumb`

**Example Request:**
```http
GET /api/v1/categories/42/breadcrumb
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "breadcrumb": [
    {
      "category_id": 1,
      "name": "IT & Software",
      "slug": "it-software",
      "level": 1
    },
    {
      "category_id": 2,
      "name": "Programming",
      "slug": "programming",
      "level": 2
    },
    {
      "category_id": 5,
      "name": "Python",
      "slug": "python",
      "level": 3
    },
    {
      "category_id": 15,
      "name": "Web Development",
      "slug": "web-development",
      "level": 4
    },
    {
      "category_id": 42,
      "name": "Flask Framework",
      "slug": "flask-framework",
      "level": 5
    }
  ]
}
```

---

### 5. Search Categories

Search categories by name or description.

**Endpoint:** `GET /categories/search`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | Search query (min 2 chars) |
| active_only | boolean | No | Only search active categories |

**Example Request:**
```http
GET /api/v1/categories/search?q=python&active_only=true
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "categories": [
    {
      "category_id": 5,
      "name": "Python",
      "slug": "python",
      "level": 3,
      "parent_name": "Programming",
      "course_count": 78
    },
    {
      "category_id": 23,
      "name": "Python for Data Science",
      "slug": "python-for-data-science",
      "level": 4,
      "parent_name": "Data Science",
      "course_count": 24
    }
  ],
  "total": 2,
  "query": "python"
}
```

---

### 6. Get Category Statistics

Get statistical information about categories.

**Endpoint:** `GET /categories/stats`

**Example Request:**
```http
GET /api/v1/categories/stats
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "stats": {
    "total_categories": 150,
    "active_categories": 142,
    "level_1_count": 10,
    "level_2_count": 45,
    "level_3_count": 60,
    "level_4_count": 30,
    "level_5_count": 5,
    "max_level": 5
  }
}
```

---

### 7. Create Category (Admin Only)

Create a new category.

**Endpoint:** `POST /categories`

**Authentication:** Required (Admin/Superadmin)

**Request Body:**
```json
{
  "name": "Flask Framework",
  "slug": "flask-framework",
  "description": "Learn Flask web framework for Python",
  "parent_id": 15,
  "level": 5,
  "icon": "fa-flask",
  "color": "#000000",
  "order_index": 0,
  "is_active": true
}
```

**Field Descriptions:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Category name (3-255 chars) |
| slug | string | No | URL slug (auto-generated from name) |
| description | string | No | Category description (max 2000 chars) |
| parent_id | integer | No | Parent category ID (null for level 1) |
| level | integer | Yes | Hierarchy level (1-5) |
| icon | string | No | Icon identifier (e.g., "fa-code") |
| color | string | No | Hex color code (e.g., "#3498db") |
| order_index | integer | No | Display order (auto-assigned) |
| is_active | boolean | No | Active status (default: true) |

**Validation Rules:**
- Level 1 categories cannot have a parent_id
- Level 2-5 categories must have a parent_id
- Parent category must exist
- Level must be parent level + 1
- Slug must be unique and contain only lowercase, numbers, hyphens

**Example Response (201 Created):**
```json
{
  "success": true,
  "message": "Category created successfully",
  "category": {
    "category_id": 43,
    "name": "Flask Framework",
    "slug": "flask-framework",
    "parent_id": 15,
    "level": 5,
    "created_at": "2025-01-16T14:30:00Z"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Validation error",
  "details": [
    {
      "type": "value_error",
      "loc": ["level"],
      "msg": "Level 5 categories must have a parent_id",
      "input": null
    }
  ]
}
```

---

### 8. Update Category (Admin Only)

Update an existing category.

**Endpoint:** `PUT /categories/:id`

**Authentication:** Required (Admin/Superadmin)

**Note:** Cannot update `level` or `parent_id` to prevent breaking hierarchy.

**Request Body:**
```json
{
  "name": "Advanced Flask",
  "description": "Updated description",
  "icon": "fa-flask",
  "color": "#34495e",
  "is_active": true
}
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "message": "Category updated successfully",
  "category": {
    "category_id": 43,
    "name": "Advanced Flask",
    "updated_at": "2025-01-16T15:00:00Z"
  }
}
```

---

### 9. Delete Category (Admin Only)

Delete a category.

**Endpoint:** `DELETE /categories/:id`

**Authentication:** Required (Admin/Superadmin)

**WARNING:** Will fail if category has:
- Child categories
- Associated courses

Use deactivate instead for categories in use.

**Example Response (200 OK):**
```json
{
  "success": true,
  "message": "Category deleted successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Cannot delete category",
  "message": "Cannot delete category with subcategories. Delete children first."
}
```

---

### 10. Reorder Categories (Admin Only)

Update the display order of multiple categories.

**Endpoint:** `POST /categories/reorder`

**Authentication:** Required (Admin/Superadmin)

**Request Body:**
```json
{
  "category_orders": [
    {"category_id": 5, "order_index": 0},
    {"category_id": 3, "order_index": 1},
    {"category_id": 8, "order_index": 2}
  ]
}
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "message": "Categories reordered successfully"
}
```

---

### 11. Activate Category (Admin Only)

Activate a deactivated category.

**Endpoint:** `POST /categories/:id/activate`

**Authentication:** Required (Admin/Superadmin)

**Example Response (200 OK):**
```json
{
  "success": true,
  "message": "Category activated successfully",
  "category": {
    "category_id": 15,
    "is_active": true
  }
}
```

---

### 12. Deactivate Category (Admin Only)

Soft delete - deactivate a category without removing it.

**Endpoint:** `POST /categories/:id/deactivate`

**Authentication:** Required (Admin/Superadmin)

**Example Response (200 OK):**
```json
{
  "success": true,
  "message": "Category deactivated successfully",
  "category": {
    "category_id": 15,
    "is_active": false
  }
}
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Example Use Cases

### 1. Building a Category Dropdown

```javascript
// Fetch tree structure
const response = await fetch('/api/v1/categories/tree?active_only=true');
const { tree } = await response.json();

// Render hierarchical dropdown
function renderCategoryOptions(categories, level = 0) {
  return categories.map(cat => `
    <option value="${cat.category_id}">
      ${'—'.repeat(level)} ${cat.name} (${cat.course_count})
    </option>
    ${cat.children.length > 0 ? renderCategoryOptions(cat.children, level + 1) : ''}
  `).join('');
}
```

### 2. Displaying Breadcrumb Navigation

```javascript
// Fetch breadcrumb
const response = await fetch('/api/v1/categories/42/breadcrumb');
const { breadcrumb } = await response.json();

// Render breadcrumb
const breadcrumbHTML = breadcrumb
  .map(cat => `<a href="/category/${cat.slug}">${cat.name}</a>`)
  .join(' / ');
```

### 3. Category Search Autocomplete

```javascript
// Search as user types
const searchCategories = async (query) => {
  if (query.length < 2) return [];

  const response = await fetch(`/api/v1/categories/search?q=${query}`);
  const { categories } = await response.json();

  return categories;
};
```

---

## Compliance

This API documentation complies with:
- **ISO/IEC/IEEE 26515:2018** - Developing user documentation
- **ISO 9001:2015** - Quality management systems
- **RESTful API Design** best practices

---

## Support

For API support or questions:
- Documentation: https://lernsystemx.de/docs
- Email: api-support@lernsystemx.de
- GitHub Issues: https://github.com/lernsystemx/backend/issues

---

**Document Version:** 1.0.0
**Last Updated:** 2025-11-16
**Maintained by:** LernsystemX Development Team
